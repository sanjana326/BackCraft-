from flask import Flask, request, jsonify, render_template, url_for
import os
from rembg import remove
from PIL import Image, ImageFilter

app = Flask(__name__)

# Define upload and output directories
UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "static/outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff", "webp"}  # ✅ Supports multiple formats

# Function to check allowed file types
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ Home Page Route
@app.route("/")
def home():
    return render_template("index.html")

# ✅ Upload Pages for Remove & Blur Background
@app.route("/upload_remove_bg", methods=["GET"])
def upload_remove_bg():
    return render_template("upload_remove_bg.html")

@app.route("/upload_blur_bg", methods=["GET"])
def upload_blur_bg():
    return render_template("upload_blur_bg.html")

# ✅ Remove Background Route
@app.route("/remove_bg", methods=["POST"])
def remove_bg():
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return "Invalid file format", 400

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_path = os.path.join(OUTPUT_FOLDER, f"processed_{file.filename}")

    file.save(input_path)

    try:
        # Open the image and remove background
        input_image = Image.open(input_path).convert("RGBA")
        output_image = remove(input_image)
        output_image.save(output_path, "PNG")

        return render_template(
            "result.html",
            original_image=url_for("static", filename=f"uploads/{file.filename}"),
            processed_image=url_for("static", filename=f"outputs/processed_{file.filename}"),
        )
    except Exception as e:
        return f"Error: {str(e)}", 500


# ✅ Blur Background Route

@app.route("/blur_bg", methods=["POST"])
def blur_bg():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file format"}), 400

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_path = os.path.join(OUTPUT_FOLDER, f"blurred_{file.filename}")

    file.save(input_path)

    try:
        # Open the image
        image = Image.open(input_path).convert("RGBA")

        # Remove the background
        foreground = remove(image)

        # Create a blurred background
        blurred_bg = image.filter(ImageFilter.GaussianBlur(15))  # Adjust blur intensity

        # Merge foreground with blurred background
        final_image = Image.new("RGBA", image.size)
        final_image.paste(blurred_bg, (0, 0))
        final_image.paste(foreground, (0, 0), foreground)

        # Save the final image
        final_image.save(output_path, "PNG")

        return render_template(
            "result.html",
            original_image=url_for("static", filename=f"uploads/{file.filename}"),
            processed_image=url_for("static", filename=f"outputs/blurred_{file.filename}"),
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/replace_bg", methods=["POST"])
def replace_bg():
    if "file" not in request.files or "background" not in request.files:
        return jsonify({"error": "Both image and background are required"}), 400

    file = request.files["file"]
    background_file = request.files["background"]

    if file.filename == "" or background_file.filename == "" or not allowed_file(file.filename) or not allowed_file(background_file.filename):
        return jsonify({"error": "Invalid file format"}), 400

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    bg_path = os.path.join(UPLOAD_FOLDER, background_file.filename)
    output_path = os.path.join(OUTPUT_FOLDER, f"replaced_{file.filename}")

    file.save(input_path)
    background_file.save(bg_path)

    try:
        # Open images
        input_image = Image.open(input_path).convert("RGBA")
        background = Image.open(bg_path).convert("RGBA")

        # Remove background from input image
        foreground = remove(input_image)

        # Resize background to match input image
        background = background.resize(input_image.size)

        # Merge images
        final_image = Image.new("RGBA", input_image.size)
        final_image.paste(background, (0, 0))
        final_image.paste(foreground, (0, 0), foreground)

        # Save final image
        final_image.save(output_path, "PNG")

        return render_template(
            "result.html",
            original_image=url_for("static", filename=f"uploads/{file.filename}"),
            processed_image=url_for("static", filename=f"outputs/replaced_{file.filename}"),
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/upload_replace_bg", methods=["GET"])
def upload_replace_bg():
    return render_template("upload_replace_bg.html")
@app.route('/crop_resize')
def crop_resize():
    return render_template('crop_resize.html')
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/features")
def features():
    return render_template("features.html")
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        print(f"New message from {name} ({email}): {message}")
        return "Thank you for your message!"
    
    return render_template("contact.html")

    


# ✅ Run Flask App
if __name__ == "__main__":
    app.run(debug=True)

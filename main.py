from flask import Flask, render_template, request, flash, redirect
from werkzeug.utils import secure_filename
import cv2
import os
import img2pdf
from pdf2image import convert_from_path
from docx import Document

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif', 'pdf', 'docx'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(filename, operation):
    img_path = f"uploads/{filename}"
    new_filename = f"static/{filename.split('.')[0]}"
    
    match operation:
        case "cgray":
            img = cv2.imread(img_path)
            img_processed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            new_filename += ".png"
            cv2.imwrite(new_filename, img_processed)
        case "cwebp":
            img = cv2.imread(img_path)
            new_filename += ".webp"
            cv2.imwrite(new_filename, img)
        case "cjpg":
            img = cv2.imread(img_path)
            new_filename += ".jpg"
            cv2.imwrite(new_filename, img)
        case "cpng":
            img = cv2.imread(img_path)
            new_filename += ".png"
            cv2.imwrite(new_filename, img)
        case "to_pdf":
            with open(new_filename + ".pdf", "wb") as f:
                f.write(img2pdf.convert(img_path))
            new_filename += ".pdf"
        case "pdf_to_jpg":
            images = convert_from_path(img_path)
            new_filename += ".jpg"
            for img in images:
                img.save(new_filename, 'JPEG')
        case "pdf_to_png":
            images = convert_from_path(img_path)
            new_filename += ".png"
            for img in images:
                img.save(new_filename, 'PNG')
        case "docx_to_pdf":
            doc = Document(img_path)
            doc.save(new_filename + ".pdf")
            new_filename += ".pdf"
    return new_filename

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/how")
def how():
    return render_template("how.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            operation = request.form.get("operation")
            new_file_path = process_image(filename, operation)
            flash(f'File successfully processed. Download it <a href="/{new_file_path}" download>here</a>.')
            return redirect("/")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)

import os
import time
from flask import Flask, render_template, request, jsonify
import pyttsx3
from PyPDF2 import PdfReader

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads/"
app.config["AUDIO_FOLDER"] = "static/audio/"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["AUDIO_FOLDER"], exist_ok=True)

def clear_old_audio():
    try:
        for filename in os.listdir(app.config["AUDIO_FOLDER"]):
            file_path = os.path.join(app.config["AUDIO_FOLDER"], filename)
            os.remove(file_path)
    except Exception as e:
        pass

def clear_old_PDF():
    try:
        for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
            if filename.endswith(".pdf"):
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                os.remove(file_path)
    except Exception as e:
        pass

def process_pdf(pdf_path, audio_folder="static/audio"):
    clear_old_audio()
    

    reader = PdfReader(open(pdf_path, 'rb'))
    voice = pyttsx3.init()

    clean_text = ""
    for page in range(len(reader.pages)):
        text = reader.pages[page].extract_text()
        clean_text += text.strip().replace('\n', ' ')

    audio_file_name = f"PDFaudio.mp3"
    audio_file_path = os.path.join(audio_folder, audio_file_name)
    
    os.makedirs(audio_folder, exist_ok=True)
    
    voice.save_to_file(clean_text, audio_file_path)
    voice.runAndWait()

    return audio_file_name

@app.route("/")
def home():
    if request.method == "GET":
        clear_old_PDF()
        clear_old_audio()
    return render_template("index.html", audio_file=None)

@app.route("/process-pdf", methods=["POST"])
def process_pdf_upload():
    try:
        file = request.files.get("pdfFile")
        if not file or file.filename == "":
            return render_template("index.html", audio_file=None, message="No selected file")
        
        if not file.filename.endswith(".pdf"):
            return render_template("index.html", audio_file=None, message="Invalid file type. Please upload a PDF")
        
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)
        clear_old_audio()
        
        try:
            audio_file_name = process_pdf(file_path, audio_folder=app.config["AUDIO_FOLDER"])
            audio_file_url = f"/static/audio/{audio_file_name}?{time.time()}"
            return render_template("index.html", audio_file=audio_file_url, message="File processed successfully")
        except Exception as e:
            return render_template("index.html", audio_file=None, message=f"Error processing PDF: {e}")
    except Exception as e:
        return render_template("index.html", audio_file=None, message=f"Unexpected error: {e}")
if __name__ == "__main__":
    app.run(debug=True)

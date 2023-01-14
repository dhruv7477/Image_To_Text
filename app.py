import base64
import io
import uuid
from flask import Flask,request,app,render_template,send_from_directory,make_response
from flask_cors import CORS,cross_origin
import pytesseract
from PIL import Image
import pandas as pd
from werkzeug.utils import secure_filename
import os
from docx import Document
from fpdf import FPDF
from logger import logging
import sqlite3


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}


app=Flask(__name__)
@app.route('/',methods=['GET'])
@cross_origin()
def home():
    '''This function will render index.html'''
    return render_template('index.html')


def allowed_file(filename):
    '''This function will verify if the input file is a valid image or not!'''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/image',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    '''This function will take image as an input and return the text on it by extracting it.'''
    if request.method == 'POST':
        try:
            # Get the file from the form
            image = request.files["image"]
            logging.info(f"The image name entered was {image}")
            filename = secure_filename(image.filename)
            if not allowed_file(filename):
                return 'Invalid file type. Please upload a jpg, jpeg or png file.'
            
            # Save the file to the server
            UPLOAD_FOLDER = 'uploads'
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Convert the image to a file-like object
            image.seek(0)
            image_file = io.BytesIO(image.read())
            # Open the image file
            image = Image.open(image_file)
            # read image data
            image_data = image_file.getvalue()

            
            # Extract the text from the image
            text = pytesseract.image_to_string(image)
            logging.info(f"The text in the file was {text}")
            with open(f'uploads/{filename}.txt', 'w') as f:
                f.write(text)
                f.close()

            # Connect to the SQLite database
            conn = sqlite3.connect('test.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
            if cursor.fetchone() is None:
                cursor.execute('''CREATE TABLE images (image_id text PRIMARY KEY, image_data blob)''')
            image_id = str(uuid.uuid4())
            image_data = base64.b64encode(image_data).decode()
            cursor.execute("INSERT INTO images (image_id, image_data) VALUES (?, ?)", (image_id, image_data))
            conn.commit()
            conn.close()


            return render_template('result.html', text = text, filename = filename)
        except Exception as e:
            logging.exception(f'The Exception message caused by the index function is: {e}')
            return 'Something is wrong. Check the log files!'
    else:
        return render_template('index.html')


@app.route('/download_txt/<filename>')
def download_txt(filename):
    '''This function will allow the user to save the extracted text in txt format.'''
    try:
        with open(f'uploads/{filename}.txt', 'r') as f:
            text = f.read()
        response = make_response(text)
        response.headers["Content-Disposition"] = "attachment; filename=file.txt"
        response.headers["Content-type"] = "text/plain"
        logging.info("The user downloaded the extracted text in txt format")
        return response
        
    except Exception as e:
        logging.exception(f'The Exception message caused by the download_txt function is: {e}')
        return 'Something is wrong. Check the log files!'


@app.route('/download_word/<filename>')
def download_word(filename):
    '''This function will allow the user to save the extracted text in word format.'''
    try:
        # Open the text file
        with open(f'uploads/{filename}.txt', 'r') as f:
            text = f.read()
            f.close()

        # Create a new Word document
        document = Document()
        document.add_paragraph(text)
        
        # Save the document in memory
        file = io.BytesIO()
        document.save(f'uploads/{filename}.docx')
        file.seek(0)
        
        # Return the Word document as a downloadable file
        response = make_response(send_from_directory(app.config['UPLOAD_FOLDER'], f'{filename}.docx', as_attachment=True))
        response.headers["Content-Disposition"] = f"attachment; filename={filename}.docx"
        logging.info("The user downloaded the extracted text in word format")
        return response

    except Exception as e:
        logging.exception(f'The Exception message caused by the download_word function is: {e}')
        return 'Something is wrong. Check the log files!'

@app.route('/download_pdf/<filename>')
def download_pdf(filename):
    '''This function will allow the user to save the extracted text in pdf format.'''
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        with open(f'uploads/{filename}.txt', 'r') as f:
            text = f.read()
            pdf.cell(200, 10, txt=text, ln=1, align="C")
            pdf.output(f'uploads/{filename}.pdf')
        response = make_response(send_from_directory(app.config['UPLOAD_FOLDER'], f'{filename}.pdf', as_attachment=True))
        response.headers["Content-Disposition"] = f"attachment; filename={filename}.pdf"
        logging.info("The user downloaded the extracted text in pdf format")
        return response

    except Exception as e:
        logging.exception(f'The Exception message caused by the download_pdf function is: {e}')
        return 'Something is wrong. Check the log files!'

if __name__ == "__main__":
    app.run(debug=True)
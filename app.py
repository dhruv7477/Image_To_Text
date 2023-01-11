import io
from flask import Flask,request,app,render_template,send_from_directory,make_response
from flask_cors import CORS,cross_origin
import pytesseract
from PIL import Image
import pandas as pd
from werkzeug.utils import secure_filename
import os
from docx import Document
from fpdf import FPDF

app=Flask(__name__)
@app.route('/',methods=['GET'])
@cross_origin()
def home():
    '''This function will render index.html'''
    return render_template('index.html')

@app.route('/image',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    '''This function will take image as an input and return the text on it by extracting it.'''
    if request.method == 'POST':
        try:
            # Get the file from the form
            image = request.files["image"]
            # Save the file to the server
            filename = secure_filename(image.filename)
            UPLOAD_FOLDER = 'uploads'
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            image.save("uploads/" + filename)
            # Open the image file
            image = Image.open("uploads/" + filename)
            # Extract the text from the image
            text = pytesseract.image_to_string(image)
            with open(f'uploads/{filename}.txt', 'w') as f:
                f.write(text)
                f.close()
            
            return render_template('result.html', text = text, filename = filename)
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
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
        return response
    except Exception as e:
        return str(e)


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
        return response

    except Exception as e:
        return str(e)


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
        return response
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run(debug=True)
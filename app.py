from flask import Flask,request,app,jsonify,url_for,render_template
from flask_cors import CORS,cross_origin
import pytesseract
from PIL import Image
import pandas as pd
from werkzeug.utils import secure_filename
import os



app=Flask(__name__)
@app.route('/',methods=['GET'])
@cross_origin()
def home():
    return render_template('index.html')

@app.route('/image',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
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
            
            return render_template('result.html', text = text)
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    else:
        return render_template('index.html')



if __name__ == "__main__":
    app.run(debug=True)
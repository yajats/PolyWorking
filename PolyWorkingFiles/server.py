from flask import Flask, url_for, redirect, render_template, request
import os, pytesseract
from flask_uploads import UploadSet, configure_uploads, IMAGES
from PIL import Image
import json
from urllib.request import urlopen
import urllib.request
#import string
#from io import BytesIO
#import requests
#from io import BytesIO
pytesseract.pytesseract.tesseract_cmd = 'C:\\Camera_Flask_App-main\\Tesseract\\tesseract.exe'

# Path for current location
project_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            static_url_path = '',
            static_folder = 'static',
            template_folder = 'templates')

photos = UploadSet('photos', IMAGES)

app.config['DEBUG'] = False
app.config['UPLOAD_FOLDER'] = 'images'

# Class for Image to Text
class GetText(object):
    
    def __init__(self, file):
        self.file = pytesseract.image_to_string(Image.open(project_dir + '/images/' + file))


# Home page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Check if the form is empty
        if 'photo' not in request.files:
            return 'there is no photo in form'
           
        photo = request.files['photo']
        path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
        # Save the photo in the upload folder
        photo.save(path)
        
        # Class instance 
        textObject = GetText(photo.filename)
        result = textObject.file
        
        return redirect(url_for('result', result=result))
    return render_template('index.html')

# Result page


@app.route('/result', methods=['GET', 'POST'])
def result():
    def removelines(value):
        return value.replace('\n', '')
    def removespaces(value):
        return value.replace(' ', '+')
    result = request.args.get('result', None)
    intitle = removespaces(removelines(result))

    api = "https://www.googleapis.com/books/v1/volumes?q=intitle:\""
    resp = urlopen(api + intitle)
    book_data = json.load(resp)
    volume_info = book_data["items"][0]["volumeInfo"]
    author = volume_info["authors"]
    prettify_author = author if len(author) > 1 else author[0]
    urllib.request.urlretrieve(volume_info['imageLinks']['thumbnail'], "gfg.png")

    api2 = "https://www.googleapis.com/customsearch/v1/"
    key = "AIzaSyCNaeD-vDa_2bA5y56oN05j_si21-MBFWU"

    img = Image.open("gfg.png")
    img.show()
    return f"Title: {volume_info['title']}<br/>" \
           f"Author: {prettify_author}<br/>" \
           f"Page Count: {volume_info['pageCount']}<br/>" \
           f"Publication Date: {volume_info['publishedDate']}<br/>" \
           f"Publisher: {volume_info['publisher']}<br/>" \
           f"Description: {volume_info['description']}<br/>" \
           f"Ebook: {volume_info['infoLink']}<br/>" \


if __name__ == '__main__':
    app.run()
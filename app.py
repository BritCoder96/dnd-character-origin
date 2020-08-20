from distutils.core import setup
import os,cv2,pytesseract
from flask import Flask, render_template, request,jsonify
from PIL import Image
import sys 
from pdf2image import convert_from_path 

pytesseract.pytesseract.tesseract_cmd = 'tesseract'

app = Flask(__name__)

UPLOAD_FOLDER = os.path.basename('.')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/ocr', methods=['POST','GET'])
def upload_file():
    if request.method == "GET":
        return "This is the api BLah blah"
    elif request.method == "POST":
        file = request.files['image']

        f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        filename, file_extension = os.path.splitext(file.filename)
        # add your custom code to check that the uploaded file is a valid image and not a malicious file (out-of-scope for this post)
        file.save(f)
        # print(file.filename)
        text = ''
        if file_extension == '.pdf':
            pages = convert_from_path(file.filename, 500) 
              
            # Counter to store images of each page of PDF to image 
            image_counter = 1
              
            # Iterate through all the pages stored above 
            for page in pages: 
              
                # Declaring filename for each page of PDF as JPG 
                # For each page, filename will be: 
                # PDF page 1 -> page_1.jpg 
                # PDF page 2 -> page_2.jpg 
                # PDF page 3 -> page_3.jpg 
                # .... 
                # PDF page n -> page_n.jpg 
                filename = "page_"+str(image_counter)+".jpg"
                  
                # Save the image of the page in system 
                page.save(filename, 'JPEG') 
              
                # Increment the counter to update filename 
                image_counter = image_counter + 1
              
            # Variable to get count of total number of pages 
            filelimit = image_counter-1
              
            # Iterate from 1 to total number of pages 
            for i in range(1, filelimit + 1): 
              
                # Set filename to recognize text from 
                # Again, these files will be: 
                # page_1.jpg 
                # page_2.jpg 
                # .... 
                # page_n.jpg 
                filename = "page_"+str(i)+".jpg"
                      
                # Recognize the text as string in image using pytesserct 
                text = str(((pytesseract.image_to_string(Image.open(filename))))) 
              
                # The recognized text is stored in variable text 
                # Any string processing may be applied on text 
                # Here, basic formatting has been done: 
                # In many PDFs, at line ending, if a word can't 
                # be written fully, a 'hyphen' is added. 
                # The rest of the word is written in the next line 
                # Eg: This is a sample text this word here GeeksF- 
                # orGeeks is half on first line, remaining on next. 
                # To remove this, we replace every '-\n' to ''. 
                text = text.replace('-\n', '')
        else:
            image = cv2.imread(UPLOAD_FOLDER+"/"+file.filename)
            os.remove(UPLOAD_FOLDER+"/"+file.filename)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # check to see if we should apply thresholding to preprocess the
            # image
            preprocess = request.form.get('preprocess', 'Thresh')
            if  preprocess == "thresh":
                gray = cv2.threshold(gray, 0, 255,
                                     cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

            # make a check to see if median blurring should be done to remove
            # noise

            elif preprocess == "blur":
                gray = cv2.medianBlur(gray, 3)
            # write the grayscale image to disk as a temporary file so we can
            # apply OCR to it
            filename = "{}.png".format(os.getpid())
            cv2.imwrite(filename, gray)
            # load the image as a PIL/Pillow image, apply OCR, and then delete
            # the temporary file
            # print("C:/Users/mzm/PycharmProjects/My_website/ocr_using_video/"+filename,Image.open("C:\\Users\mzm\PycharmProjects\My_website\ocr_using_video\\"+filename))
            text = pytesseract.image_to_string(Image.open(filename))
        os.remove(filename)
        print("Text in Image :\n",text)

        return jsonify({"text" : text})

app.run("0.0.0.0",5000,threaded=True,debug=True)



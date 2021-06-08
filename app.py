from distutils.core import setup
import os, sys, cv2, tempfile, pytesseract, tika, re, requests, urllib.parse,uuid
from flask import Flask, render_template, request,jsonify
from PIL import Image
from pdf2image import convert_from_path 
from tika import parser
import constants
# Credentials are stored on the local environment for security.
import credentials

tika.initVM()

pytesseract.pytesseract.tesseract_cmd = 'tesseract'

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(tempfile.gettempdir())
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def full_file_path(filename, hex):
    return os.path.join(app.config['UPLOAD_FOLDER'], hex + filename)

def get_traits(text, reverse):
    traits = []
    regex = re.compile('[^a-zA-Z\n -]')
    text = regex.sub('', text)
    split_text = text.lower().split()
    if reverse:
        split_text.reverse()
    for trait_category in (constants.TRAITS):
        split_traits = set(trait_category['traits'])
        words = list(split_traits & set(split_text))
        if len(words) > 0 and trait_category["type"] == 'races':
            if trait_category["type"] == 'races':
                min_trait_index = sys.maxsize
                min_trait = []
                for trait in words:
                    index = split_text.index(trait)
                    if index < min_trait_index:
                        min_trait_index = index
                        min_trait = trait
                words = [min_trait]
        traits += words
    return traits

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process_character_sheet', methods=['POST'])
def upload_file():
    file = request.files['image']
    hex = uuid.uuid4().hex
    f = full_file_path(file.filename, hex)
    filename, file_extension = os.path.splitext(file.filename)
    file.save(f)
    text = ''
    traits = []
    if file_extension == '.pdf':
        parsed = parser.from_file(f)
        text = parsed['content']
        traits = get_traits(text, True)
        if not (len(text) > 0 and len(traits) > 0):
            text = ''
            pages = convert_from_path(f, 500)

            # Counter to store images of each page of PDF to image
            image_counter = 1

            # Iterate through all the pages stored above
            for page in pages:
                # Declaring filename for each page of PDF as JPG
                # For each page, filename will be
                # PDF page 1 -> page_1.jpg
                # PDF page 2 -> page_2.jpg
                # PDF page 3 -> page_3.jpg
                # ....
                # PDF page n -> page_n.jpg
                split_filename = full_file_path("page_" + str(image_counter) + ".jpg", hex)
                # Save the image of the page in system
                page.save(split_filename, 'JPEG')

                # Increment the counter to update filename
                image_counter = image_counter + 1

            # Variable to get count of total number of pages
            filelimit = image_counter - 1

            # Iterate from 1 to total number of pages
            for i in range(1, filelimit + 1):
                # Set filename to recognize text from
                # Again, these files will be:
                # page_1.jpg
                # page_2.jpg
                #
                # page_n.jpg
                split_filename = full_file_path("page_" + str(i) + ".jpg", hex)

                # Recognize the text as string in image using pytesserct
                text += str(((pytesseract.image_to_string(Image.open(split_filename)))))
                # The recognized text is stored in variable text
                # Any string processing may be applied on text
                # Here, basic formatting has been done:
                # In many PDFs, at line ending, if a word can't
                # be written fully, a 'hyphen' is added
                # The rest of the word is written in the next line
                text = text.replace('-\n', '')
                if os.path.exists(split_filename):
                    os.remove(split_filename)

    else:
        image = cv2.imread(f)
        os.remove(f)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # check to see if we should apply thresholding to preprocess the
        # image
        preprocess = request.form.get('preprocess', 'Blur')
        if  preprocess == "thresh":
            gray = cv2.threshold(gray, 0, 255,
                                 cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # make a check to see if median blurring should be done to remove noise

        elif preprocess == "blur":
            gray = cv2.medianBlur(gray, 3)
        # write the grayscale image to disk as a temporary file so we can
        # apply OCR to it
        filename = full_file_path("{}.png".format(os.getpid()), '')
        cv2.imwrite(filename, gray)
        # load the image as a PIL/Pillow image, apply OCR, and then delete
        # the temporary file
        text = pytesseract.image_to_string(Image.open(filename))
    if os.path.exists(f):
        os.remove(f)
    if len(traits) == 0:
        traits = get_traits(text, False)
    exclude_terms = ['mini', 'sheet', 'stats', 'DnD-Next-Monster', 'group', 'party']
    if 'male' in traits:
        exclude_terms.append('female')

    print("Traits in Image :\n", (', ').join(traits))
    query = urllib.parse.quote("dnd character image " + (' ').join(traits) + ' -'+ (' -').join(exclude_terms))
    response = requests.get("https://www.googleapis.com/customsearch/v1/siterestrict?key=" + credentials.GOOGLE_API_KEY + "&cx=" + credentials.GOOGLE_CX + "&q=" + query + "&searchType=image&safe=off&num=10&filter=1&excludeTerms=" + ('|').join(exclude_terms)).json()
    print("search results:", response)
    response = list(map(lambda image: image["link"], response["items"]))

    return {"text": response, "traits": traits}

app.run("0.0.0.0",5000,threaded=True,debug=True)



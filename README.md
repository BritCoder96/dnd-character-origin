# dnd-character-origin
D&amp;D character image creator/sharer, generated from just your character sheet!


To run, cd into the project directory, turn on the virtual environment via venv, run python3 app.py in a terminal and go to http://0.0.0.0:5000/. You'll have to install a bunch of stuff (most of these via pip3) including:
python3-venv, python3, flask, pytesseract, opencv-python, tesseract itself (via brew install tesseract on mac and sudo apt install tesseract on linux), tika, and pdf2image. You may need to install poppler, especially on Mac (brew install poppler). Follow the errors when trying to run the server. Of note, it looks like pip3 broke a few days ago but was fixed: https://stackoverflow.com/questions/63410588/cant-install-opencv-python3-8 if you get this error upgrade pip3: sudo -H pip3 install --upgrade pip

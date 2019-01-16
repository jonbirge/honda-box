import os
from random import randint
from flask import Flask, flash, request, redirect, url_for
from flask import send_from_directory, render_template, session
from flask_autoindex import AutoIndex
from werkzeug.utils import secure_filename
from PIL import Image

UPLOAD_BASE = '/app/files/'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg', 'gif'])
SECRET_KEY = 'viadelamesatemeculaca'
PIN_DIGITS = 10
RES_LIST = {
    "720p": (1280, 720),
    "WGA": (800, 480)
}
HONDA_LIST = {
    "Civic": "WGA",
    "Clarity": "WGA",
    "2018-later Accord": "720p",
    "Pre-2018 Accord": "WGA",
    "2019 Pilot": "720p",
    "Pre-2019 Pilot": "WGA"
}
DEFAULT_RES = "WGA"

app = Flask(__name__)
files_index = AutoIndex(app, os.path.curdir + '/files', add_url_rules=False)
app.config['UPLOAD_BASE'] = UPLOAD_BASE
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
app.secret_key = SECRET_KEY

@app.route('/')
def index():
    return 'Main page coming soon!'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def random_pin():
    return str(randint(10**(PIN_DIGITS - 1), 10**PIN_DIGITS - 1))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST': # POST method handler
        ### check for errors...
        car = request.form['model']
        session['car'] = car
        problems = 0
        if 'file' not in request.files:
            flash('No file selected')
            problems += 1
        else:
            file = request.files['file']
            if not allowed_file(file.filename):
                flash('Bad file type')
                problems += 1
        userpin = request.form['pin']
        if len(userpin) < 6:
            flash('PIN is too short')
            problems += 1
        else:
            session['pin'] = userpin
        if problems > 0:
            return redirect(request.url)

        ### handle request
        filename = secure_filename(file.filename)
        fullpath = os.path.join(app.config['UPLOAD_BASE'], userpin)
        try:
            os.mkdir(fullpath)
        except:
            pass  # we don't care!
        ### process file
        tmpfile = os.path.join('/tmp/', filename)
        finalfile = os.path.join(fullpath, filename)
        file.save(tmpfile)  # tmp file
        origimage = Image.open(tmpfile)
        width, height = RES_LIST[HONDA_LIST[car]]
        croppedimage = origimage.crop((0, 0, width, height))
        croppedimage.save(finalfile, 'JPEG')
        return render_template('success.html', pin=userpin, filename=filename, car=car)
    else: # GET method handler
        if not 'pin' in session:
            session['pin'] = random_pin()
        if not 'car' in session:
            session['car'] = next(iter(HONDA_LIST.keys()))
        carlist = list(HONDA_LIST.keys())
        sessioncar = session['car']
        return render_template('upload.html', cars=carlist, thecar=sessioncar)

@app.route('/files')
@app.route('/files/')
def default_files():
    if 'pin' in session:
        return redirect('/files/' + session['pin'])
    else:
        return 'No files uploaded in this session.'

@app.route('/files/<path:path>')
def autoindex(path='.'):
    return files_index.render_autoindex(path)

if __name__ == "__main__":
    app.run("0.0.0.0", port = 80, debug = True)

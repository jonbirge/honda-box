import os
from random import randint
from flask import Flask, flash, request, redirect, url_for
from flask import send_from_directory, render_template, session
from flask_autoindex import AutoIndex
from werkzeug.utils import secure_filename

UPLOAD_BASE = '/app/files/'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg', 'gif'])
SECRET_KEY = 'viadelamesatemeculaca'
PIN_DIGITS = 10

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
    if request.method == 'POST':
        # check for errors...
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
        # handle request
        filename = secure_filename(file.filename)
        # TODO fullpath = 'example.com/files' + userpin + '/' + filename
        fullpath = os.path.join(app.config['UPLOAD_BASE'], userpin)
        try:
            os.mkdir(fullpath)
        except:
            pass  # we don't care!
        file.save(os.path.join(fullpath, filename))
        return render_template('success.html', pin=userpin, filename=filename)
    else: # if GET
        if not 'pin' in session:
            session['pin'] = random_pin() # TODO make random hash
        return render_template('upload.html')

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

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run("0.0.0.0", port = 80, debug = True)

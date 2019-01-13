import os
import os.path
from flask import Flask, flash, request, redirect, url_for
from flask import send_from_directory, render_template, session
from flask_autoindex import AutoIndex
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/app/uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg', 'gif'])
SECRET_KEY = 'viadelamesatemecula'

app = Flask(__name__)
files_index = AutoIndex(app, os.path.curdir + '/files', add_url_rules=False)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
app.secret_key = SECRET_KEY

@app.route('/')
def index():
    return 'Main page coming soon...'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
                flash('Bad file name!')
                problems += 1
        userpin = request.form['pin']
        if len(userpin) < 6:
            flash('PIN is too short!')
            problems += 1
        else:
            session['pin'] = userpin
        if problems > 0:
            return redirect(request.url)
        # handle request
        filename = secure_filename(file.filename)
        # TODO fullpath = 'example.com/files' + userpin + '/' + filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('success.html', pin=userpin, filename=filename)
    else: # if GET
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

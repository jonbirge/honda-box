import os
from flask import Flask, flash, request, redirect, url_for
from flask import send_from_directory, render_template, session
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/app/uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg', 'gif'])
SECRET_KEY = 'viadelamesa'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.secret_key = SECRET_KEY

@app.route('/')
def index():
    return 'Coming soon...'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_ack(request):
    return ('<h3>Successfully uploaded %s under PIN: %s<h3>'
        % (request.files['file'].filename, request.form['pin']))

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
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return upload_ack(request)
    return render_template('upload.html')

@app.route('/uploads/<pin>')
def show_files(pin):
    return 'Someday this will list files for user $s...' % pin

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run("0.0.0.0", port = 80, debug = True)

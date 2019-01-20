import os
from random import randint
from flask import Flask, flash, request, redirect
from flask import send_from_directory, render_template, session
from flask_autoindex import AutoIndex
from werkzeug.utils import secure_filename
from PIL import Image
import redis
from autoscale import auto_scale

UPLOAD_BASE = '/data/boxes/'
CONTENT_LENGTH = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg', 'gif'])
SECRET_KEY = 'viadelamesatemeculaca'
PIN_DIGITS = 10
HONDA_RES = {
    "Civic": "WGA",
    "Clarity": "WGA",
    "2018-later Accord": "720p",
    "Pre-2018 Accord": "WGA",
    "2019 Pilot": "720p",
    "Pre-2019 Pilot": "WGA"
}

# app configuration
app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)
app.config['UPLOAD_BASE'] = UPLOAD_BASE
app.config['MAX_CONTENT_LENGTH'] = CONTENT_LENGTH
app.secret_key = SECRET_KEY
files_index = AutoIndex(app, '/data', add_url_rules=False)

@app.route('/')
def index():
    cache.incr('main_gets')
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def random_pin():
    return str(randint(10**(PIN_DIGITS - 1), 10**PIN_DIGITS - 1))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST': # POST method handler
        cache.incr('upload_tries')
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
        tempopath = os.path.join('/tmp/', userpin)
        try:
            os.mkdir(fullpath)
        except:
            pass  # we don't care!
        try:
            os.mkdir(tempopath)
        except:
            pass
        ### process file
        tmpfile = os.path.join(tempopath, filename)
        finalfile = os.path.join(fullpath, filename)
        file.save(tmpfile)
        origimage = Image.open(tmpfile)
        scaledimage = auto_scale(origimage, HONDA_RES[car])
        scaledimage.save(finalfile, 'JPEG')
        os.remove(tmpfile)
        cache.incr('uploads')
        boxurl = request.url_root + 'data/boxes/' + userpin
        return render_template('success.html',
            filename=filename, car=car, url=boxurl)
    else: # GET method handler
        cache.incr('upload_gets')
        if not 'pin' in session:
            session['pin'] = random_pin()
        if not 'car' in session:
            session['car'] = next(iter(HONDA_RES.keys()))
        carlist = list(HONDA_RES.keys())
        return render_template('upload.html',
            cars=carlist, thecar=session['car'], pin=session['pin'])

def redisint(cache, key):
    getkey = cache.get(key)
    if getkey is None:
        return 0
    else:
        return int(getkey)

@app.route('/stats')
def stats():
    mains = redisint(cache, 'main_gets')
    uploads = redisint(cache, 'uploads')
    tries = redisint(cache, 'upload_gets')
    return render_template('stats.html',
        statreads=cache.incr('stat_gets'), mainloads=mains,
        uploads=uploads, tries=tries)

@app.route('/box')
@app.route('/box/')
def default_files():
    if 'pin' in session:
        return redirect('/data/boxes/' + session['pin'])
    else:
        return 'No files uploaded yet.'

@app.route('/data')
@app.route('/data/')
@app.route('/data/boxes')
@app.route('/data/boxes/')
def static_files():
    return redirect('.')

@app.route('/data/<path:path>')
def autoindex(path='.'):
    return files_index.render_autoindex(path)

if __name__ == "__main__":
    app.run("127.0.0.1", port = 8000, debug = True)

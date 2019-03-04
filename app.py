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
MIN_PIN_LEN = 6
HONDA_RES = {
    "Civic": "WGA",
    "Clarity": "WGA",
    "2018-2019 Accord": "720p",
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

# AutoIndex configuration
files_index = AutoIndex(app, '/data', add_url_rules=False)

@app.route('/')
def index():
    cache.incr('main_gets')
    if 'pin' in session:
        default_pin = session['pin']
    else:
        default_pin = None
    return render_template('index.html', pin = default_pin)

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
        if len(userpin) < MIN_PIN_LEN:
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
        cache.incr('upload_goods')
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

@app.route('/box/', methods=['GET', 'POST'])
@app.route('/box', methods=['GET', 'POST'])
def goto_box():
    cache.incr('download_gets')
    if request.method == 'POST': # POST method handler
        userpin = request.form['pin']
        if len(userpin) < 6:
            flash('PIN is too short')
            return redirect(request.url)
        boxpath = '/data/boxes/' + userpin
        session['pin'] = userpin
        return redirect(boxpath)
    else: # GET method handler
        if  'pin' in session:
            default_pin = session['pin']
        else:
            default_pin =''
        return render_template('download.html', pin=default_pin)

@app.route('/data/<path:path>')
def autoindex(path='.'):
    try:
        cache.incr('download_tries')
        cache.incr('download_goods')  # assume we succeed...
        return files_index.render_autoindex(path)
    except:
        cache.decr('download_goods')  # ...until we don't
        thebox = 'data/' + path
        return render_template('missing.html', box=thebox)

@app.route('/data')
@app.route('/data/')
@app.route('/data/boxes')
@app.route('/data/boxes/')
def static_files():
    return redirect('/box')

def redisint(key, cache=cache):
    getkey = cache.get(key)
    if getkey is None:
        return 0
    else:
        return int(getkey)

@app.route('/stats')
def stats():
    mains = redisint('main_gets')
    upload_goods = redisint('upload_goods')
    upload_gets = redisint('upload_gets')
    upload_tries = redisint('upload_tries')
    download_goods = redisint('download_goods')
    download_gets = redisint('download_gets')
    download_tries = redisint('download_tries')
    return render_template('stats.html',
      statreads=cache.incr('stat_gets'), mainloads=mains,
      upload_goods=upload_goods, upload_tries=upload_tries, upload_gets=upload_gets,
      download_goods=download_goods, download_tries=download_tries, download_gets=download_gets)

if __name__ == "__main__":
    app.run("0.0.0.0", port = 5000, debug = True)

from flask import Flask, render_template, request, send_file, redirect, url_for
from ftplib import FTP
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ftp = None

@app.route('/')
def index():
    return render_template('index.html', message=None, error=None, files=[])


@app.route('/connect', methods=['POST'])
def connect():
    global ftp
    host = request.form['host']
    username = request.form['username']
    
    password = request.form['password']
    
    try:
        ftp = FTP(host)
        ftp.login(user=username, passwd=password)
        files = ftp.nlst()  
        return render_template('index.html', message="Connected successfully!", error=None, files=files)
    except Exception as e:
        return render_template('index.html', message=None, error=f"Connection failed: {str(e)}", files=[])

@app.route('/upload', methods=['POST'])
def upload():
    global ftp
    if not ftp:
        return render_template('index.html', message=None, error="Not connected to any server.", files=[])

    file = request.files['file']
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        with open(filepath, 'rb') as f:
            ftp.storbinary(f'STOR {file.filename}', f)
        os.remove(filepath)
        files = ftp.nlst()
        return render_template('index.html', message="File uploaded successfully!", error=None, files=files)

@app.route('/download', methods=['POST'])
def download():
    global ftp
    if not ftp:
        return render_template('index.html', message=None, error="Not connected to any server.", files=[])

    filename = request.form['filename']
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        with open(filepath, 'wb') as f:
            ftp.retrbinary(f"RETR {filename}", f.write)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        files = ftp.nlst() if ftp else []
        return render_template('index.html', message=None, error=f"Download failed: {str(e)}", files=files)

@app.route('/disconnect', methods=['POST'])
def disconnect():
    global ftp
    if ftp:
        ftp.quit()
        ftp = None
    return render_template('index.html', message="Disconnected successfully!", error=None, files=[])

if __name__ == '__main__':
    app.run(debug=True)

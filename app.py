import io
import time
import hashlib
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from utils.encryption import encrypt_bytes, decrypt_bytes

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64 MB limit

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/encrypt', methods=['POST'])
def api_encrypt():
    if 'file' not in request.files or 'password' not in request.form:
        return jsonify({'error': 'File and password are required.'}), 400

    file = request.files['file']
    password = request.form['password']

    if not file.filename or not password:
        return jsonify({'error': 'Filename or password cannot be empty.'}), 400

    start_time = time.perf_counter()
    raw_data = file.read()
    orig_size = len(raw_data)
    orig_hash = hashlib.sha256(raw_data).hexdigest()

    encrypted_data = encrypt_bytes(raw_data, password)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    download_name = secure_filename(file.filename) + ".enc"

    response = send_file(
        io.BytesIO(encrypted_data),
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name=download_name
    )

    response.headers['X-Original-Size'] = str(orig_size)
    response.headers['X-Encrypted-Size'] = str(len(encrypted_data))
    response.headers['X-Original-Hash'] = orig_hash
    response.headers['X-Processing-Time-Ms'] = str(duration_ms)
    response.headers['Access-Control-Expose-Headers'] = (
        'X-Original-Size, X-Encrypted-Size, X-Original-Hash, X-Processing-Time-Ms'
    )
    return response

@app.route('/api/decrypt', methods=['POST'])
def api_decrypt():
    if 'file' not in request.files or 'password' not in request.form:
        return jsonify({'error': 'File and password are required.'}), 400

    file = request.files['file']
    password = request.form['password']

    if not file.filename or not password:
        return jsonify({'error': 'Filename or password cannot be empty.'}), 400

    encrypted_data = file.read()
    start_time = time.perf_counter()

    try:
        plaintext, verified_hash = decrypt_bytes(encrypted_data, password)
    except ValueError as err:
        return jsonify({'error': str(err)}), 400

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    download_name = secure_filename(file.filename)
    if download_name.endswith('.enc'):
        download_name = download_name[:-4]
    else:
        download_name = "decrypted_" + download_name

    response = send_file(
        io.BytesIO(plaintext),
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name=download_name
    )

    response.headers['X-Decrypted-Hash'] = verified_hash
    response.headers['X-Processing-Time-Ms'] = str(duration_ms)
    response.headers['Access-Control-Expose-Headers'] = (
        'X-Decrypted-Hash, X-Processing-Time-Ms'
    )
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
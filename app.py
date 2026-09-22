import io
import time
import zipfile
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
    uploaded_files = request.files.getlist('files')
    password = request.form.get('password')

    if not uploaded_files or not password:
        return jsonify({'error': 'Files and password are required.'}), 400

    # Filter out empty file objects
    files = [f for f in uploaded_files if f.filename]
    if not files:
        return jsonify({'error': 'No files selected.'}), 400

    # Single File Encryption
    if len(files) == 1:
        file = files[0]
        raw_data = file.read()
        encrypted_data = encrypt_bytes(raw_data, password)
        download_name = secure_filename(file.filename) + ".enc"

        return send_file(
            io.BytesIO(encrypted_data),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=download_name
        )

    # Batch Multi-File Encryption -> ZIP Archive
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            safe_name = secure_filename(file.filename)
            raw_data = file.read()
            encrypted_data = encrypt_bytes(raw_data, password)
            zip_file.writestr(f"{safe_name}.enc", encrypted_data)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='encrypted_vault_batch.zip'
    )

@app.route('/api/decrypt', methods=['POST'])
def api_decrypt():
    if 'file' not in request.files or 'password' not in request.form:
        return jsonify({'error': 'File and password are required.'}), 400

    file = request.files['file']
    password = request.form['password']

    if not file.filename or not password:
        return jsonify({'error': 'Filename or password cannot be empty.'}), 400

    encrypted_data = file.read()

    try:
        plaintext, verified_hash = decrypt_bytes(encrypted_data, password)
    except ValueError as err:
        return jsonify({'error': str(err)}), 400

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
    response.headers['Access-Control-Expose-Headers'] = 'X-Decrypted-Hash'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
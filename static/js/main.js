document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    const target = document.getElementById(btn.dataset.tab);
    if (target) target.classList.add('active');
  });
});

function handleFileSelection(inputId, previewId) {
  const input = document.getElementById(inputId);
  const preview = document.getElementById(previewId);
  if (!input || !preview) return;

  input.addEventListener('change', () => {
    if (input.files && input.files.length > 0) {
      if (input.files.length === 1) {
        const file = input.files[0];
        preview.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
      } else {
        let totalSize = Array.from(input.files).reduce((acc, f) => acc + f.size, 0);
        preview.textContent = `${input.files.length} files selected (${(totalSize / 1024).toFixed(1)} KB total - will bundle as .zip)`;
      }
    }
  });
}
handleFileSelection('enc-file-input', 'enc-file-preview');
handleFileSelection('dec-file-input', 'dec-file-preview');

['enc-drop-zone', 'dec-drop-zone'].forEach(id => {
  const zone = document.getElementById(id);
  if (!zone) return;

  ['dragenter', 'dragover'].forEach(eventName => {
    zone.addEventListener(eventName, (e) => {
      e.preventDefault();
      zone.classList.add('active');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    zone.addEventListener(eventName, (e) => {
      e.preventDefault();
      zone.classList.remove('active');
    });
  });
});

const passInput = document.getElementById('enc-password');
const bar = document.getElementById('strength-bar');
const label = document.getElementById('strength-label');
const advice = document.getElementById('strength-advice');

function updateStrengthUI() {
  if (passInput && typeof assessPassword === 'function') {
    const res = assessPassword(passInput.value);
    if (bar) {
      bar.style.width = res.percent + '%';
      bar.style.backgroundColor = res.color;
    }
    if (label) label.textContent = `Entropy: ~${res.entropy} bits`;
    if (advice) advice.textContent = res.advice;
  }
}
if (passInput) passInput.addEventListener('input', updateStrengthUI);

document.querySelectorAll('.toggle-visibility').forEach(btn => {
  btn.addEventListener('click', () => {
    const targetInput = document.getElementById(btn.dataset.target);
    if (!targetInput) return;
    if (targetInput.type === 'password') {
      targetInput.type = 'text';
      btn.textContent = '🔒';
    } else {
      targetInput.type = 'password';
      btn.textContent = '👁';
    }
  });
});

const genBtn = document.getElementById('generate-pass-btn');
if (genBtn) {
  genBtn.addEventListener('click', () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+~`|}{[]:;?><,./-=';
    const array = new Uint8Array(16);
    window.crypto.getRandomValues(array);
    let generatedPassword = '';
    for (let i = 0; i < array.length; i++) {
      generatedPassword += chars[array[i] % chars.length];
    }
    passInput.value = generatedPassword;
    passInput.type = 'text';
    const toggleBtn = document.querySelector('.toggle-visibility[data-target="enc-password"]');
    if (toggleBtn) toggleBtn.textContent = '🔒';
    updateStrengthUI();
  });
}

function processRequest(url, formData, progressContainer, progressBar, statusBox) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    statusBox.className = 'status-box';
    statusBox.style.display = 'none';
    progressContainer.style.display = 'block';
    progressBar.style.width = '0%';

    xhr.open('POST', url, true);
    xhr.responseType = 'blob';

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        progressBar.style.width = percent + '%';
      }
    };

    xhr.onload = () => {
      progressContainer.style.display = 'none';

      if (xhr.status === 200) {
        const disposition = xhr.getResponseHeader('Content-Disposition');
        let filename = 'downloaded_file';
        if (disposition && disposition.includes('filename=')) {
          filename = disposition.split('filename=')[1].replace(/"/g, '').trim();
        }

        const blob = xhr.response;
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(link.href);

        statusBox.className = 'status-box success';
        statusBox.textContent = `Success! File downloaded: ${filename}`;
        statusBox.style.display = 'block';
        resolve();
      } else {
        const blob = xhr.response;
        blob.text().then(text => {
          let errorMessage = "Invalid password or corrupted ciphertext.";
          try {
            const parsed = JSON.parse(text);
            if (parsed.error) errorMessage = parsed.error;
          } catch (_) {}

          statusBox.className = 'status-box error';
          statusBox.textContent = `Error: ${errorMessage}`;
          statusBox.style.display = 'block';
          reject();
        });
      }
    };

    xhr.onerror = () => {
      progressContainer.style.display = 'none';
      statusBox.className = 'status-box error';
      statusBox.textContent = 'A network error occurred. Is the server running?';
      statusBox.style.display = 'block';
      reject();
    };

    xhr.send(formData);
  });
}

const encForm = document.getElementById('encrypt-form');
if (encForm) {
  encForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('enc-file-input');
    const pInput = document.getElementById('enc-password');

    if (!fileInput.files.length) return alert('Select at least one file first.');
    if (!pInput.value) return alert('Enter a password.');

    const formData = new FormData();
    for (let i = 0; i < fileInput.files.length; i++) {
      formData.append('files', fileInput.files[i]);
    }
    formData.append('password', pInput.value);

    processRequest(
      '/api/encrypt',
      formData,
      document.getElementById('enc-progress-container'),
      document.getElementById('enc-progress-bar'),
      document.getElementById('enc-status')
    );
  });
}

const decForm = document.getElementById('decrypt-form');
if (decForm) {
  decForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('dec-file-input');
    const pInput = document.getElementById('dec-password');

    if (!fileInput.files.length) return alert('Select an encrypted file first.');
    if (!pInput.value) return alert('Enter a password.');

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('password', pInput.value);

    processRequest(
      '/api/decrypt',
      formData,
      document.getElementById('dec-progress-container'),
      document.getElementById('dec-progress-bar'),
      document.getElementById('dec-status')
    );
  });
}
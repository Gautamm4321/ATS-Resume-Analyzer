(function () {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('resumeInput');
    const fileName = document.getElementById('fileName');
    const form = document.getElementById('uploadForm');
    const btn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');

    if (!dropZone || !fileInput) return;

    // Click to upload
    dropZone.addEventListener('click', () => fileInput.click());

    // Drag & drop
    ['dragover', 'dragenter'].forEach(ev => {
        dropZone.addEventListener(ev, (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
    });
    ['dragleave', 'drop'].forEach(ev => {
        dropZone.addEventListener(ev, (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        });
    });
    dropZone.addEventListener('drop', (e) => {
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            showName();
        }
    });

    fileInput.addEventListener('change', showName);

    function showName() {
        if (fileInput.files.length) {
            const name = fileInput.files[0].name;
            fileName.textContent = '✅ ' + (name.length > 40 ? name.slice(0, 40) + '…' : name);
        }
    }

    form.addEventListener('submit', () => {
        if (!fileInput.files.length) return;
        btn.disabled = true;
        btnText.hidden = true;
        btnLoader.hidden = false;
    });
})();
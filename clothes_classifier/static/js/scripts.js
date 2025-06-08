function previewImage(input) {
    const preview = document.getElementById('preview');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

const dataScript = document.querySelector('script[type="application/json"]');

function toggleOutput() {
    const toggle = document.getElementById('outputToggle');
    const outputText = document.getElementById('outputText');
    const jsonOutput = document.getElementById('jsonOutput');

    if (!toggle || !outputText || !jsonOutput) return;

    if (toggle.checked && dataScript) {
        try {
            const data = JSON.parse(dataScript.textContent);
            jsonOutput.textContent = JSON.stringify(data, null, 2);
            outputText.style.display = 'none';
            jsonOutput.style.display = 'block';
        } catch (e) {
            console.error('JSON parse error:', e);
            jsonOutput.textContent = 'Помилка читання даних.';
            outputText.style.display = 'none';
            jsonOutput.style.display = 'block';
        }
    } else {
        outputText.style.display = 'block';
        jsonOutput.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('outputToggle');
    if (toggle) {
        toggle.addEventListener('change', toggleOutput);
    }
});

const MAX_IMAGE_BYTES = 10 * 1024 * 1024;
const PNG_DATA_URL = /^data:image\/png;base64,[A-Za-z0-9+/]+={0,2}$/;
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

async function bannerDescriptionTypeEffect() {
    const banner = document.querySelector('.banner-description');
    if (!banner || reducedMotion) return;
    const text = banner.textContent.trim() + "\n\nLet's style your dream photo!";
    banner.textContent = '';
    for (const character of text) {
        banner.textContent += character;
        await new Promise(resolve => setTimeout(resolve, 20));
    }
}
bannerDescriptionTypeEffect();

const craftingRoom = document.getElementById('crafting-room');
const featurePanels = document.querySelectorAll('#crafting-room > .collapse');

function validateFile(file) {
    if (!file) throw new Error('Choose all required images.');
    if (!file.size) throw new Error('The selected image is empty.');
    if (file.size > MAX_IMAGE_BYTES) throw new Error('Each image must be at most 10 MiB.');
    if (file.type && !['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)) {
        throw new Error('Only JPEG and PNG files are supported.');
    }
}

featurePanels.forEach(panel => {
    panel.addEventListener('shown.bs.collapse', event => {
        if (event.target === panel) craftingRoom.scrollIntoView({behavior: reducedMotion ? 'auto' : 'smooth'});
    });
    const feature = panel.dataset.id;
    const inputs = [...panel.querySelectorAll('input[type="file"]')];
    const tabs = [...panel.querySelectorAll('[data-bs-toggle="tab"]')];
    const templates = [...panel.querySelectorAll('input[name="style-template"]')];
    const popularPane = panel.querySelector('#style-blender-popular');
    const submit = panel.querySelector('.btn-submit');
    const loading = panel.querySelector('.btn-loading');
    const helper = panel.querySelector('.form-text');
    const download = panel.querySelector('.btn-download');
    const results = panel.querySelector('.result-section');
    const before = panel.querySelector('.result-before');
    const after = panel.querySelector('.result-after');
    const slider = panel.querySelector('#pencil-sharpness-slider');
    const spinner = panel.querySelector('.pencil-sharpness-wrapper .spinner-border');
    const consent = panel.querySelector('.analytics-consent');
    const controls = [...inputs, ...tabs, ...templates, ...(consent ? [consent] : [])];
    let busy = false;
    let resultUrl = null;
    let trackingToken = null;
    let previewUrl = null;
    let lastSharpness = slider ? slider.value : null;

    function message(text, error = false) {
        helper.textContent = text;
        helper.classList.toggle('text-danger', error);
        helper.classList.toggle('text-secondary', !error);
        helper.classList.toggle('d-none', !text);
    }

    function collectInputs() {
        const main = inputs[0].files[0];
        validateFile(main);
        const body = new FormData();
        body.append('image_0', main);
        if (feature === 'style-blender') {
            if (popularPane.classList.contains('active')) {
                const selected = templates.find(input => input.checked);
                if (!selected) throw new Error('Choose a style template.');
                body.append('style_filename', selected.value);
            } else {
                const style = inputs[1].files[0];
                validateFile(style);
                body.append('image_1', style);
            }
        }
        if (slider) body.append('sharpen_factor', slider.value);
        if (consent?.checked) {
            body.append('analytics_consent', 'true');
            if (slider && trackingToken) body.append('range_name', trackingToken);
        }
        return {main, body};
    }

    function updateControls() {
        controls.forEach(control => { control.disabled = busy; });
        let valid = false;
        try { collectInputs(); valid = true; } catch (_) { /* Incomplete input. */ }
        submit.disabled = busy || !valid;
        download.disabled = busy || !resultUrl;
        if (slider) slider.disabled = busy || !resultUrl;
        submit.classList.toggle('d-none', busy);
        loading.classList.toggle('d-none', !busy);
        if (spinner) spinner.classList.toggle('d-none', !busy || !resultUrl);
        panel.setAttribute('aria-busy', String(busy));
    }

    function clearResult() {
        resultUrl = null;
        trackingToken = null;
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        previewUrl = null;
        before.removeAttribute('src');
        after.removeAttribute('src');
        results.classList.add('d-none');
        if (slider) {
            slider.value = slider.min;
            lastSharpness = slider.value;
        }
    }

    function selectionChanged() {
        if (busy) return;
        clearResult();
        try { collectInputs(); message('Ready to process.'); }
        catch (error) { message(error.message, Boolean(inputs[0].files.length)); }
        updateControls();
    }

    async function process(isAdjustment = false) {
        if (busy) return;
        if (!isAdjustment) clearResult();
        let payload;
        try { payload = collectInputs(); }
        catch (error) { message(error.message, true); updateControls(); return; }
        busy = true;
        updateControls();
        message('Processing your image on the server. This may take a moment.');
        try {
            const response = await fetch(panel.dataset.endpoint, {method: 'POST', body: payload.body});
            const data = await response.json().catch(() => null);
            if (!response.ok) throw new Error(data?.error || `Image processing failed (HTTP ${response.status}).`);
            if (!data || typeof data.result !== 'string' || !PNG_DATA_URL.test(data.result)) {
                throw new Error('The server returned an invalid image.');
            }
            const image = new Image();
            image.src = data.result;
            await image.decode();
            const nextPreview = URL.createObjectURL(payload.main);
            if (previewUrl) URL.revokeObjectURL(previewUrl);
            previewUrl = nextPreview;
            before.src = previewUrl;
            after.src = data.result;
            resultUrl = data.result;
            trackingToken = typeof data.range_name === 'string' ? data.range_name : null;
            if (slider) lastSharpness = slider.value;
            results.classList.remove('d-none');
            message('');
        } catch (error) {
            if (slider) slider.value = lastSharpness;
            message(error instanceof TypeError ? 'Could not reach the server. Please try again.' : (error.message || 'Image processing failed.'), true);
        } finally {
            busy = false;
            updateControls();
        }
    }

    inputs.forEach(input => input.addEventListener('change', selectionChanged));
    templates.forEach(input => input.addEventListener('change', selectionChanged));
    tabs.forEach(tab => tab.addEventListener('shown.bs.tab', selectionChanged));
    if (consent) consent.addEventListener('change', selectionChanged);
    submit.addEventListener('click', () => process());
    if (slider) slider.addEventListener('change', () => process(true));
    download.addEventListener('click', () => {
        if (busy || !resultUrl) return;
        const link = document.createElement('a');
        link.href = resultUrl;
        link.download = `${feature}.png`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        if (trackingToken && consent?.checked) {
            fetch(panel.dataset.downloadEndpoint, {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({range_name: trackingToken}), keepalive: true
            }).catch(() => {});
        }
    });
    selectionChanged();
});

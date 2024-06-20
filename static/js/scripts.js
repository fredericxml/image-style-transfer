const craftingRoomSection = document.getElementById('crafting-room');
const tryFeatureButtons = document.querySelectorAll('#recommendations .try-feature');
const featureCollapses = document.querySelectorAll('#crafting-room .collapse');
tryFeatureButtons.forEach(button => {
    button.addEventListener('click', function () {
        featureCollapses.forEach(collapse => {
            collapse.classList.remove('show');
            collapse.addEventListener('shown.bs.collapse', function () {
                craftingRoomSection.scrollIntoView({ behavior: 'smooth' });
            });
        });
    });
});

const resultSection = document.querySelector('#crafting-room .result-section');
const resultBefore = document.querySelector('#crafting-room .result-before');
const resultAfter = document.querySelector('#crafting-room .result-after');

const pencilSharpnessWrapper = document.querySelector('#crafting-room .pencil-sharpness-wrapper');
const pencilSharpnessSlider = pencilSharpnessWrapper.querySelector('input');

featureCollapses.forEach(collapse => {
    const imageInputs = collapse.querySelectorAll('input[type="file"]');
    const submitButton = collapse.querySelector('.btn-submit');
    const popularTab = collapse.querySelector('#tab-style-blender-popular');

    function handleSubmitButtonDisable() {
        let emptyInputCount = imageInputs.length;
        imageInputs.forEach(input => {
            const tabPane = input.closest('.tab-pane');
            if (tabPane) {
                // If input is in tab pane and tab is active, only for style blender
                if (tabPane.classList.contains('active') && input.files.length)
                    emptyInputCount--;
            } else {
                if (input.files.length) emptyInputCount--;
            }
        });
        if (collapse.dataset.id === 'style-blender') {
            if (popularTab.classList.contains('active')) emptyInputCount--;
        }
        // Disable button if the number of input is not complete
        submitButton.disabled = emptyInputCount;
    }
    if (collapse.dataset.id === 'style-blender') {
        const tabButtons = collapse.querySelectorAll('.nav-link');
        tabButtons.forEach(button => {
            button.addEventListener('click', handleSubmitButtonDisable);
        });
    }
    imageInputs.forEach(input => (input.addEventListener('input', handleSubmitButtonDisable)));

    const loadingButton = collapse.querySelector('.btn-loading');
    const helperText = collapse.querySelector('.form-text');

    function process(param) {
        submitButton.classList.toggle('d-none');
        loadingButton.classList.toggle('d-none');
        helperText.classList.remove('d-none');
        helperText.innerText = 'Hold on, let me cook! It should not take more than three minutes...';

        let hasInvalidFile = false;
        const validFileTypes = ['image/jpeg', 'image/jpg', 'image/png'];

        const formData = new FormData();
        imageInputs.forEach((input, index) => {
            const file = input.files[0];
            const tabPane = input.closest('.tab-pane');
            if (tabPane) {
                // If input is in tab pane and tab is active, only for style blender
                if (tabPane.classList.contains('active')) {
                    if (validFileTypes.includes(file.type))
                        formData.append(`image_${index}`, file);
                    else hasInvalidFile = true;
                }
            } else {
                if (validFileTypes.includes(file.type))
                    formData.append(`image_${index}`, file);
                else hasInvalidFile = true;
            }
        });
        if (hasInvalidFile) {
            helperText.innerText = 'Only JPEG and PNG files are allowed.';
            submitButton.classList.toggle('d-none');
            loadingButton.classList.toggle('d-none');
            return;
        }

        for (const item of param) {
            Object.entries(item).forEach(([key, value]) => {
                formData.append(key, value);
            });
        }

        const url = `/${collapse.dataset.id}`;
        const options = {
            method: 'POST',
            headers: {},
            body: formData
        };
        fetch(url, options)
            .then(response => response.json())
            .then(data => {
                const reader = new FileReader();
                reader.onload = (e) => (resultBefore.src = e.target.result);
                reader.readAsDataURL(imageInputs[0].files[0]);

                resultAfter.src = data.result;
                downloadButton.dataset.src = data.result;

                helperText.classList.toggle('d-none');
                submitButton.classList.toggle('d-none');
                loadingButton.classList.toggle('d-none');
                resultSection.classList.remove('d-none');
            })
            .catch(error => {
                console.error('Fetch error:', error);
                helperText.innerText = 'An error occurred while processing the request.';
                submitButton.classList.toggle('d-none');
                loadingButton.classList.toggle('d-none');
            });
    }

    submitButton.addEventListener('click', function () {
        pencilSharpnessSlider.value = pencilSharpnessSlider.getAttribute('min');

        let param = [];
        if (collapse.dataset.id === 'style-blender') {
            if (popularTab.classList.contains('active')) {
                const options = collapse.querySelectorAll('input[name="style-template"]');

                let selectedStyle;
                for (const option of options) {
                    if (option.checked) selectedStyle = option.value;
                }
                param.push({ style_filename: selectedStyle });
            }
        }
        process(param);
    });

    // Pencil sketch feature
    collapse.addEventListener('shown.bs.collapse', function () {
        if (collapse.dataset.id === 'pencil-sketch') {
            pencilSharpnessWrapper.classList.remove('d-none');
        } else {
            pencilSharpnessWrapper.classList.add('d-none');
        }
    });
    if (collapse.dataset.id === 'pencil-sketch') {
        pencilSharpnessSlider.addEventListener('change', function () {
            process([{ sharpen_factor: pencilSharpnessSlider.value }]);
        });
    }
});

const downloadButton = document.querySelector('#crafting-room .btn-download');
downloadButton.addEventListener('click', function () {
    const downloadLink = document.createElement('a');
    downloadLink.href = downloadButton.dataset.src;
    downloadLink.download = 'styledreamer-download.png';
    downloadLink.click();
});
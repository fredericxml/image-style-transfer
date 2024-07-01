async function bannerDescriptionTypeEffect() {
    const bannerDescription = document.querySelector('.banner-description');
    const text = bannerDescription.dataset.description + "\n\nLet's style your dream photo!";
    bannerDescription.innerText = '';

    for (let i = 0; i < text.length; i++) {
        bannerDescription.innerText += text.charAt(i);
        await new Promise(resolve => setTimeout(resolve, 20));
    }
}
bannerDescriptionTypeEffect();

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

featureCollapses.forEach(collapse => {
    const imageInputs = collapse.querySelectorAll('input[type="file"]');
    const submitButton = collapse.querySelector('.btn-submit');
    const popularTab = collapse.querySelector('#tab-style-blender-popular');
    const pencilSharpnessSpinner = collapse.querySelector('.pencil-sharpness-wrapper .spinner-border');

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
    const downloadButton = collapse.querySelector('.btn-download');
    const resultSection = collapse.querySelector('.result-section');
    const resultBefore = collapse.querySelector('.result-before');
    const resultAfter = collapse.querySelector('.result-after');

    function process(param) {
        submitButton.classList.toggle('d-none');
        loadingButton.classList.toggle('d-none');
        helperText.classList.remove('d-none');
        if (pencilSharpnessSpinner) pencilSharpnessSpinner.classList.toggle('d-none');
        helperText.innerHTML = 'Hold on, it might take a while... If it takes longer than 3 minutes, <a href="javascript:void(0);" onclick="location.reload();">refresh</a> the page or try again later.';

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
            helperText.innerText = 'Hint: Only JPEG and PNG files are allowed.';
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
                downloadButton.dataset.range_name = data.range_name;

                helperText.classList.toggle('d-none');
                submitButton.classList.toggle('d-none');
                loadingButton.classList.toggle('d-none');
                resultSection.classList.remove('d-none');
                if (pencilSharpnessSpinner) pencilSharpnessSpinner.classList.toggle('d-none');
            })
            .catch(error => {
                console.error('Error:', error);
                helperText.innerText = 'An error occurred while processing the request.';
                submitButton.classList.toggle('d-none');
                loadingButton.classList.toggle('d-none');
            });
    }


    const pencilSharpnessSlider = document.querySelector('#crafting-room #pencil-sharpness-slider');

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

    // Pencil sketch slider handler
    if (collapse.dataset.id === 'pencil-sketch') {
        pencilSharpnessSlider.addEventListener('change', function () {
            process([{
                sharpen_factor: pencilSharpnessSlider.value,
                range_name: downloadButton.dataset.range_name
            }]);
        });
    }

    downloadButton.addEventListener('click', function () {
        const options = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ range_name: downloadButton.dataset.range_name })
        };
        fetch('/download', options)
            .then(response => response.json())
            .then(data => {
                const downloadLink = document.createElement('a');
                downloadLink.href = downloadButton.dataset.src;
                downloadLink.download = 'StyleDreamer-download.png';
                downloadLink.click();
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
});
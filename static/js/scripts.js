const tryFeatureButtons = document.querySelectorAll('#recommendations .try-feature');
const featureCollapses = document.querySelectorAll('#crafting-room .collapse');
tryFeatureButtons.forEach(button => {
    button.addEventListener('click', function () {
        featureCollapses.forEach(collapse => {
            collapse.classList.remove('show');
        });
    });
});

const resultSection = document.querySelector('#crafting-room .result-section');
const resultBefore = document.querySelector('#crafting-room .result-before');
const resultAfter = document.querySelector('#crafting-room .result-after');

const pencilSharpnessWrapper = document.querySelector('#crafting-room .pencil-sharpness-wrapper');
const pencilSharpnessSlider = pencilSharpnessWrapper.querySelector('input');

featureCollapses.forEach(collapse => {
    const imageInputs = collapse.querySelectorAll('input');
    const submitButton = collapse.querySelector('.btn-submit');

    imageInputs.forEach(input => {
        input.addEventListener('input', function () {
            let emptyInputCount = imageInputs.length;
            imageInputs.forEach(imageInput => {
                if (imageInput.files.length) emptyInputCount--;
            });
            // Disable button if there is any empty input
            submitButton.disabled = emptyInputCount;
        });
    });

    const loadingButton = collapse.querySelector('.btn-loading');
    const helperText = collapse.querySelector('.form-text');

    function process(param) {
        submitButton.classList.toggle('d-none');
        loadingButton.classList.toggle('d-none');
        helperText.classList.remove('d-none');
        helperText.innerText = 'Hold on, let me cook! It should not take more than three minutes...';

        const formData = new FormData();
        imageInputs.forEach((input, index) => {
            formData.append(`image_${index}`, input.files[0]);
        });
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
            .catch(console.error);
    }

    submitButton.addEventListener('click', function () {
        pencilSharpnessSlider.value = pencilSharpnessSlider.getAttribute('min');
        process([]);
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
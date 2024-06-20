import random


def banner_description():
    banner_description_list = [
        'It merges technology and creativity, transforming photos with diverse artistic styles.',
        'Using Generative AI, ordinary photos are turned into captivating visual masterpieces.',
        'It offers endless possibilities for creative expression and artistic innovation.',
        'Generative AI redefines how we perceive and interact with visual art.',
        'It blends art and technology to inspire awe and imagination.',
        'Artistic styles of famous painters can be seamlessly applied to photos using AI.',
        'It allows for the creation of unique visual aesthetics.',
        'It transforms simple snapshots into captivating visual compositions.',
        'It offers a new way to explore and experiment with artistic styles.',
        'Through Generative AI, photos are transformed into personalized works of art.',
        'It bridges the gap between technology and artistic creativity.',
        'Using Generative AI, photos can emulate the styles of renowned painters effortlessly.',
        'It offers a novel approach to enhancing visual storytelling.',
        'It enhances photos by infusing them with artistic flair.',
        'It unlocks new potentials for digital artistry and creativity.',
        'By leveraging Generative AI, users can transform their photos into visually striking artworks.',
        'It automates the application of artistic styles to photos, enhancing creativity.',
        'Using Generative AI, users can apply diverse artistic inspirations to their photos seamlessly.',
        'It expands the possibilities of digital artistry with automated style application.',
        'It empowers users to create unique visual narratives from their photos using Generative AI.'
    ]
    banner_description = 'Style Dreamer is a tool to transform photos into stunningly styled images. '
    banner_description += random.choice(banner_description_list)
    return banner_description


def feature_list():
    feature_list = [
        {
            'title': 'Style Blender',
            'description': 'Turn your photos into stunning artworks with our style blender technology.',
            'story': 'Harnessing the power of style blender through Generative AI, photographs metamorphose into kaleidoscopic visions, blending the essence of classic paintings with contemporary imagery, evoking emotions that transcend time and technology.'},
        {
            'title': 'Cartoonize',
            'description': 'Transform your photos into whimsical, animated masterpieces.',
            'story': 'Cartoonifying with Generative AI transforms mundane photographs into vibrant, animated caricatures, where everyday scenes leap to life with exaggerated features and whimsical charm. It offers a playful reinterpretation of reality to evoke joy and imaginative exploration.'},
        {
            'title': 'Pencil Sketch',
            'description': 'Turn your memories into timeless pencil sketches of hand-drawn magic.',
            'story': 'Delving into the realm of pencil sketch filter, where digital precision converges with the nostalgic allure of hand-drawn artistry. Each image unfolds as a delicate dance of lines and shading, capturing the essence of moments with an emotive depth that resonates beyond pixels.'},
    ]
    for feature in feature_list:
        feature['id'] = '-'.join(feature['title'].lower().split())
    return feature_list


def style_template_list():
    style_template_list = [
        {'filename': 'People (AI Generated).jpg'},
        {'filename': 'Phantasmagorical (Pripyat).jpg'},
        {'filename': 'Mona Lisa (Leonardo da Vinci).jpg'},
        {'filename': 'The Visitor (Hennie Niemann).jpg'},
        {'filename': 'Starry Night (Van Gogh).jpg'},
        {'filename': 'Prayer in the Garden (Sebastiano Ricci).jpg'},
        {'filename': 'The Great Wave off Kanagawa (Katsushika Hokusai).jpg'},
        {'filename': 'Circles in a Circle (Vassily Kandinsky).jpg'},
    ]
    return style_template_list
# User guide

Open the application and choose **Try Now** on the feature you want to use. All three processing pipelines run on the application server, independently of the optional analytics service.

## Style Blender

1. Select a JPEG or PNG as the **Main image**.
2. Under **Style image**, choose **Popular** for a bundled reference or **Upload** to select your own JPEG or PNG style reference.
3. Select **Cook It!**. The result appears in the Before/After comparison.
4. Select **Download** to save `style-blender.png`.

Bundled references:

- People (AI Generated)
- Mona Lisa (Leonardo da Vinci)
- The Visitor (Hennie Niemann)
- Phantasmagorical (Pripyat)
- Starry Night (Van Gogh)
- Prayer in the Garden (Sebastiano Ricci)
- The Great Wave off Kanagawa (Katsushika Hokusai)
- Circles in a Circle (Vassily Kandinsky)

The processing module also supports optional content-style bottleneck interpolation at the Python function level; see the [API reference](api.md). This parameter is not exposed as a web slider or HTTP field.

## Cartoonize

1. Upload a main image.
2. Select **Cook It!** to run the pretrained CartoonGAN model.
3. Inspect the Before/After comparison and select **Download** to save `cartoonize.png`.

## Pencil Sketch

1. Upload a main image and select **Cook It!**.
2. Once a result is available, adjust the **Sharpness** slider (4–40). The default value of 4 applies no extra sharpening. Each completed slider change requests a new result.
3. Select **Download** to save `pencil-sketch.png`.

If a sharpness adjustment fails, the previous successful result and slider value are retained. Choosing a new input clears the previous preview and resets sharpness.

## Input and output limits

| Property | Value |
| --- | --- |
| Supported input | JPEG, PNG |
| Maximum file size | 10 MiB per image |
| Maximum image resolution | 12 million pixels per image |
| Maximum HTTP request | 21 MiB including multipart overhead |
| Output | PNG; longest side at most 350 pixels |

The application validates the actual uploaded bytes and dimensions. Neural models use square inputs; results may show distortion or artifacts. The output is resized to match the source aspect ratio within pixel rounding. The browser download does not depend on analytics.

## Optional image archiving and activity tracking

When the operator configures analytics, an unchecked consent box appears in each feature panel. Read it before selecting it. If accepted, processing can send input images to ImgBB and record metadata in Google Sheets, including sketch settings and download actions. Use synthetic or authorized non-sensitive images only. ImgBB links may be publicly accessible.

Changing the consent selection clears the previous result; process again to generate a result under the new setting. Turning off consent does not delete previously archived images or spreadsheet records. See [analytics setup and data handling](analytics.md).

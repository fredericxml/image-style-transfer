# API reference

Base URL for local use: `http://127.0.0.1:5000`. The image processing endpoints accept `multipart/form-data` and return JSON. GET on processing or download endpoints returns an informational message; GET `/` renders the web interface.

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/` | GET | Application interface |
| `/style-blender` | POST | Arbitrary neural style transfer |
| `/cartoonize` | POST | Cartoonization |
| `/pencil-sketch` | POST | Pencil sketch generation |
| `/download` | POST | Optional download tracking |

## Processing parameters

| Field | Endpoints | Description |
| --- | --- | --- |
| `image_0` | All processing routes | Required JPEG/PNG file |
| `image_1` | Style Blender | Custom style JPEG/PNG; required when `style_filename` is absent |
| `style_filename` | Style Blender | Exact bundled template filename; mutually exclusive with `image_1` |
| `sharpen_factor` | Pencil Sketch | Optional integer 4–40; 4 or omission disables extra sharpening |
| `analytics_consent` | All processing routes | Optional; exact string `true` permits configured external tracking |
| `range_name` | Pencil Sketch | Optional signed tracking token from a previous result for the same image; used with consent to update the existing row |

See [input limits](usage.md#input-and-output-limits) for file and request restrictions. Built-in template filenames match the files in `models/style_transfer/images/` and the application's template allowlist.

### Example requests

Run from a shell with curl installed and replace filenames with local, non-sensitive test images. On Windows use `curl.exe` if PowerShell resolves `curl` to an alias.

```bash
curl -F 'image_0=@content.png' -F 'image_1=@style.png' http://127.0.0.1:5000/style-blender
curl -F 'image_0=@content.png' -F 'style_filename=Starry Night (Van Gogh).jpg' http://127.0.0.1:5000/style-blender
curl -F 'image_0=@content.png' http://127.0.0.1:5000/cartoonize
curl -F 'image_0=@content.png' -F 'sharpen_factor=15' http://127.0.0.1:5000/pencil-sketch
```

These examples do not opt in to external tracking. JSON responses contain base64 image data, not a binary PNG body.

### Response format

Successful processing (HTTP 200; abbreviated PNG data):

```json
{"result": "data:image/png;base64,...", "range_name": null}
```

With configured analytics and consent, `range_name` can contain an opaque signed token instead of `null`. A missing token may indicate that tracking was disabled or unsuccessful. The image transformation does not depend on tracking success.

| HTTP status | Meaning |
| --- | --- |
| 200 | Processing succeeded |
| 400 | Invalid input or malformed request |
| 413 | Request or file exceeds byte limit |
| 500 | Image processing failed |

Error bodies contain an `error` message. Example: `{"error": "Image is empty."}`.

## Download tracking

`POST /download` accepts `application/json` with `{"range_name": "<signed token>"}`. The response is `{"tracked": true}` on a successful spreadsheet update or `{"tracked": false}` when tracking cannot be recorded. This endpoint does not serve the PNG; decode the processing response or use the browser download control. Only send a token following a consented download action. Tokens expire after 24 hours and arbitrary spreadsheet ranges are not accepted.

## Python-level content blending

`modules.style_transfer.do_style_transfer` accepts an optional `content_blending_ratio` parameter (0–1, default 0). The parameter interpolates the predicted content and style bottlenecks before transformation. It is part of the Python processing interface, not a public HTTP parameter or web control.

```python
from pathlib import Path
from modules.style_transfer import do_style_transfer

result = do_style_transfer(
    Path('content.png').read_bytes(),
    Path('style.png').read_bytes(),
    from_style_template=False,
    content_blending_ratio=0.25,
)
```

The Python result contains `image`, `content_dimension`, and `style_dimension`. `image` is a PNG data URI. The other image processing modules similarly return PNG data and input dimensions. See the source for implementation details.

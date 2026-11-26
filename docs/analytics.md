# Image archiving and analytics

The application can store input images in ImgBB and log processing activity in Google Sheets. This integration is optional and disabled by default. Enabling it does not replace local inference. The user must opt in before external tracking is performed.

## 1. Install dependencies

Inside the Python 3.11 virtual environment:

```bash
python -m pip install -r requirements-analytics.txt
```

This includes all local processing dependencies.

## 2. Configure ImgBB

Obtain an API key from the [ImgBB API website](https://api.imgbb.com/). Keep it private. The application uses the upload API to archive the original main image and, for custom style transfer, the uploaded style image. The generated image is returned directly by the application, not uploaded by the tracking implementation.

## 3. Configure Google Sheets

1. In a Google Cloud project you are authorized to administer, [enable the Google Sheets API](https://developers.google.com/workspace/guides/enable-apis).
2. Follow Google's [service account credential guide](https://developers.google.com/workspace/guides/create-credentials) to create a dedicated service account and, where your organization's policy permits, obtain its JSON key.
3. Create `secret/` in the repository root and store the credential as `secret/service-account.json` (or configure a different secure location). Never commit the file.
4. Create a dedicated spreadsheet and share it with the service account email (`client_email` in the JSON) as an editor. A Cloud IAM role alone does not grant access to the spreadsheet. No domain-wide delegation is needed for this direct sharing workflow.
5. Copy the spreadsheet ID from its URL, between `/d/` and the next `/`.
6. Create the three tabs below with the exact names and paste the matching tab-separated headers into cell A1. Do not insert additional columns into the tracked schema.

### Style Transfer (A–M)

```text
Date	Time	Content ID	Content Link	Content Filename	Content Dimensions	Content Size (MB)	Style ID	Style Link	Style Filename	Style Dimensions	Style Size (MB)	Downloaded
```

### Cartoonize (A–H)

```text
Date	Time	Image ID	Image Link	Filename	Dimensions	Size (MB)	Downloaded
```

### Pencil Sketch (A–I)

```text
Date	Time	Image ID	Image Link	Filename	Dimensions	Size (MB)	Sharpness	Downloaded
```

Dimensions are recorded as height × width; file sizes use decimal MB. For built-in style references, the style ID contains `template:<filename>` and the other style metadata columns remain blank.

## 4. Set environment variables

Copy `.env.example` to `.env` (see [configuration](configuration.md)). Edit the values locally:

```dotenv
ANALYTICS_ENABLED=true
IMGBB_API_KEY=<your-key>
SPREADSHEET_ID=<your-spreadsheet-id>
GOOGLE_SERVICE_ACCOUNT_FILE=secret/service-account.json
TRACKING_SECRET=<your-random-signing-secret>
```

Replace all placeholders with actual values; do not commit `.env`. Generate a private signing secret locally:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

The secret must be at least 32 characters. Do not reuse an API key as the signing secret. Environment variables already set in the shell take precedence over `.env`. Restart the application after configuration changes.

## 5. Verify the integration

Use a disposable spreadsheet and synthetic test images that contain no personal information.

| Workflow | Expected tracking behavior |
| --- | --- |
| Process with consent unchecked | No ImgBB upload or spreadsheet write |
| Built-in Style Blender | One input image archived; template recorded; one row in Style Transfer |
| Custom Style Blender | Main and style inputs archived; one row in Style Transfer |
| Cartoonize | One archived input and one row in Cartoonize |
| Pencil Sketch | One archived input and one row in Pencil Sketch; default sharpness stored as `-1` |
| Adjust sketch sharpness | With a valid token for the same image, update column H of the existing row without reuploading |
| Download tracked result | Set downloaded flag to `1` in column M, H or I for the respective tab |

A download flag starts at `0`; it records the browser's download action, not confirmation that a file was saved. Signed tracking tokens expire after 24 hours. A missing or expired token can lead to a new sketch tracking row when processing again. Downloading still works if tracking fails.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Consent checkbox missing | Analytics flag, nonempty API key and spreadsheet ID, signing secret length, server restart |
| Checkbox present but no log row | Consent checked, optional dependencies installed, correct credential file, valid ImgBB key, Sheets API enabled, spreadsheet shared with service account, exact tab names; inspect server warnings |
| Images archived but no row | Spreadsheet permissions and schema; an upload can succeed before a spreadsheet write fails |
| Sketch creates another row | Same image bytes, previous valid tracking token, consent enabled, token not expired |
| Download flag stays `0` | Valid tracking token, consent, spreadsheet connectivity; browser download itself is independent |

## Data handling

Opt-in is unchecked by default. Image data sent to ImgBB leaves the application server; returned links may be publicly accessible. Filenames, dimensions, image IDs and links, dates, times, sizes, sketch settings and download status are stored in the spreadsheet. Use authorized non-sensitive images, limit spreadsheet access, and define a retention and deletion policy before enabling tracking for other users. Turning off consent prevents new tracking requests but does not delete existing records. The application does not include automatic deletion or cleanup of partial uploads. Service failures are logged and do not invalidate successful image processing. For the HTTP contract, see the [API reference](api.md).

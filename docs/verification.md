# Verification

Run the test suite in the Python 3.11 environment:

```bash
python -m pip check
python -m unittest discover -s tests -v
python scripts/verify_release.py --repeat 5
```

The integration tests invoke the bundled models through Flask's test client. The verification script saves synthetic inputs and actual generated PNGs to `verification-output/` and reports request latency and process RSS. RSS snapshots are not peak memory measurements or proof of leak-free operation.

For browser verification, start `app.py` and check all three features, built-in and custom style references, the sharpness slider, downloads, invalid uploads, and desktop/mobile layouts. Inspect generated images for artifacts, aspect ratio and color consistency. With analytics disabled or consent unchecked, no images or activity metadata should be sent to ImgBB or Google Sheets. CDN requests for interface resources are expected. Test optional analytics separately with a disposable spreadsheet and synthetic images; the analytics unit tests use mocks and do not contact either service.

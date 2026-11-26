# Configuration

The application reads `.env` from the repository root at startup. Variables already defined in the operating system or deployment environment take precedence. Restart the server after changing configuration.

## Local processing

Install `requirements.txt` in a Python 3.11 virtual environment and run `python app.py` using that environment. No `.env` file or external credentials are required for the default configuration. For customized settings, copy the example:

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

```bash
# Linux
cp .env.example .env
```

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_HOST` | `127.0.0.1` | Local bind address |
| `APP_PORT` | `5000` | HTTP port |
| `ANALYTICS_ENABLED` | `false` | Enable optional external storage and tracking (`true`, `1` or `yes`) |
| `IMGBB_API_KEY` | Empty | ImgBB upload credential |
| `SPREADSHEET_ID` | Empty | Destination Google spreadsheet ID |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | `secret/service-account.json` | Service account JSON path; relative paths resolve from the repository root |
| `TRACKING_SECRET` | Empty | Secret for signing tracking tokens; at least 32 characters |

Install `requirements-analytics.txt` for analytics; it includes the base requirements. Follow the [analytics guide](analytics.md) for external credentials and spreadsheet setup. The tracking checkbox appears when analytics is enabled and the API key, spreadsheet ID and sufficiently long signing secret are configured. The checkbox alone does not confirm that the services are reachable or credentials are valid.

## Local credential files

```text
image-style-transfer/
├── .env.example                  # Commit this template
├── .env                          # Local configuration; ignored by Git
└── secret/                       # Create locally when needed; ignored by Git
    └── service-account.json      # Google-issued credential; never commit
```

There is no need to create an example service account JSON. Obtain credentials from the provider, store them securely, and grant access only to the intended spreadsheet. Keep `.env`, private keys, and credential JSON out of Git. Use a securely managed environment or secret store for hosted deployments. Do not expose Flask's development server publicly.

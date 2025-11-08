# Quick Setup Guide

## Prerequisites
- Python 3.9 or higher
- pip package manager

## Installation Steps

1. **Navigate to project directory**:
   ```bash
   cd provider_validation_system
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your actual API keys from:
   - HuggingFace: https://huggingface.co/settings/tokens
   - Google Gemini: https://makersuite.google.com/app/apikey
   - OpenAI: https://platform.openai.com/api-keys
   - TomTom: https://developer.tomtom.com/
   - NumVerify: https://numverify.com/
   - LocationIQ: https://locationiq.com/
   - OCR.space: https://ocr.space/ocrapi
   - NPI Registry: Use "FREE" for public API

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Access the web interface**:
   Open your browser and go to: `http://localhost:5000`

## Testing

1. Use the sample data file: `data/synthetic_providers.csv`
2. Upload it through the web interface
3. Monitor processing in real-time
4. Review results and export reports

## Troubleshooting

- **Import errors**: Make sure you're in the `provider_validation_system` directory or have added it to PYTHONPATH
- **API errors**: Verify your API keys in the `.env` file
- **Database errors**: Delete `database.db` and restart the app to recreate the database
- **Port in use**: Change the port in `app.py` (line with `app.run()`)


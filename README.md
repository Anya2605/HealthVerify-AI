# HealthVerify AI - Provider Data Validation System

An automated healthcare provider directory validation system that validates 200 provider profiles in under 30 minutes with 80%+ validation accuracy.

## Features

- ⚡ **Fast Processing**: Validate 200 providers in under 30 minutes
- 🎯 **High Accuracy**: 80%+ validation accuracy with ML-based confidence scoring
- 🤖 **AI-Powered**: Multi-agent system with intelligent validation
- 📊 **Real-time Dashboard**: Track validation progress and KPIs
- 🚩 **Flag Management**: Automatic flagging of issues requiring review
- 📈 **Comprehensive Reports**: Export validation results to Excel

## Tech Stack

- **Backend**: Python 3.9+, Flask
- **Database**: SQLite
- **Frontend**: HTML5, TailwindCSS (CDN), Vanilla JavaScript
- **AI/ML**: Gemini API, Hugging Face, OpenAI
- **APIs**: NPI Registry, TomTom, LocationIQ, NumVerify

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd provider_validation_system
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Create a `.env` file in the `provider_validation_system` directory
   - Add your API keys in the following format:
   ```
   # AI/ML APIs
   HUGGINGFACE_API_KEY=your_key_here
   GEMINI_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   
   # Data Validation APIs
   TOMTOM_API_KEY=your_key_here
   NUMVERIFY_API_KEY=your_key_here
   LOCATIONIQ_API_KEY=your_key_here
   OCRSPACE_API_KEY=your_key_here
   
   # Free Public APIs
   NPI_REGISTRY_API_KEY=FREE
   NPI_REGISTRY_API_URL=https://npiregistry.cms.hhs.gov/api/
   ```
   - **Note**: The API keys provided in the project specification should be added to your `.env` file

5. **Initialize the database**:
   The database will be automatically created on first run.

## Usage

1. **Start the Flask application**:
   ```bash
   cd provider_validation_system
   python app.py
   ```
   
   Or from the project root:
   ```bash
   python provider_validation_system/app.py
   ```

2. **Access the web interface**:
   Open your browser and navigate to `http://localhost:5000`

3. **Upload provider data**:
   - Go to the Upload page
   - Select a CSV or Excel file with provider data
   - Required columns: `npi`, `first_name`, `last_name`, `specialty`, `practice_address`, `city`, `state`, `zip_code`, `phone`
   - Optional columns: `email`, `website`, `provider_id`

4. **Monitor processing**:
   - View real-time progress on the Processing page
   - Check the Dashboard for KPIs and statistics

5. **Review results**:
   - View validation results on the Results page
   - Check Flagged Items for issues requiring review
   - Export reports to Excel

## Project Structure

```
provider_validation_system/
├── app.py                 # Flask main application
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── .env                   # API keys (create this)
├── agents/                # AI agents
│   ├── data_validation_agent.py
│   ├── enrichment_agent.py
│   ├── quality_agent.py
│   └── directory_agent.py
├── services/              # API services
│   ├── npi_service.py
│   ├── location_service.py
│   ├── phone_service.py
│   ├── gemini_service.py
│   ├── huggingface_service.py
│   ├── web_scraper.py
│   └── ml_models.py
├── utils/                 # Utilities
│   ├── database.py
│   ├── file_processor.py
│   ├── confidence_scorer.py
│   └── report_generator.py
├── models/                # Data models
│   └── schema.py
├── templates/             # HTML templates
├── static/                # CSS and JavaScript
└── data/                  # Sample data and results
```

## Agent 1: Data Validation Agent

The Data Validation Agent performs comprehensive validation:

1. **NPI Validation**: Verifies NPI against CMS NPI Registry
2. **Address Validation**: Geocodes and validates addresses using TomTom/LocationIQ
3. **Phone Validation**: Validates phone numbers using NumVerify
4. **Web Presence**: Searches and verifies provider websites
5. **Confidence Scoring**: Calculates weighted confidence scores
6. **Flag Generation**: Automatically flags issues for review

## API Keys Required

- **Gemini API**: For document extraction and OCR
- **Hugging Face API**: For NLP and text similarity
- **TomTom API**: For geocoding (primary)
- **LocationIQ API**: For geocoding (backup)
- **NumVerify API**: For phone validation
- **NPI Registry**: Free public API (no key needed)

## Performance Targets

- ✅ Validation Accuracy: 80%+ success rate
- ✅ Processing Speed: 100 providers in under 5 minutes
- ✅ Information Extraction: 85%+ accuracy from PDFs
- ✅ Throughput: 500+ provider validations per hour

## Troubleshooting

1. **API Errors**: Check your API keys in `.env` file
2. **Database Errors**: Delete `database.db` and restart the app
3. **Import Errors**: Ensure all dependencies are installed: `pip install -r requirements.txt`
4. **Port Already in Use**: Change the port in `app.py` or kill the process using port 5000

## License

This project is for demonstration purposes.

## Support

For issues or questions, please check the documentation or create an issue in the repository.


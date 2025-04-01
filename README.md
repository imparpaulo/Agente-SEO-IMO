# Agente SEO IMO - Real Estate Ad Optimizer

An AI-powered tool for analyzing and optimizing real estate listings.

## Setup

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Copy `.env.example` to `.env` and configure your environment variables
5. Run the application:
```bash
streamlit run streamlit_app.py
```

## Usage

1. Paste your real estate listing text into the chat input
2. Wait for the AI analysis
3. Review the optimization suggestions

## Environment Variables

- `WEBHOOK_URL`: URL for the webhook endpoint
- `BEARER_TOKEN`: Authentication token
- `MAX_MESSAGES`: Maximum number of messages to store (default: 50)
- `TIMEOUT_SECONDS`: Request timeout in seconds (default: 30)

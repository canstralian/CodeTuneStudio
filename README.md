git clone https://github.com/yourusername/ml-finetuning-platform.git
cd ml-finetuning-platform
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Database configuration
export DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
├── .streamlit/          # Streamlit configuration
├── components/          # UI components
├── migrations/         # Database migrations
├── styles/            # Custom CSS styles
├── utils/             # Utility functions
└── app.py            # Main application file
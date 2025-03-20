import os

# Database Configuration
DATABASE_URI = "sqlite:///database/pharmacy.db"
SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key_here")

# ✅ Make sure this is set correctly
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your-real-api-key-here")

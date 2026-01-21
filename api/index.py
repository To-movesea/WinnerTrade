
from backend.app import app

# Vercel serverless function entry point
# It needs a callable named 'app'
# We import the existing Flask app from backend/app.py

if __name__ == '__main__':
    app.run()

import os
import logging
from datetime import timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from chatbot import analyze_symptoms

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("pharmacy-bot")

# Initialize Flask app
app = Flask(__name__, static_folder="static")

# Environment-based configuration
if os.environ.get("FLASK_ENV") == "production":
    # Production settings
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=1)
    )
    debug_mode = False
else:
    # Development settings
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev_secret_key_for_testing_only"),
        PERMANENT_SESSION_LIFETIME=timedelta(days=1)
    )
    debug_mode = True

# Initialize rate limiter to prevent abuse
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.before_request
def session_management():
    """Set session to permanent and update its lifetime"""
    session.permanent = True
    # Extend session on each request
    app.permanent_session_lifetime = app.config.get('PERMANENT_SESSION_LIFETIME')

@app.route('/')
def home():
    """Render the main chat interface"""
    # Clear chat history for new session if needed
    if request.args.get('reset'):
        if "chat_history" in session:
            del session["chat_history"]
        return redirect(url_for('home'))
    
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
@limiter.limit("15 per minute")  # Rate limit the chat endpoint
def chat():
    """Process chat messages and return Nova's response"""
    try:
        data = request.json
        user_input = data.get("message", "").strip()

        if not user_input:
            return jsonify({"response": "Nova: Please provide more details about your symptoms."})

        # Log incoming messages (excluding sensitive data)
        logger.info(f"Received message with length: {len(user_input)}")
        
        # Process the message through our chatbot
        response = analyze_symptoms(user_input)
        
        # Return the response
        return jsonify({"response": response})

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        return jsonify({
            "response": "Nova: I'm having technical difficulties at the moment. Please try again shortly or contact the pharmacy directly."
        }), 500

@app.route('/reset', methods=['POST'])
def reset_chat():
    """Reset the chat history"""
    if "chat_history" in session:
        del session["chat_history"]
    return jsonify({"status": "success", "message": "Chat history reset"})

@app.route('/health')
def health_check():
    """Simple health check endpoint for monitoring"""
    return jsonify({"status": "healthy"})

@app.errorhandler(429)
def ratelimit_handler(e):
    """Custom response for rate limited requests"""
    return jsonify({
        "response": "Nova: You've sent too many messages too quickly. Please wait a moment before trying again."
    }), 429

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(e)}", exc_info=True)
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting Pharmacy First Nova bot on {host}:{port}")
    app.run(debug=debug_mode, host=host, port=port)
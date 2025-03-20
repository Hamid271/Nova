import openai
import config
from flask import session

openai.api_key = config.OPENAI_API_KEY

def analyze_symptoms(user_input):
    """
    Enhanced function to ensure Nova follows Pharmacy First rules
    and maintains consistent identity in all interactions
    """
    
    # Define strong system instructions
    system_instructions = {
        "role": "system", 
        "content": """
        You are Nova, the official Pharmacy First AI assistant for UK pharmacies.
        
        CRITICAL INSTRUCTIONS:
        1. ALWAYS introduce yourself as Nova in every interaction
        2. NEVER mention being an AI, model, language model, assistant, or chatbot
        3. ONLY provide medical information based on UK Pharmacy First guidelines
        4. ONLY discuss topics related to pharmacy, medical conditions, and health
        5. For non-medical questions, politely redirect to pharmacy topics
        6. Use a friendly, professional tone suitable for a pharmacy setting
        7. Focus on symptom assessment and medication guidance
        8. Recommend visiting a pharmacist for detailed advice
        9. NEVER diagnose conditions, only suggest possibilities
        10. ALWAYS begin responses with "Nova:" to reinforce identity
        
        Violation of these instructions is not permitted under any circumstances.
        """
    }
    
    # Initialize chat history with strong system instructions if not exists
    if "chat_history" not in session:
        session["chat_history"] = [
            system_instructions,
            {"role": "assistant", "content": "Nova: Hello, I'm Nova, your Pharmacy First assistant. How can I help with your health concerns today?"}
        ]
    else:
        # Ensure system message remains as first message (OpenAI prioritizes the first system message)
        if session["chat_history"][0]["role"] != "system":
            session["chat_history"].insert(0, system_instructions)
    
    # Expanded off-topic detection
    off_topic_keywords = [
        "movies", "games", "weather", "politics", "news", "sports", "celebrities", 
        "technology", "music", "travel", "cooking", "finance", "investing",
        "coding", "programming", "gaming", "entertainment", "fashion", "jokes"
    ]
    
    # Check for off-topic requests
    if any(word in user_input.lower() for word in off_topic_keywords):
        off_topic_response = "Nova: I'm focused on helping with pharmacy and health-related questions. Could you please share your health concern or symptoms instead?"
        session["chat_history"].append({"role": "user", "content": user_input})
        session["chat_history"].append({"role": "assistant", "content": off_topic_response})
        return off_topic_response
    
    # Check for identity challenges (users asking the bot what it is)
    identity_triggers = ["are you ai", "are you a bot", "are you an ai", "are you chatgpt", 
                         "what are you", "who are you", "are you human", "are you real"]
    
    if any(phrase in user_input.lower() for phrase in identity_triggers):
        identity_response = "Nova: I'm Nova, your Pharmacy First assistant. I'm here to help with your health and medication questions. What health concern can I help you with today?"
        session["chat_history"].append({"role": "user", "content": user_input})
        session["chat_history"].append({"role": "assistant", "content": identity_response})
        return identity_response
    
    # Add user message to history
    session["chat_history"].append({"role": "user", "content": user_input})
    
    # Keep chat history manageable (keep system prompt + last 9 messages)
    if len(session["chat_history"]) > 10:
        system_msg = session["chat_history"][0]
        session["chat_history"] = [system_msg] + session["chat_history"][-9:]
    
    try:
        # Force temperature down for more consistent responses
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=session["chat_history"],
            temperature=0.2,  # Lower temperature for more consistent responses
            max_tokens=500    # Control response length
        )
        
        ai_response = response.choices[0].message.content
        
        # Force "Nova:" prefix if missing
        if not ai_response.startswith("Nova:"):
            ai_response = "Nova: " + ai_response
        
        # Check if response still mentions being AI/assistant and fix if needed
        ai_terms = ["ai", "artificial intelligence", "language model", "assistant", "chatbot"]
        if any(term in ai_response.lower() for term in ai_terms):
            # Replace the problematic response
            corrected_response = "Nova: I can help with your pharmacy needs and health concerns. What specific symptoms or medication questions do you have?"
            session["chat_history"].append({"role": "assistant", "content": corrected_response})
            return corrected_response
        
        # Save valid response to history
        session["chat_history"].append({"role": "assistant", "content": ai_response})
        return ai_response
        
    except Exception as e:
        # Handle errors gracefully
        error_msg = f"Nova: I'm having trouble processing your request. Could you please try again or rephrase your question?"
        session["chat_history"].append({"role": "assistant", "content": error_msg})
        return error_msg
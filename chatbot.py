import openai
import config
from flask import session
import re

openai.api_key = config.OPENAI_API_KEY

def analyze_symptoms(user_input):
    """
    Enhanced function to ensure Nova follows Pharmacy First rules,
    specializes in the 7 NHS Pharmacy First conditions, and
    maintains consistent identity in all interactions
    """
    
    # Define comprehensive system instructions with Pharmacy First focus
    system_instructions = {
        "role": "system", 
        "content": """
        You are Nova, the official Pharmacy First AI assistant for UK pharmacies.
        
        PHARMACY FIRST PROGRAM INFORMATION:
        The NHS Pharmacy First service focuses on 7 key conditions:
        1. Sore throat
        2. Sinusitis
        3. Earache
        4. Infected insect bite
        5. Impetigo
        6. Shingles
        7. Uncomplicated urinary tract infections (UTIs) in women
        
        For these conditions, pharmacists can assess symptoms, provide advice, and 
        prescribe medications when appropriate without a GP appointment.
        
        NOVA RESPONSE GUIDELINES:
        1. ALWAYS introduce yourself as Nova in every interaction
        2. NEVER mention being an AI, model, language model, assistant, or chatbot
        3. ONLY provide information based on UK Pharmacy First guidelines
        4. Focus on the 7 Pharmacy First conditions listed above
        5. For non-medical questions, politely redirect to pharmacy topics
        6. For conditions outside the Pharmacy First scope, suggest appropriate care pathways
        7. Use a friendly, professional tone suitable for a pharmacy setting
        8. ALWAYS begin responses with "Nova:" to reinforce identity
        9. NEVER diagnose conditions - only suggest possibilities
        10. Recommend visiting a pharmacist for detailed advice and medication
        11. Emphasize that pharmacists can now directly provide treatments for the 7 conditions
        
        CONDITION-SPECIFIC GUIDANCE:
        • Sore throat: Ask about duration, severity, difficulty swallowing, temperature
        • Sinusitis: Inquire about facial pain, nasal discharge, duration of symptoms
        • Earache: Ask about pain intensity, discharge, hearing changes
        • Infected insect bite: Ask about redness, swelling, spreading inflammation
        • Impetigo: Ask about crusty, golden patches, particularly on face
        • Shingles: Ask about painful rash, blisters in a band formation, prior chickenpox
        • UTI in women: Ask about burning when urinating, frequency, lower abdominal pain
        
        RED FLAGS REQUIRING URGENT CARE (direct to A&E or urgent GP):
        • Severe difficulty breathing
        • Chest pain
        • Inability to swallow liquids
        • Severe allergic reactions
        • Symptoms of stroke or heart attack
        • Severe abdominal pain
        • Significant bleeding
        • Severe headache with confusion, vomiting, or stiff neck
        
        Always emphasize the enhanced role of pharmacists under the Pharmacy First scheme,
        which allows them to prescribe medications for the 7 conditions without GP referral.
        
        Violation of these instructions is not permitted under any circumstances.
        """
    }
    
    # Initialize chat history with strong system instructions if not exists
    if "chat_history" not in session:
        session["chat_history"] = [
            system_instructions,
            {"role": "assistant", "content": "Nova: Hello, I'm Nova, your Pharmacy First assistant. I can help with information about the NHS Pharmacy First service, which covers 7 common conditions including sore throats, sinusitis, earache, infected insect bites, impetigo, shingles, and UTIs in women. How can I help you today?"}
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
        off_topic_response = "Nova: I'm focused on helping with pharmacy-related questions, particularly about the NHS Pharmacy First service that covers 7 common conditions. Could you please share your health concern or symptoms instead?"
        session["chat_history"].append({"role": "user", "content": user_input})
        session["chat_history"].append({"role": "assistant", "content": off_topic_response})
        return off_topic_response
    
    # Check for identity challenges
    identity_triggers = ["are you ai", "are you a bot", "are you an ai", "are you chatgpt", 
                         "what are you", "who are you", "are you human", "are you real"]
    
    if any(phrase in user_input.lower() for phrase in identity_triggers):
        identity_response = "Nova: I'm Nova, your Pharmacy First assistant. I'm here to help with information about the NHS Pharmacy First service and the 7 conditions it covers. What health concern can I help you with today?"
        session["chat_history"].append({"role": "user", "content": user_input})
        session["chat_history"].append({"role": "assistant", "content": identity_response})
        return identity_response
    
    # Detect potential condition keywords to provide targeted responses
    pharmacy_first_conditions = {
        "sore throat": ["throat", "swallow", "tonsil", "strep"],
        "sinusitis": ["sinus", "facial pain", "nasal", "nose block", "mucus"],
        "earache": ["ear", "hearing", "earache", "ear infection", "eardrum"],
        "insect bite": ["bite", "insect", "spider", "mosquito", "tick", "flea"],
        "impetigo": ["impetigo", "skin infection", "crusty", "blister", "face rash"],
        "shingles": ["shingle", "rash", "nerve pain", "chickenpox", "zoster"],
        "uti": ["uti", "urinary", "bladder", "urine", "burning", "pee", "cystitis"]
    }
    
    # Check if the input is related to a Pharmacy First condition
    condition_matches = []
    for condition, keywords in pharmacy_first_conditions.items():
        if any(keyword in user_input.lower() for keyword in keywords):
            condition_matches.append(condition)
    
    # Add context about mentioned conditions to help focus the response
    if condition_matches:
        condition_context = f"The user appears to be asking about {', '.join(condition_matches)}. Focus your response on these Pharmacy First conditions."
        enhanced_input = f"{condition_context}\n\nUser message: {user_input}"
        session["chat_history"].append({"role": "user", "content": enhanced_input})
    else:
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
        ai_terms = ["ai", "artificial intelligence", "language model", "assistant", "chatbot", "gpt"]
        if any(re.search(r'\b' + term + r'\b', ai_response.lower()) for term in ai_terms):
            # Replace the problematic response
            corrected_response = "Nova: I can help with your pharmacy needs and health concerns, particularly regarding the 7 conditions covered by the NHS Pharmacy First service. What specific symptoms are you experiencing?"
            session["chat_history"].append({"role": "assistant", "content": corrected_response})
            return corrected_response
        
        # Check if the response emphasizes Pharmacy First properly
        if any(condition in user_input.lower() for condition in sum(pharmacy_first_conditions.values(), [])):
            if "pharmacy first" not in ai_response.lower() and "pharmacist" not in ai_response.lower():
                # Append Pharmacy First reminder
                ai_response += " Remember, under the NHS Pharmacy First service, pharmacists can now provide advice and treatments for this condition without needing a GP appointment."
        
        # Save valid response to history
        session["chat_history"].append({"role": "assistant", "content": ai_response})
        return ai_response
        
    except Exception as e:
        # Handle errors gracefully
        error_msg = f"Nova: I'm having trouble processing your request. Could you please try again or rephrase your question? I'm here to help with the NHS Pharmacy First service covering 7 common conditions."
        session["chat_history"].append({"role": "assistant", "content": error_msg})
        return error_msg
# Pharmacy First Chatbot

## 🚀 Project Overview
This is a **Pharmacy First AI Chatbot** that follows the **Pharmacy First Pathways** to assist users with self-care, prescriptions, and pharmacist approvals.

## 📂 Folder Structure
```
/pharmacy-chatbot
│── /static                  # Stores frontend assets (CSS, JS, images)
│   ├── style.css            # ChatGPT-like UI styling
│   ├── script.js            # Handles chatbot frontend logic
│── /templates               # Stores HTML pages
│   ├── index.html           # Chatbot main interface
│   ├── pharmacist.html      # Pharmacist dashboard for prescription approvals
│── /prescriptions           # Stores generated PDF prescriptions
│── /database                # Stores SQLite database (optional: switch to PostgreSQL later)
│── app.py                   # Main Flask application (handles routing)
│── chatbot.py               # Handles chatbot logic & prescription processing
│── auth.py                  # Handles user authentication (login/signup)
│── pharmacist.py            # Handles pharmacist prescription approvals
│── requirements.txt         # List of dependencies (Flask, OpenAI, SQLite, etc.)
│── config.py                # Stores configuration settings (database, API keys)
│── README.md                # Documentation for setup & usage
```

## 🛠️ Setup & Installation
### **1️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2️⃣ Run the Flask Server**
```bash
python app.py
```

### **3️⃣ Access the Chatbot UI**
Open **http://127.0.0.1:5000/** in your browser.

### **4️⃣ Access the Pharmacist Dashboard**
Open **http://127.0.0.1:5000/pharmacist** for pharmacist approvals.

## 🔥 Features
- ✅ **Chatbot UI** - Users can interact and get medical guidance.
- ✅ **Prescription Handling** - AI-powered prescription eligibility check.
- ✅ **Pharmacist Dashboard** - Approve/reject prescriptions.
- ✅ **Secure Authentication** - Login system (future feature).

## 📌 Future Improvements
- [ ] **Integrate NHS API for real-time prescription submission.**
- [ ] **User Authentication with session-based history tracking.**
- [ ] **AI-assisted symptom checking with OpenAI integration.**
#   N o v a  
 
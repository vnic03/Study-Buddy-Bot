# Studdy-Buddy

Welcome to the WhatsApp Exam Helper Bot! This project aims to assist students in their exam preparation by providing a WhatsApp bot that generates questions on various topics and offers informative responses using artificial intelligence.

# Usage

**Interacting with the Bot:**
- Every 2 hours (deafult, changeable ofc !) the bot will send you a question on the topic you've selected
- Respond to the question by sending a message to the WhatsApp number associated with the Twilio Sandbox.
- The bot provides feedback on whether your answer is right or wrong.

## Features

- **Question Generation**: Automatically generates questions on different subjects, such as computer science, mathematics, and more.
- **Interactive Communication**: Engages users in interactive conversations via WhatsApp to provide answers and assistance.
- **Twilio Integration**: Utilizes the Twilio API to enable communication between the bot and users through WhatsApp messaging.
- **Flask Web Framework**: Implements the Flask framework to create the backend server for handling incoming messages and responses.
- **Ngrok for Local Development**: Utilizes Ngrok for local development to expose the Flask server to the internet, allowing Twilio to send and receive messages during testing.
- **OpenAI Integration**: Incorporates the OpenAI API to generate informative responses to user queries using state-of-the-art natural language processing models.

## Getting Started

1. **Installation**: Clone the repository and install the required dependencies listed in `requirements.txt`.
   
   ```bash
   git clone https://github.com/vnic03/Study-Buddy-Bot.git
   cd Study-Buddy-Bot
   pip install -r requirements.txt
   ```

# Configuration

1. **Obtain Twilio Credentials**: Obtain your Twilio Account SID and Auth Token. Similarly, acquire your OpenAI API key.
2. **Set Up .env File**: Create a `.env` file in the project root directory and populate it with your Twilio and OpenAI credentials.

```plaintext
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
OPENAI_API_KEY=your_openai_api_key
MY_WHATSAPP_NUMBER=whatsapp:+your_number
```

# Local Development

1. **Start Flask Server:** Launch the Flask server locally to handle incoming messages and responses.
2. **Expose Server with Ngrok:** Use Ngrok to expose the local server to the internet. This step is necessary for Twilio to communicate with your Flask application during testing.
3. **Configure Twilio WhatsApp Sandbox:** Set the Ngrok URL as the webhook endpoint in the Twilio WhatsApp Sandbox settings. This enables Twilio to forward WhatsApp messages to your Flask application.

# Deployment

1. **Deploy Application:** Deploy your application to your preferred hosting platform, ensuring that it supports running Flask applications.
2. **Update Webhook URL:** Once deployed, update the webhook URL in the Twilio console to point to your deployed application. This ensures that Twilio forwards incoming messages to the correct endpoint.






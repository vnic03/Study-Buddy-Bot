from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

from twilio.rest import Client
from openai import OpenAI

import schedule
import time
import random
from threading import Thread

from models import db, User
from helper import get_or_add_user, get_user_name, add_points, add_achievement


load_dotenv() #  Load environment variables from .env file

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID') # Your Account SID from twilio.com/console
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN') # Your Auth Token from twilio.com/console

twilio_phone_number = 'whatsapp:+14155238886' # make sure to use the right sandbox number  
my_whatsapp_number = os.getenv('MY_WHATSAPP_NUMBER')

openai_api_key = os.getenv('OPENAI_API_KEY') # Your OpenAI API key

twilio_client = Client(twilio_account_sid, twilio_auth_token) 

client = OpenAI(api_key=openai_api_key)


# Generate a question about computer science
def generate_question():

    response = client.completions.create(model = 'gpt-3.5-turbo', 
        prompt = "Ask a question about computer science", # basic prompt, change it to your needs
        temperature = 0.7,
        max_tokens = 100,
        top_p = 1.0,
        frequency_penalty = 0.0,
        presence_penalty = 0.0)
    
    return response.choices[0].text.strip()
    

# Send a message to a recipient
def send_message(question, recipient=my_whatsapp_number):
    message = twilio_client.messages.create(
        body=question,
        from_=twilio_phone_number,
        to=recipient
    )
    print(f"Message sent: {message.sid}")


# Send a question every 2 hours
def run_scheduler():

    def send_question():
        question = generate_question()
        send_message(question)
    
    schedule.every(2).hours.do(send_question) # Change the interval to your needs

    while True:
        schedule.run_pending()
        time.sleep(1)


# Generate a response to a user input
def generate_response(user_input, user_name="your name", retry_count=3):

    if user_input.lower() == 'test' or user_input.lower() == 'hi':
        return f"Hello {user_name}! How can I help you today?"

    initial_wait_time = 1 

    for i in range(retry_count):
        try:
            response = client.completions.create(
                model='gpt-3.5-turbo',
                prompt=f"A user asks: '{user_input}'\n\nAnswer politely and informatively:",
                temperature=0.7,
                max_tokens=150,
                top_p=1.0,
                frequency_penalty=0.5,
                presence_penalty=0.0,
                stop=["\n"]
            )

            return response.choices[0].text.strip()
            
        except Exception as e:
            print(f"Request failed, attempt {i + 1} of {retry_count}. Error: {e}")

            if i < retry_count - 1:  # Wait and retry
                wait_time = initial_wait_time + (2 ** i) + random.random()  # exponential backoff

                print(f"Wait {wait_time} seconds until next try...")

                time.sleep(wait_time)
            else:
                print("Maximum number of attempts reached, request failed.")

    return f"Mmh, something went wrong :/ Try again later, {user_name}."



# Handle user interaction with points and achievements
def handle_user_interaction(sender, points=10, achievement_threshold=100):

    current_points = add_points(sender, points)
    response_msg = f"You earned {points} points! You now have {current_points} points."

    if current_points >= achievement_threshold:
        achievement_name = "100 Points Club!"

        add_achievement(sender, achievement_name)

        response_msg += f" Congratulations, you've unlocked the '{achievement_name}' achievement!"
    
    return response_msg


def process_additional_message(sender, msg):

    user_name = get_user_name(sender)
    response_msg = generate_response(msg, user_name)

    return response_msg
        

# Prefix for the user's name
NAME_PREFIX = 'my name is '

# Webhook for incoming messages

@app.route('/webhook', methods=['POST']) 
def webhook():
    try:
        incoming_msg_original = request.values.get('Body', '')
        incoming_msg = incoming_msg_original.lower()
        sender = request.values.get('From') # The sender's phone number
        response_msg = "" 

        if incoming_msg.lower().startswith(NAME_PREFIX):
            user_name = incoming_msg_original[len(NAME_PREFIX):].strip()
            get_or_add_user(sender, user_name)
            response_msg += f"Nice to meet you, {user_name}!"

            additional_msg_index = len(NAME_PREFIX) + len(user_name)

            if len(incoming_msg) > additional_msg_index:

                additional_msg = incoming_msg_original[additional_msg_index:].strip()

                if additional_msg:
                    response_msg += " " + process_additional_message(sender, additional_msg)

            else:
                response_msg += " How can I help you today?"


            interaction_response = handle_user_interaction(sender)
            response_msg += " " + interaction_response
        else:
            user_name = get_user_name(sender)
            if not user_name:
                response_msg = "Please tell me your name by typing: 'My name is <your name>'."
            else:
                response_msg = generate_response(incoming_msg_original, user_name)

                interaction_response = handle_user_interaction(sender)
                response_msg += " " + interaction_response
                    

        send_message(response_msg, recipient=sender)
        return "OK", 200
    
    except Exception as e:
        print(f"Error in webhook: {e}")

        return "Error", 500


if __name__ == '__main__':

    # Creates the database tables
    with app.app_context():
        db.create_all()

    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.start()

    app.run(debug=True)
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

from twilio.rest import Client
from openai import OpenAI

import schedule
import time
import random
from threading import Thread


load_dotenv() #  Load environment variables from .env file

app = Flask(__name__)

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
def generate_response(user_input, retry_count=3):

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

    return "Mmh, something went wrong :/ Try again later."


# Webhook for incoming messages

@app.route('/webhook', methods=['POST']) 
def webhook():

    try:
        incoming_msg = request.values.get('Body', '').lower() 
        sender = request.values.get('From') # The sender's phone number

        response = generate_response(incoming_msg) 

        send_message(response, recipient=sender)
        return "OK", 200
    
    except Exception as e:
        print(f"Error in webhook: {e}")

        return "Error", 500


if __name__ == '__main__':
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.start()

    app.run(debug=True)
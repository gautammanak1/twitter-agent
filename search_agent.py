import json
import os
import sys
import logging
import requests
import time
from flask import Flask, request
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
from uuid import uuid4
import threading
from fetchai.communication import parse_message_from_agent, send_message_to_agent
GEMINI_API_KEY = ""
GEMINI_TEXT_URL = f""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

AGENTVERSE_KEY = os.environ.get('AGENTVERSE_KEY', "")
if AGENTVERSE_KEY == "":
    sys.exit("Environment variable AGENTVERSE_KEY not defined")

@app.route('/register', methods=['GET'])
def register():
    ai_identity = Identity.from_seed("search-agent-seed", 0)
    name = "search-agent"
    
    readme = """
    <description>My AI's description for generating AI trend tweets</description>
    <use_cases>
        <use_case>Generate and send AI trend tweets to Twitter Agent</use_case>
    </use_cases>
    """
    ai_webhook = os.environ.get('SEARCH_AGENT_WEBHOOK', "http://127.0.0.1:5002/webhook")
    
    try:
        register_with_agentverse(
            ai_identity,
            ai_webhook,
            AGENTVERSE_KEY,
            name,
            readme,
        )
        logger.info("Agent registration successful")
    except requests.exceptions.HTTPError as err:
        logger.error(f"Registration failed: {err}")
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
    
    return {"status": "Agent registration attempted"}
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    try:
        message = parse_message_from_agent(json.dumps(data))
        logger.info(f"Webhook received from {message.sender}: {message.payload}")
    except ValueError as e:
        logger.error(f"Error parsing message: {e}")
        return {"status": f"error: {e}"}
    
    return {"status": "Message processed"}

def wait_for_server(port):
    while True:
        try:
            response = requests.get(f'http://127.0.0.1:{port}')
            if response.status_code == 200:
                return  
        except requests.ConnectionError:
            logger.info(f"Waiting for server on port {port} to start...")
            time.sleep(1)  

def generate_and_send_content():

    wait_for_server(5001)  
    
    while True:
        try:
            query = "Generate a tweet about the latest AI trends."
            text_payload = {
                "contents": [{"parts": [{"text": query}]}]
            }
            headers = {"Content-Type": "application/json"}
            text_response = requests.post(GEMINI_TEXT_URL, json=text_payload, headers=headers)
            text_response_json = text_response.json()

            if "candidates" in text_response_json:
                tweet_content = text_response_json["candidates"][0]["content"]["parts"][0]["text"]
                logger.info(f"Generated tweet content: {tweet_content}")
                webhook_url = os.environ.get('TWITTER_AGENT_WEBHOOK', "http://127.0.0.1:5001/webhook")
                logger.info(f"Attempting to send to Twitter Agent at {webhook_url}")
                sender_identity = Identity.from_seed("search-agent-seed", 0)
                target_identity = Identity.from_seed("twitter-agent-seed", 0)  
                
                envelope = {
                    "version": "1.0",
                    "sender": sender_identity.address,
                    "target": target_identity.address,
                    "session": str(uuid4()),
                    "schema_digest": "",  
                    "payload": {
                        "tweet_content": tweet_content[:280]
                    }
                }
                response = requests.post(webhook_url, json=envelope, headers=headers)
                
                if response.status_code == 200:
                    logger.info(f"Content sent successfully to Twitter Agent")
                else:
                    logger.error(f"Failed to send content to Twitter Agent. Status code: {response.status_code}")
            else:
                logger.error("Failed to generate text content from Gemini API")
        
        except Exception as e:
            logger.error(f"Error in generate_and_send_content: {e}")
        
        time.sleep(60)  

if __name__ == "__main__":
    content_thread = threading.Thread(target=generate_and_send_content)
    content_thread.daemon = True 
    content_thread.start()

    app.run(host='0.0.0.0', port=5002, debug=True)

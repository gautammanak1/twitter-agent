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
        payload = json.loads(data.get('payload', "{}"))  # Parse payload as JSON
        if payload.get("type") == "content_generated":
            tweet_content = payload.get("content")
            if tweet_content:
                logger.info(f"Received generated content: {tweet_content}")
                send_to_twitter_agent(tweet_content)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding payload JSON: {e}")
        return {"status": f"error: {e}"}
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return {"status": f"error: {e}"}
    
    return {"status": "Message processed"}

def send_to_twitter_agent(content):
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
        "payload": json.dumps({  
            "tweet_content": content[:280]
        })
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(webhook_url, json=envelope, headers=headers)
    
    if response.status_code == 200:
        logger.info(f"Content sent successfully to Twitter Agent")
    else:
        logger.error(f"Failed to send content to Twitter Agent. Status code: {response.status_code}")

def send_to_content_generation_agent(query):
    webhook_url = os.environ.get('CONTENT_GENERATION_AGENT_WEBHOOK', "http://127.0.0.1:5003/webhook")
    logger.info(f"Attempting to send to Content Generation Agent at {webhook_url}")
    sender_identity = Identity.from_seed("search-agent-seed", 0)
    target_identity = Identity.from_seed("content-generation-agent-seed", 0)  
    
    envelope = {
        "version": "1.0",
        "sender": sender_identity.address,
        "target": target_identity.address,
        "session": str(uuid4()),
        "schema_digest": "",  
        "payload": json.dumps({  # Convert payload to JSON string
            "query": query
        })
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(webhook_url, json=envelope, headers=headers)
    
    if response.status_code == 200:
        logger.info(f"Query sent successfully to Content Generation Agent")
    else:
        logger.error(f"Failed to send query to Content Generation Agent. Status code: {response.status_code}")

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
            send_to_content_generation_agent(query)
        except Exception as e:
            logger.error(f"Error in generate_and_send_content: {e}")
        
        time.sleep(60)  

if __name__ == "__main__":
    content_thread = threading.Thread(target=generate_and_send_content)
    content_thread.daemon = True 
    content_thread.start()

    app.run(host='0.0.0.0', port=5002, debug=True)
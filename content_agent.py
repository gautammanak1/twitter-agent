import json
import os
import sys
import logging
import requests
from flask import Flask, request
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
from uuid import uuid4

GEMINI_API_KEY = "AIzaSyDxxSzqkL24eW3nSCjNyyM9CaydBtBqfTA"
GEMINI_TEXT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

AGENTVERSE_KEY = os.environ.get('AGENTVERSE_KEY', "")
if AGENTVERSE_KEY == "":
    sys.exit("Environment variable AGENTVERSE_KEY not defined")

@app.route('/register', methods=['GET'])
def register():
    ai_identity = Identity.from_seed("content-generation-agent-seed", 0)
    name = "content-generation-agent"
    
    readme = """
    <description>My AI's description for generating content</description>
    <use_cases>
        <use_case>Generate content based on queries</use_case>
    </use_cases>
    """
    ai_webhook = os.environ.get('CONTENT_GENERATION_AGENT_WEBHOOK', "http://127.0.0.1:5003/webhook")
    
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
        query = payload.get("query", "")
        if query:
            logger.info(f"Received query: {query}")
            generated_content = generate_content(query)
            if generated_content:
                send_to_search_agent(generated_content)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding payload JSON: {e}")
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
    
    return {"status": "Message processed"}

def generate_content(query):
    text_payload = {
        "contents": [{"parts": [{"text": query}]}]
    }
    headers = {"Content-Type": "application/json"}
    text_response = requests.post(GEMINI_TEXT_URL, json=text_payload, headers=headers)
    text_response_json = text_response.json()

    if "candidates" in text_response_json:
        content = text_response_json["candidates"][0]["content"]["parts"][0]["text"]
        logger.info(f"Generated content: {content}")
        return content
    else:
        logger.error("Failed to generate content from Gemini API")
        return None

def send_to_search_agent(content):
    webhook_url = os.environ.get('SEARCH_AGENT_WEBHOOK', "http://127.0.0.1:5002/webhook")
    logger.info(f"Attempting to send to Search Agent at {webhook_url}")
    sender_identity = Identity.from_seed("content-generation-agent-seed", 0)
    target_identity = Identity.from_seed("search-agent-seed", 0)  
    
    envelope = {
        "version": "1.0",
        "sender": sender_identity.address,
        "target": target_identity.address,
        "session": str(uuid4()),
        "schema_digest": "",  
        "payload": json.dumps({  # Convert payload to JSON string
            "type": "content_generated",
            "content": content
        })
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(webhook_url, json=envelope, headers=headers)
    
    if response.status_code == 200:
        logger.info(f"Content sent successfully to Search Agent")
    else:
        logger.error(f"Failed to send content to Search Agent. Status code: {response.status_code}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5003, debug=True)
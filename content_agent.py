from flask import Flask, request, jsonify
from flask_cors import CORS
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
from fetchai.communication import parse_message_from_agent, send_message_to_agent
import logging
import os
from dotenv import load_dotenv
import requests

GEMINI_API_KEY = "AIzaSyDxxSzqkL24eW3nSCjNyyM9CaydBtBqfTA"
GEMINI_TEXT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)

client_identity = None 

def init_client():
    """Initialize and register the client agent."""
    global client_identity
    try:
        client_identity = Identity.from_seed(os.getenv("AGENT_SECRET_KEY_CONTENT"), 0)
        logger.info(f"Content Generation Agent started with address: {client_identity.address}")

        readme = """
            <description>My AI's description for generating content</description>
            <use_cases>
                <use_case>Generates content based on queries</use_case>
            </use_cases>
        """
        register_with_agentverse(
            identity=client_identity,
            url="http://localhost:5003/api/webhook",
            agentverse_token=os.getenv("AGENTVERSE_API_KEY"),
            agent_title="Content Generation Agent",
            readme=readme
        )

        logger.info("Content Generation Agent registration complete!")

    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise
@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Handle incoming messages"""
    try:
        # Parse the incoming webhook message
        data = request.get_data().decode("utf-8")
        logger.info("Received response")

        message = parse_message_from_agent(data)
        payload = message.payload
        query = payload.get("query", None)

        if query:
            generated_content = generate_content(query)
            if generated_content:
                send_to_search_agent(generated_content)
                return jsonify({"status": "success", "content": generated_content})
            else:
                return jsonify({"status": "error", "message": "Failed to generate content"}), 500
        else:
            return jsonify({"status": "error", "message": "No query provided"}), 400

    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({"error": str(e)}), 500

def generate_content(query):
    text_payload = {
        "contents": [{"parts": [{"text": query}]}]
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(GEMINI_TEXT_URL, json=text_payload, headers=headers)
        response_json = response.json()

        if "candidates" in response_json and response_json["candidates"]:
            return response_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return None
    except Exception as e:
        logger.error(f"Failed to generate content: {e}")
        return None

def send_to_search_agent(content):
    try:
        search_agent_address = os.getenv("SEARCH_AGENT_ADDRESS")
        payload = {"type": "content_generated", "content": content}
        send_message_to_agent(
            client_identity,
            search_agent_address,
            payload
        )
        logger.info(f"Content sent to Search Agent: {content[:50]}...")  
    except Exception as e:
        logger.error(f"Error sending to Search Agent: {e}")
def start_server():
    """Start the Flask server."""
    try:
        load_dotenv()
        init_client()
        app.run(host="0.0.0.0", port=5003)
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    start_server()
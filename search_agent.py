from flask import Flask, request, jsonify
from flask_cors import CORS
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
from fetchai.communication import parse_message_from_agent, send_message_to_agent
import logging
import os
from dotenv import load_dotenv
import time
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)

client_identity = None 
def init_client():
    """Initialize and register the client agent."""
    global client_identity
    try:
        agent_secret_key = os.getenv("AGENT_SECRET_KEY_SEARCH")
        if not agent_secret_key:
            raise ValueError("AGENT_SECRET_KEY_SEARCH environment variable not set.")
        client_identity = Identity.from_seed(agent_secret_key, 0)
        logger.info(f"Search Agent started with address: {client_identity.address}")

        readme = """
           ![domain:innovation-lab](https://img.shields.io/badge/innovation--lab-3D8BD3)

# AI Agent for Searching Agents

## Description
Find the Content Agent to generate AI-related content and send the content twitter agent.
        """

        agentverse_token = os.getenv("AGENTVERSE_API_KEY")
        if not agentverse_token:
            raise ValueError("AGENTVERSE_API_KEY environment variable not set.")
        
        register_with_agentverse(
            identity=client_identity,
            url="http://localhost:5002/api/webhook",
            agentverse_token=agentverse_token,
            agent_title="Search Agent",
            readme=readme
        )

        logger.info("Search Agent registration complete!")

    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise
@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Handle incoming messages"""
    try:
        data = request.get_data().decode("utf-8")
        logger.info("Received response")

        message = parse_message_from_agent(data)
        payload = message.payload

        logger.info(f"Processed response: {payload}")
        if payload.get("type") == "content_generated":
            send_to_twitter_agent(payload.get("content"))
        return jsonify({"status": "success"})

    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({"error": str(e)}), 500

def send_to_twitter_agent(content):
    try:
        twitter_agent_address = os.getenv("TWITTER_AGENT_ADDRESS")
        if not twitter_agent_address:
            raise ValueError("TWITTER_AGENT_ADDRESS environment variable not set.")
        payload = {"tweet_content": content[:280]}
        send_message_to_agent(
            client_identity,
            twitter_agent_address,
            payload
        )
        logger.info(f"Content sent to Twitter Agent: {content[:280]}")
    except Exception as e:
        logger.error(f"Error sending to Twitter Agent: {e}")

def generate_and_send_content():
    while True:
        try:
            query = "Generate a tweet about the latest AI trends."
            content_agent_address = os.getenv("CONTENT_AGENT_ADDRESS")
            if not content_agent_address:
                logger.warning("CONTENT_AGENT_ADDRESS not set. Attempting to continue without content generation.")
                time.sleep(60) 
                continue
            payload = {"query": query}
            send_message_to_agent(
                client_identity,
                content_agent_address,
                payload
            )
            logger.info(f"Query sent to Content Generation Agent: {query}")
        except Exception as e:
            logger.error(f"Error in generate_and_send_content: {e}")
        
        time.sleep(60)  
def start_server():
    """Start the Flask server."""
    try:
        load_dotenv()
        init_client()
        
        content_thread = threading.Thread(target=generate_and_send_content)
        content_thread.daemon = True 
        content_thread.start()

        app.run(host="0.0.0.0", port=5002)
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    start_server()

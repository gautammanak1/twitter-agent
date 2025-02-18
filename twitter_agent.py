from flask import Flask, request, jsonify
from flask_cors import CORS
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
from fetchai.communication import parse_message_from_agent
import logging
import os
from dotenv import load_dotenv
import tweepy


CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)
client_identity = None 

# Function to register agent
def init_client():
    """Initialize and register the client agent."""
    global client_identity
    try:
        client_identity = Identity.from_seed(os.getenv("AGENT_SECRET_KEY_TWITTER"), 0)
        logger.info(f"Twitter Agent started with address: {client_identity.address}")

        readme = """
![Innovation Lab](https://img.shields.io/badge/innovation--lab-3D8BD3)
## Description
My AI's description for posting to Twitter.

## Use Cases
- Automatically posts content to Twitter.
        """

        # Register the agent with Agentverse
        register_with_agentverse(
            identity=client_identity,
            url="http://localhost:5001/api/webhook",
            agentverse_token=os.getenv("AGENTVERSE_API_KEY"),
            agent_title="Twitter Agent",
            readme=readme
        )

        logger.info("Twitter Agent registration complete!")

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
        tweet_content = payload.get("tweet_content", None)

        if tweet_content:
            response = client.create_tweet(text=tweet_content)
            if response.data:
                tweet_id = response.data['id']
                logger.info(f"Tweet posted successfully! Tweet ID: {tweet_id}")
                return jsonify({"status": "success", "tweet_id": tweet_id})
            else:
                logger.error("Failed to post tweet: No response data.")
                return jsonify({"status": "error", "message": "Failed to post tweet"}), 500
        else:
            return jsonify({"status": "error", "message": "No tweet content provided"}), 400

    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({"error": str(e)}), 500
def start_server():
    """Start the Flask server."""
    try:
        load_dotenv()
        init_client()
        app.run(host="0.0.0.0", port=5001)
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    start_server()

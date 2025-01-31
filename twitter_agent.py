import json
import os
import sys
import logging
from flask import Flask, request
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
from uuid import uuid4
import requests
import tweepy

# Twitter API credentials
CONSUMER_KEY = "7jb9bVEhPPGdJ5uiHXQ1BSqRW"
CONSUMER_SECRET = "r8VsJ9vNZAP5w6SyPAwMB0gPiMlmbxsKoE9x1W2en4gSh2x9BW"
ACCESS_TOKEN = "1724444645399158784-NMEuCX2c8eSznB4UTxJMwxujxZp9Vj"
ACCESS_TOKEN_SECRET = "9O9lX6tinqrxuw5Qj5NAStwB3rMSlWcR7WGMgp1ePUPhJ"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

app = Flask(__name__)

AGENTVERSE_KEY = os.environ.get('AGENTVERSE_KEY', "")
if AGENTVERSE_KEY == "":
    sys.exit("Environment variable AGENTVERSE_KEY not defined")

@app.route('/')
def root():
    logger.info(f"Root path accessed from {request.remote_addr}")
    return {"status": "Twitter Agent is running"}, 200

@app.route('/register', methods=['GET'])
def register():
    ai_identity = Identity.from_seed("twitter-agent-seed", 0)
    name = "twitter-agent"
    
    readme = """
    <description>My AI's description for posting tweets</description>
    <use_cases>
        <use_case>Automatically posts tweets received from Search Agent</use_case>
    </use_cases>
    """

    ai_webhook = os.environ.get('TWITTER_AGENT_WEBHOOK', "http://127.0.0.1:5001/webhook")
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
        tweet_content = payload.get('tweet_content', None)
        
        if tweet_content:
            logger.debug(f"Received tweet content for review: {tweet_content}")
            response = client.create_tweet(text=tweet_content)
            
            if response.data:
                tweet_id = response.data['id']
                logger.info(f"Tweet posted successfully! Tweet ID: {tweet_id}")
            else:
                logger.error("Failed to post tweet: No response data.")
        else:
            logger.error("No tweet content in received data.")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding payload JSON: {e}")
    except Exception as e:
        logger.error(f"Error posting tweet: {e}")
    
    return {"status": "Twitter Agent message processed"}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
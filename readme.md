# AI Tweet Generator and Poster

## Overview
This project comprises two Flask-based agents:
- **Search Agent**: Generates content about AI trends using Google's Gemini API.
- **Twitter Agent**: Posts the generated content to Twitter using the Twitter API.

## Project Structure
- `search_agent.py`: Contains the logic for generating and sending tweet content.
- `twitter_agent.py`: Handles receiving and posting tweets on Twitter.

## Prerequisites
- Python 3.8+
- Flask
- Fetch.ai library for agent communication
- Tweepy for Twitter API interactions
- `requests` for HTTP requests
- An API key for Google's Gemini service
- Twitter Developer account for API credentials

## Installation

### Setup Environment
1. **Clone the repository**:
   ```bash
   git clone https://github.com/gautammanak1/twitter-agent
   cd twitter-agent
   ```

2. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install Flask fetchai tweepy requests
   ```

### Configuration
#### Environment Variables:
- `AGENTVERSE_KEY`: Your key for agentverse registration.
- `TWITTER_AGENT_WEBHOOK`: URL of the Twitter Agent for the Search Agent to send content to.
- `SEARCH_AGENT_WEBHOOK`: URL of the Search Agent for any potential interactions (not used in current setup).

Set these in your environment or in a `.env` file:
```bash
export AGENTVERSE_KEY="your-agentverse-key"
export TWITTER_AGENT_WEBHOOK="http://127.0.0.1:5001/webhook"
export SEARCH_AGENT_WEBHOOK="http://127.0.0.1:5002/webhook"
```

#### API Keys:
- **Twitter API Credentials**: Replace the placeholder values in `twitter_agent.py` with your actual Twitter API credentials.
- **Gemini API Key**: Replace the placeholder `GEMINI_API_KEY` in `search_agent.py` with your actual API key.

## Running the Agents

### Search Agent
Start the search agent:
```bash
python search_agent.py
```
This will start a server on port `5002` and begin generating tweets about AI trends every 60 seconds, sending them to the Twitter Agent.

### Twitter Agent
Start the Twitter agent:
```bash
python twitter_agent.py
```
This will start a server on port `5001`, waiting for the Search Agent to send content, which it will then post to Twitter.

## How It Works
### Search Agent:
- Uses Gemini API to generate text about AI trends.
- Sends this content to the Twitter Agent via HTTP POST every minute.

### Twitter Agent:
- Listens for incoming content from the Search Agent.
- Once received, it uses the Tweepy library to post this content as a tweet on Twitter.

## Future Scope
- **Image Generation**: Integrate image generation services like DALL-E or Google's Imagen to add visuals to tweets.
- **Enhanced Tweet Curation**: Categorize, filter, or moderate content before posting to ensure quality and relevance.
- **User Interaction**: Allow user input or feedback to customize tweet topics.
- **Multi-Platform Support**: Extend the Twitter Agent to post on LinkedIn, Instagram, or Mastodon.
- **Scheduled Posts**: Implement a scheduling system for optimal posting times.
- **Sentiment Analysis**: Analyze sentiment to adjust tweet strategy.
- **Agent Interaction**: Add more agents for trend monitoring, user interactions, or content generation.

## Contributions
Pull requests are welcome. For major changes, please open an issue first to discuss modifications.
Ensure that tests are updated as appropriate.


## Contact
For issues or inquiries, reach out via [https://gautammanaktech.vercel.app/].

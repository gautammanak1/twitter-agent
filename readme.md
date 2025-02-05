### Automating AI Trend Tweets with Fetch.ai, Gemini API & Twitter API

### Introduction

Imagine an AI system that automatically tweets about the latest AI trends without human intervention! This project does exactly that using **Fetch.ai SDK, Google’s Gemini API, and Twitter API**. It consists of three smart agents working together in an automated and efficient manner.

### How It Works

The system is powered by three agents:

1.  **Search Agent** — Finds the Content Agent to generate AI-related content.
    
2.  **Content Agent** — Uses Google’s Gemini API to create engaging AI trend content.
    
3.  **Twitter Agent** — Receives the content and posts it on Twitter.
    

### Step-by-Step Process:

*   The **Search Agent** starts by locating the **Content Agent**, sends a request, and receives the generated content.
    
*   Then, the **Search Agent** finds the **Twitter Agent** and forwards the content.
    
*   The **Twitter Agent** posts the content on Twitter and returns the tweet ID.
    

All agents communicate using **multi-threading**, making the system efficient and fast.

### **Technologies Used**

*   **Fetch.ai SDK** — Enables agent-based automation.
    
*   **Google Gemini API** — Generates AI-related content.
    
*   **Twitter API** — Posts tweets automatically.
    
*   **uAgents Framework** — Simplifies AI agent interactions.
    

### Project Links

*   **GitHub Repository**: [Twitter Agent Project](https://github.com/gautammanak1/twitter-agent)
    
*   **Twitter API Docs**: [Twitter API](https://developer.x.com/en/docs/x-api)
    
*   **Google Gemini API**: [Gemini API](https://aistudio.google.com/welcome)
    
*   **Fetch.ai SDK Docs**: [Fetch.ai SDK Quickstart](https://fetch.ai/docs/guides/fetchai-sdk/quickstart)
    

### How to Run the Project

Follow these steps to set up and run the agents:

1.  Clone the repository:
    
`   git clone https://github.com/gautammanak1/twitter-agent.git cd twitter-agent   `

2.Install dependencies:

`   pip install -r requirements.txt   `

3 Run the agents:

`python3 search_agent.py
python3 content_agent.py
python3 twitter_agent.py   `

4 .env

`AGENTVERSE_API_KEY=
AGENT_SECRET_KEY_SEARCH= 
AGENT_SECRET_KEY_CONTENT=
AGENT_SECRET_KEY_TWITTER=
CONTENT_AGENT_ADDRESS= 
SEARCH_AGENT_ADDRESS=
TWITTER_AGENT_ADDRESS=
GEMINI_API_KEY = 
GEMINI_TEXT_URL =   `


Once running, the system will continuously generate and post AI-related tweets automatically!

### Future Enhancements

*   **Sentiment Analysis**: Generate content based on trending emotions.
    
*   **Tweet Scheduling**: Post tweets at optimized times.
    
*   **Better Error Handling**: Improve debugging and monitoring.
    

### Conclusion

This project showcases the power of AI-driven automation using **Fetch.ai SDK**. By integrating AI agents, multi-threading, and real-time content generation, it creates a seamless system for AI trend updates on Twitter. Try it out and let your AI agent tweet for you!

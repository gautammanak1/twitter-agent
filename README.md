# Twitter Agent

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Fetch.ai](https://img.shields.io/badge/Fetch.ai-uAgents-000000)](https://fetch.ai/)

AI-powered tweet generation and posting agent built with Fetch.ai uAgents. Generates contextual tweets using AI content generation and posts them via the Twitter API through Composio integration.

## Features

- **AI Content Generation** — Generates engaging tweets based on topics or prompts
- **Twitter Integration** — Posts tweets directly via Composio's Twitter tools
- **Search & Trend Analysis** — Searches Twitter for trending topics and relevant content
- **uAgent Protocol** — Operates as an autonomous agent on the Fetch.ai network

## Components

| File | Purpose |
|------|---------|
| `content_agent.py` | AI-powered content generation for tweets |
| `twitter_agent.py` | Twitter API integration and posting |
| `search_agent.py` | Twitter search and trend discovery |

## Setup

```bash
pip install uagents composio-openai openai python-dotenv
```

### Environment Variables

```bash
export OPENAI_API_KEY="your-openai-key"
export COMPOSIO_API_KEY="your-composio-key"
```

## Usage

```bash
python twitter_agent.py
```

The agent accepts text prompts, generates tweet content using AI, and posts to Twitter through Composio's authenticated connection.

## Project Structure

```
twitter-agent/
├── content_agent.py    # AI content generation
├── twitter_agent.py    # Twitter posting agent
├── search_agent.py     # Twitter search agent
└── readme.md
```

## License

MIT

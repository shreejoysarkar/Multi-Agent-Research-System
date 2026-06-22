# 🔬 Multi-Agent Research System

<div align="center">

**A fully autonomous AI research pipeline that searches, scrapes, writes, and critiques — so you don't have to.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-Framework-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-FF6F00?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036?style=for-the-badge)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)

</div>

---

## 📖 Overview

The **Multi-Agent Research System** is an end-to-end AI pipeline that automates the entire research workflow — from discovering sources on the web to delivering a polished, peer-reviewed article. It uses a team of specialised AI agents, each with a distinct role, orchestrated through a fault-tolerant pipeline with real-time progress tracking.

Enter a topic, and the system will:

1. **Search** the web for the most recent and relevant sources.
2. **Scrape** full article content from discovered URLs.
3. **Write** a comprehensive, citation-rich article from the raw research.
4. **Critique** the article with detailed peer-review feedback.

All of this is accessible through a sleek **Streamlit dashboard** or via the **command line**.

### 🌐 Live Demo

👉 **[Try it now — Multi-Agent Research System](https://multi-agent-research-system-3nlmuwwn7nucj5eyisjzcr.streamlit.app/)**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI (app.py)                  │
│           Real-time progress  ·  Tabbed results             │
└────────────────────────┬────────────────────────────────────┘
                         │  on_status callback
┌────────────────────────▼────────────────────────────────────┐
│                  Pipeline (pipeline.py)                      │
│         Orchestration  ·  Retry logic  ·  Fallbacks         │
└──┬──────────┬──────────────┬──────────────┬─────────────────┘
   │          │              │              │
   ▼          ▼              ▼              ▼
┌──────┐  ┌────────┐   ┌────────┐    ┌─────────┐
│Search│  │Research│   │ Writer │    │ Critic  │
│Agent │  │ Agent  │   │ Chain  │    │ Chain   │
└──┬───┘  └───┬────┘   └────────┘    └─────────┘
   │          │
   ▼          ▼
┌──────┐  ┌────────┐
│Tavily│  │  BS4   │
│Search│  │Scraper │
└──────┘  └────────┘
```

| Agent | Role | Powered By |
|-------|------|------------|
| **Search Agent** | Discovers relevant, recent sources via web search | Tavily API + LangGraph |
| **Research Agent** | Scrapes and extracts full article content from URLs | BeautifulSoup4 + LangGraph |
| **Writer Agent** | Synthesises raw research into a polished, cited article | Groq LLM (Llama 3.3 70B) |
| **Critic Agent** | Peer-reviews the article for accuracy, structure & completeness | Groq LLM (Llama 3.3 70B) |

---

## ✨ Key Features

- **Fully Autonomous** — Enter a topic and receive a complete research article with zero manual intervention.
- **Fault-Tolerant Pipeline** — Built-in retry logic with exponential backoff and direct-scraping fallback for unreliable LLM tool calls.
- **Multi-Source URL Extraction** — Parses URLs from all agent messages (including tool-call results), not just the final AI summary.
- **Real-Time Progress Tracking** — Live 4-stage pipeline tracker with status badges in the Streamlit UI.
- **Tabbed Results Dashboard** — View the article, critic feedback, source URLs, and raw data in separate tabs.
- **One-Click Export** — Download the generated article as a Markdown file.
- **Dual Interface** — Use the Streamlit web UI or run directly from the command line.

---

## 📂 Project Structure

```
Multi-Agent-Research-System/
├── app.py                 # Streamlit web UI
├── pipeline.py            # Pipeline orchestration (4-stage workflow)
├── agent.py               # Agent & chain definitions (search, research, writer, critic)
├── tools.py               # LangChain tools (Tavily web search, BeautifulSoup scraper)
├── config.py              # Pydantic settings (env var management)
├── main.py                # CLI entry point
├── assets/
│   └── hero_banner.png    # UI banner image
├── .env                   # API keys (not committed)
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project metadata
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** (recommended) or `pip`
- API keys for:
  - [**Groq**](https://console.groq.com/) — LLM inference (Llama 3.3 70B)
  - [**Tavily**](https://tavily.com/) — Web search API

### 1. Clone the Repository

```bash
git clone https://github.com/shreejoysarkar/Multi-Agent-Research-System.git
cd Multi-Agent-Research-System
```

### 2. Create & Activate Virtual Environment

```bash
uv venv Research_System --python 3.11
```

**Windows:**
```bash
Research_System\Scripts\activate
```

**macOS / Linux:**
```bash
source Research_System/bin/activate
```

### 3. Install Dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 5. Run the Application

**Streamlit UI (recommended):**
```bash
streamlit run app.py
```

**Command Line:**
```bash
python pipeline.py "Latest breakthroughs in quantum computing 2026"
```

Or run interactively:
```bash
python pipeline.py
# Enter your research topic: <your topic>
```

---

## 🖥️ Usage

### Streamlit Dashboard

1. Launch the app with `streamlit run app.py`.
2. Enter your research topic in the text area.
3. Click **🚀 Start Research** and watch the 4-stage pipeline execute in real time.
4. Explore results across four tabs:
   - **📝 Article** — The generated research article with inline citations.
   - **🔬 Critique** — Detailed peer-review feedback with a quality score.
   - **🔗 Sources** — List of all discovered source URLs.
   - **📦 Raw Data** — Expandable search results and scraped content.
5. Download the final article as a `.md` file with one click.

### CLI Mode

```bash
python pipeline.py "Impact of generative AI on healthcare in 2026"
```

The pipeline will print progress updates to the console and output the final article and critic feedback.

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Language** | Python 3.11 |
| **LLM** | Llama 3.3 70B via Groq |
| **Agent Framework** | LangChain + LangGraph |
| **Web Search** | Tavily API |
| **Web Scraping** | BeautifulSoup4, Requests |
| **Configuration** | Pydantic Settings, python-dotenv |
| **Frontend** | Streamlit |
| **Package Manager** | uv |

---

## 🔧 Configuration

All configuration is managed through environment variables using **Pydantic Settings**. The `.env` file is loaded automatically at startup.

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for LLM inference | ✅ |
| `TAVILY_API_KEY` | Tavily API key for web search | ✅ |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <p>Built with ❤️ using LangChain · LangGraph · Groq · Streamlit</p>
</div>

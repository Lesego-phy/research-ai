# 🔍 AI-Powered Research System

An enterprise-grade multi-agent AI system that autonomously researches topics, drafts reports, self-corrects via a reviewer agent, and exports citation-backed documents — with human approval before publication.

![CI](https://github.com/Lesego-phy/research-ai/actions/workflows/ci.yml/badge.svg)
![CD](https://github.com/Lesego-phy/research-ai/actions/workflows/cd-azure.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## Overview

This system orchestrates three specialized AI agents (Researcher, Writer, Reviewer) through a LangGraph state machine to produce high-quality research reports. The Researcher agent draws from three complementary knowledge sources: real-time web search, private document context via RAG, and peer-reviewed academic literature via MCP — giving reports both breadth and academic credibility.

**Key Features:**
 **Multi-Agent Orchestration** — LangGraph state machine with conditional routing and bounded revision loops
 **Multi-Source Research** — Tavily (web), ChromaDB (RAG), OpenAlex (academic papers via MCP)
 **Defense-in-Depth Safety** — Input/output guardrails, PII anonymization, prompt injection detection
 **Parallelized Execution** — 4-5× faster web scraping via ThreadPoolExecutor
 **Human-in-the-Loop** — Draft review and approval before export
 **Multi-Format Export** — PDF, Word, and Markdown with proper citations
 **Extensible via MCP** — Plug-and-play integration with external knowledge sources
 **Full Observability** — LangSmith distributed tracing and cost monitoring
 **Production-Ready** — Dockerized with GitHub Actions CI/CD to Azure Container Apps

---
## 🛠️ Tech Stack

**Core:**
- Python 3.10+
- LangGraph (State machine orchestration)
- LangChain (Agent framework)
- Azure OpenAI (LLM backend)

**Data & Search:**
- Tavily (Web search API)
- ChromaDB (Vector database for RAG)
- OpenAlex (Academic literature via MCP)
- BeautifulSoup (Web scraping)

**Safety & Observability:**
- Microsoft Presidio (PII detection/anonymization)
- LangSmith (Distributed tracing)
- Custom guardrails (Input/output validation, rate limiting)

**Frontend & Deployment:**
- Streamlit (Web UI)
- Docker (Containerization)
- GitHub Actions (CI/CD)
- Azure Container Apps (Production deployment)

---

## Quick Start

### Prerequisites

- Python 3.10+
- Azure OpenAI API access
- Tavily API key ([Get one free](https://tavily.com))
- LangSmith API key ([Sign up](https://smith.langchain.com))

### Installation

```bash
# Clone the repository

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys

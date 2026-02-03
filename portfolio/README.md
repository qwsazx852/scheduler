# AI Implementation Engineering Portfolio

**Candidate:** Jin-Jia Zhang (Jimmy)
**Role:** AI Implementation Engineer

This repository contains selected workflows demonstrating my ability to orchestrate **AI Agents**, **Automate Content Pipelines**, and solve **Supply Chain Optimization** problems using a hybrid approach (n8n + Python).

## 📂 Project Structure

### 1. [Sherry AI Assistant](./Sherry_AI_Assistant)
*The "Super-Assistant" with Eyes, Ears, and Memory*
- **`main_agent.json`**: The core logic handling Multi-Model switching (Gemini/Groq) and Tool Calling.
- **`job_hunter.json`**: The agent that reverse-engineers job board APIs to find and score relevant positions.
- **`morning_news.json`**: End-to-end content pipeline (RSS -> AI Summary -> TTS -> Line Audio).

### 2. [Supply Chain RFQ Agent](./Supply_Chain_RFQ)
*Automating the "Hard" Logic*
- **`rfq_agent.json`**: Orchestrates valid optical character recognition (OCR) simulation and connects to Python optimization logic.

### 3. [Utils](./Utils)
- **`tts_server.py`**: A lightweight Python server that handles Text-to-Speech generation, serving audio files to the n8n pipeline.

## 🔐 Security Note
All sensitive API Keys (Google, Line, Groq) have been sanitized and replaced with placeholders (e.g., `{{ $env.GOOGLE_GEMINI_KEY }}`).

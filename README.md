# SMB-Revenue-Service

A local AI-powered financial dashboard builder for small-to-medium businesses. 
Upload your financial spreadsheet or Google Sheet, and get a structured, interactive dashboard powered by LLaMA 3 via Ollama — with actionable insights and visualized metrics.

---

## Features

- **Smart Data Extraction**: Parses revenue, cost, and margin data from Excel, CSV, or Google Sheets using LLaMA 3.
- **Dashboards with Insights**: Generates dashboards for:
  - Revenue Analysis
  - Profit Margin Analysis
  - Cost Optimization
- **LLM Suggestions**: Includes detailed improvement advice beneath each chart.
- **Dark-Themed GUI**: Built with tkinter + Plotly Dash.
- **Automatic Error Recovery**: If the LLM returns invalid JSON, the system retries and improves the prompt using error feedback.

---

## Setup Instructions

### 1. Install Python

Ensure Python 3.10+ is installed. [Download Python](https://www.python.org/downloads/)

### 2. Install Ollama + LLaMA 3

Ollama is required to run LLaMA 3 locally:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
```
Make sure it is in your system path.


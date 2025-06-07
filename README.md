# SMB-Revenue-Service

A local AI-powered financial dashboard builder for small-to-medium businesses. 
Upload your financial spreadsheet or Google Sheet, and get a structured, interactive dashboard powered by Prophet and LLaMA 3 via Ollama — with actionable insights and visualized metrics.

---

## Features

- **Smart Data Extraction**: Parses revenue, cost, and margin data from Excel, CSV, or Google Sheets using LLaMA 3 for use in Prophet/LLama forecast.
- **Data Prediction and TimeSeries Detection**: Looks for time series aggregate data and predicts future revenue, earnings, and other financial indicators. 
- **Dashboards with Insights**: Generates dashboards for:
  - Revenue Analysis
  - Profit Margin Analysis
  - Cost Optimization
- **LLM Suggestions**: Includes detailed improvement advice beneath each chart.
- **Prophet Suggestions**: Includes detailed improvement advice based on future forecast determined by prophet.
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

### 3. Install Required Python Packages
From the project root:

```bash
pip install -r requirements.txt
```

## Usage

### Option A: Full GUI App (Recommended)
1. Select a .csv, .xlsx, or Google Sheets URL
2. It will:
   - Extract and convert financials using LLaMA 3
   - Launch a dashboard viewer at http://127.0.0.1:8050
   - Display a clickable link inside the GUI
### Option B: CLI Version (No GUI)
```bash
python nogui.py path/to/spreadsheet.xlsx
# OR
python nogui.py "https://docs.google.com/spreadsheets/d/..."
```

## Structure
```bash
.
├── fullGui.py           # Unified GUI launcher
├── extract2.py          # Spreadsheet → JSON extractor (uses LLaMA)
├── dashboard.py         # Generates interactive dashboards from JSON
├── prompts.py           # All LLM prompt logic (modular + self-correcting)
├── nogui.py             # CLI launcher alternative
├── requirements.txt     # Locked Python dependency versions
```

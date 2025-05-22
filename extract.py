import pandas as pd
import json
import os
import subprocess

def read_data(file_path_or_url):
    """
    Reads data from an Excel file, CSV file, or Google Sheets public URL.
    Returns a dictionary of sheet/table name -> DataFrame.
    """
    data = {}
    try:
        if file_path_or_url.startswith("http"):
            if "docs.google.com" in file_path_or_url:
                print("Reading from Google Sheets...")
                sheet_id = file_path_or_url.split("/d/")[1].split("/")[0]
                export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                df = pd.read_csv(export_url)
                data["Google Sheet"] = df.fillna('')
            else:
                raise ValueError("Only Google Sheets URLs are supported for now.")
        elif file_path_or_url.endswith(".csv"):
            print("Reading CSV file...")
            df = pd.read_csv(file_path_or_url)
            data["CSV File"] = df.fillna('')
        elif file_path_or_url.endswith((".xlsx", ".xls")):
            print("Reading Excel file...")
            xls = pd.ExcelFile(file_path_or_url, engine='openpyxl')
            data = {sheet: xls.parse(sheet).fillna('') for sheet in xls.sheet_names}
        else:
            raise ValueError("Unsupported file type or URL format.")
    except Exception as e:
        print(f"Error reading file: {e}")
    return data

def format_for_prompt(data_dict):
    formatted = ""
    for sheet, df in data_dict.items():
        formatted += f"\n### Sheet: {sheet}\n"
        formatted += df.to_csv(index=False)
    return formatted

def run_ollama_prompt(prompt, model='llama3'):
    try:
        result = subprocess.run(
            ['ollama', 'run', model],
            input=prompt.encode('utf-8'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=90
        )
        return result.stdout.decode('utf-8')
    except Exception as e:
        return f"Error running ollama: {e}"

def extract_json_from_response(response):
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        return json.loads(response[start:end])
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return {"raw_response": response}

def main(path_or_url):
    data = read_data(path_or_url)
    if not data:
        return

    prompt_data = format_for_prompt(data)

    prompt = f"""
You are a financial assistant AI. You cannot output any false or made up numbers. Given the following financial data from a small-to-medium retail business,
convert it into a structured JSON format summarizing key financial items: assets, liabilities, revenue, expenses, and net income.

Output only valid JSON. No explanations.

{prompt_data}
"""

    print("Running LLaMA 3 via Ollama...")
    response = run_ollama_prompt(prompt)
    json_data = extract_json_from_response(response)

    output_file = "financial_output.json"
    with open(output_file, "w") as f:
        json.dump(json_data, f, indent=2)
    print(f"✅ JSON data saved to {output_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python sheet_to_json_ollama.py <path_or_google_sheets_url>")
    else:
        main(sys.argv[1])

import pandas as pd
import json
import os
import subprocess
from prompts import get_extraction_prompt, get_timeseries_prompt

def read_data(file_path_or_url):
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

def extract_timeseries_with_retries(prompt_data, max_attempts=3):
    last_error = ""
    for attempt in range(max_attempts):
        prompt = get_timeseries_prompt(prompt_data, error_message=last_error if attempt > 0 else None)
        response = run_ollama_prompt(prompt)
        try:
            return extract_json_from_response(response)
        except Exception as e:
            last_error = str(e)
            print(f"❌ Retry {attempt + 1} failed: {last_error}")
    return {}

def main(path_or_url, mode="summary"):
    data = read_data(path_or_url)
    if not data:
        print("❌ No data extracted from file.")
        return

    prompt_data = format_for_prompt(data)
    json_data = None

    if mode == "summary":
        print("🔍 Running summary extraction...")
        for attempt in range(3):
            prompt = get_extraction_prompt(prompt_data)
            response = run_ollama_prompt(prompt)
            json_data = extract_json_from_response(response)
            if "revenue_analysis" in json_data:
                break
    elif mode == "forecast":
        print("📈 Extracting time series for Prophet...")
        json_data = extract_timeseries_with_retries(prompt_data)
    else:
        print(f"❌ Unknown extraction mode: {mode}")
        return

    if not json_data:
        print("⚠️ Could not extract valid JSON.")
        with open("financial_output_raw.txt", "w") as f:
            f.write(response)
    else:
        with open("financial_output.json", "w") as f:
            json.dump(json_data, f, indent=2)
        print("✅ JSON data saved to financial_output.json")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python extract2.py <path_or_url> <mode: summary|forecast>")
    else:
        main(sys.argv[1], sys.argv[2])

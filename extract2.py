import pandas as pd
import json
import os
import subprocess
from prompts import get_extraction_prompt

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
    base_prompt = get_extraction_prompt(prompt_data)


    max_attempts = 5
    attempt = 0
    json_data = None

    print("Running LLaMA 3 via Ollama...")
    while attempt < max_attempts:
        response = run_ollama_prompt(base_prompt)
        json_data = extract_json_from_response(response)

        # If we get a valid parsed JSON dict (not fallback), break loop
        if "raw_response" not in json_data:
            break

        print(f"❌ Failed to parse JSON on attempt {attempt + 1}. Retrying...")
        attempt += 1

    if "raw_response" in json_data:
        print("⚠️ Failed to extract valid JSON after multiple attempts. Saving raw output.")
        output_file = "financial_output_raw.txt"
        with open(output_file, "w") as f:
            f.write(json_data["raw_response"])
    else:
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

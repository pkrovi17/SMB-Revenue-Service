import pandas as pd
import json
import os
import subprocess

def read_excel_sheets(file_path):
    """
    Reads all sheets in the Excel file into a dictionary of DataFrames.
    """
    try:
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        data = {sheet_name: xls.parse(sheet_name).fillna('') for sheet_name in xls.sheet_names}
        return data
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return {}

def format_for_prompt(data_dict):
    """
    Formats the Excel data as a string for input into the LLM.
    """
    formatted = ""
    for sheet, df in data_dict.items():
        formatted += f"\n### Sheet: {sheet}\n"
        formatted += df.to_csv(index=False)
    return formatted

def run_ollama_prompt(prompt, model='llama3'):
    """
    Sends a prompt to the locally running Ollama model and returns the response.
    """
    try:
        result = subprocess.run(
            ['ollama', 'run', model],
            input=prompt.encode('utf-8'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )
        output = result.stdout.decode('utf-8')
        return output
    except subprocess.TimeoutExpired:
        return "Model timed out. Try simplifying the prompt."
    except Exception as e:
        return f"Error running ollama: {e}"

def extract_json_from_response(response):
    """
    Try to extract a JSON object from the LLM's response.
    """
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        return json.loads(response[start:end])
    except Exception as e:
        print(f"Could not parse JSON from response: {e}")
        return {"raw_response": response}

def main(excel_path):
    print("Reading Excel file...")
    data = read_excel_sheets(excel_path)
    if not data:
        return

    prompt_data = format_for_prompt(data)

    prompt = f"""
You are a financial assistant AI. Given the following spreadsheet data of a small-to-medium retail business, convert it into a structured JSON format summarizing key financial items like assets, liabilities, revenue, expenses, and net income if applicable.

Output only valid JSON. Do not include explanations.

{prompt_data}
"""

    print("Running model locally with Ollama...")
    response = run_ollama_prompt(prompt)
    json_data = extract_json_from_response(response)

    output_file = "financial_output.json"
    with open(output_file, "w") as f:
        json.dump(json_data, f, indent=2)
    print(f"✅ JSON data written to {output_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python excel_to_json_with_ollama.py <path_to_excel_file>")
    else:
        main(sys.argv[1])

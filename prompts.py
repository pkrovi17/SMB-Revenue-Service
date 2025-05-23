def get_extraction_prompt(prompt_data, error_message=None):
    error_section = f"\nNote: The previous attempt failed with this parsing error:\n{error_message}\nTry to fix the JSON formatting.\n" if error_message else ""
    suggested_structure = '''
{
  "revenue_analysis": {
    "revenue": 0
  },
  "profit_margin_analysis": {
    "revenue": 0,
    "cost_of_goods_sold": 0,
    "gross_profit": 0,
    "net_income": 0
  },
  "cost_optimization_analysis": {
    "operating_expenses": 0,
    "inventory_costs": 0,
    "logistics_costs": 0
  }
}
'''
    return f"""
You are a financial analyst AI. Given the following spreadsheet data from a small-to-medium retail business,
convert it into a structured JSON format needed to perform:

1. Revenue analysis
2. Profit margin analysis
3. Cost optimization analysis

Extract only the necessary data for these analyses. Only extract what’s available from the data. If any field is missing, include it as 0.

Please follow this suggested JSON structure exactly as a guide. Output only valid JSON — no commentary or explanation.
Error form previous attempts:
{error_section}

Suggested structure:
{suggested_structure}

Spreadsheet data:
{prompt_data}
"""

def get_dashboard_prompt(json_str, error_message=None):
    error_section = f"\nNote: The previous attempt failed with this JSON parsing error:\n{error_message}\nPlease output valid JSON.\n" if error_message else ""
    outputFormat = """
{
  {
    "title": "Revenue Analysis",
    "description": "Compare revenue over time or against targets.",
    "chart_type": "bar",
    "data_points": {
      "Revenue": "revenue_analysis.revenue"
    },
    "insight": "While revenue is stable, net income appears significantly lower, suggesting that fixed costs may be too high. Consider reducing non-essential overhead or negotiating supplier contracts to improve profitability."
  },
}
"""
    return f"""
You are a financial dashboard AI assistant.
Empty strings are not legal JSON5.
Given this JSON data for a small business, generate dashboards for these **3 fixed sections**:
You will generate **three high-quality dashboards** for a small business using the provided JSON data. Each one should correspond to one of the following fixed categories:
1. Revenue Analysis
2. Profit Margin Analysis
3. Cost Optimization Analysis

For each, return:
- "title"
- "description"
- "chart_type": bar, pie, or line
- "data_points": dictionary of label → JSON path
- "insight": A **detailed recommendation (2–3 sentences)** explaining what the chart reveals and **how the business can improve**. Include possible causes, corrective actions, or benchmarks where appropriate.

Error form previous attempts:
{error_section}

Output format (JSON list):
{outputFormat}

Financial data:
{json_str}
"""

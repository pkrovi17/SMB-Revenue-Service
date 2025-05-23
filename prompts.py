def get_extraction_prompt(prompt_data):
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

Suggested structure:
{suggested_structure}

Spreadsheet data:
{prompt_data}
"""

def get_dashboard_prompt(json_str):
    outputFormat = """
{
  {
    "title": "Revenue Analysis",
    "description": "Compare revenue over time or against targets.",
    "chart_type": "bar",
    "data_points": {
      "Revenue": "revenue_analysis.revenue"
    },
    "insight": "Consider diversifying revenue streams to reduce risk."
  },
}
"""
    return f"""
You are a financial dashboard AI assistant.
Empty strings are not legal JSON5.
Given this JSON data for a small business, generate dashboards for these **3 fixed sections**:

1. Revenue Analysis
2. Profit Margin Analysis
3. Cost Optimization Analysis

For each, return:
- "title"
- "description"
- "chart_type": bar, pie, or line
- "data_points": dictionary of label → JSON path
- "insight": 1–2 sentence suggestion on how to improve performance

Output format (JSON list):
{outputFormat}

Financial data:
{json_str}
"""

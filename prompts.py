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

Extract only the necessary data for these analyses. Only extract what’s available from the data. Do not include any explanation, comments, or notes in your answer.
If any field is missing, include it as 0.
IMPORTANT:
- Any value labeled with words like **\"loss\", \"negative\", \"deficit\", or parentheses like (1234)** should be interpreted as a **negative number**.
- For example, \"Net Loss\" of 2000 should be entered as -2000.
- Do not treat \"Loss\" values as revenue or income. Subtract them appropriately.
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
    chart_guide = """
Revenue Analysis:
- Line Chart: Revenue over time (monthly, yearly)
- Bar Chart: Revenue per product/category/store
- Treemap: Revenue share by region/product
- Heatmap: Revenue per day/hour (e.g., retail footfall)
- Cumulative Line: Year-to-date revenue progression

Profit Margin Analysis:
- Stacked Bar Chart: Revenue vs. cost vs. profit
- Line Chart: Profit margin percent over time
- Waterfall Chart: How revenue becomes net profit
- Bubble Chart: Margin % vs. revenue size

Cost Optimization Analysis:
- Pareto Chart: Which costs dominate (80/20 rule)
- Stacked Area Chart: Cost components over time
- Horizontal Bar: Costs by department/vendor
- Box Plot: Cost variance (outliers)
- Trend Line Chart: Cost impact over time
"""
    outputFormat = """
[
  {
    "title": "Revenue Analysis",
    "description": "Compare revenue over time or against targets.",
    "chart_type": "bar",
    "data_points": {
      "Revenue": "revenue_analysis.revenue"
    },
    "insight": "While revenue is stable, net income appears significantly lower, suggesting that fixed costs may be too high. Consider reducing non-essential overhead or negotiating supplier contracts to improve profitability."
  },
]
"""
    return f"""
You are a financial dashboard AI assistant.
Empty strings are not legal JSON5.
Given this JSON data for a small business, generate dashboards for these **3 fixed sections**:
You will generate **three high-quality dashboards** for a small business using the provided JSON data. Each one should correspond to one of the following fixed categories:
1. Revenue Analysis
2. Profit Margin Analysis
3. Cost Optimization Analysis
For each, choose the best-fitting chart type using this guide:
{chart_guide}
❌ DO NOT include any introductions, bullet points, titles, commentary, or markdown.
✅ Your entire response must be a valid JSON list: [{{...}}, {{...}}, ...]

Each object should have:
- "title": short chart name
- "description": what it shows
- "chart_type": one of: line, bar, treemap, bubble, waterfall, heatmap, horizontal bar, etc.
- "data_points": label → JSON path (e.g., "Revenue": "revenue_analysis.revenue")
- "insight": a recommendation (2–3 sentences) about what the chart shows and how to improve

Error form previous attempts:
{error_section}

Output format (JSON list):
{outputFormat}

Financial data:
{json_str}
"""
def get_timeseries_prompt(prompt_data, field_name="Revenue", error_message=None):
    error_section = f"\nNote: Previous attempt failed:\n{error_message}\nPlease fix the formatting.\n" if error_message else ""
    outputFormat = """
{
  {
    "revenue_analysis": {
      "revenue_by_month": {
        "2023-01": 5000,
        "2023-02": 6000
      }
    }
  }
}
"""
    outputFormat2 = """
{
  "sku_forecast": {
    "PRODUCT NAME A": {
      "2022-07": 152.30,
      "2022-08": 98.00
    },
    "PRODUCT NAME B": {
      "2022-07": 240.75
    }
  }
}
"""
    return f"""
You are a financial data extraction AI.

Given a sales spreadsheet with rows for **individual transactions** that include:
- product name or SKU
- quantity sold
- price per unit (sometimes written with currency symbols or commas)
- a timestamp (e.g., date of transaction)

Your task is to output a **monthly time series of total revenue per product** in this format:
{outputFormat2}
Do not include any explanation, comments, or notes in your answer.
Notes:
- Compute revenue = quantity × price
- Price may be a string like `"1,20 €"` — convert it to float
- Timestamps should be grouped by **month** using YYYY-MM
- If no date or revenue is available, skip that row
- Skip SKUs with no sales

{error_section}

Spreadsheet data:
{prompt_data}
"""

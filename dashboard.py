import json
import subprocess
import plotly.graph_objs as go
from dash import Dash, html, dcc
import json5 as json  # instead of regular json

def load_json_data(filepath="financial_output.json"):
    with open(filepath, "r") as f:
        return json.load(f)

def ask_llama_for_dashboard_suggestions(json_str):
    prompt = f"""
You are a financial dashboard assistant.

Your task is to generate dashboard ideas based on JSON-formatted financial data for a small-to-medium retail business.

Each dashboard must include:
- "title": short chart title
- "description": brief explanation
- "chart_type": one of ["bar", "line", "pie"]

Output ONLY valid JSON (an array of objects) with no commentary or Markdown. Format like this:

[
  {{
    "title": "Revenue vs Expenses",
    "description": "Compare revenue to cost of goods sold and net income",
    "chart_type": "bar"
  }},
  {{
    "title": "Income Composition",
    "description": "Breakdown of profit components",
    "chart_type": "pie"
  }}
]

Financial data:
{json_str}
"""


    result = subprocess.run(
        ['ollama', 'run', 'llama3'],
        input=prompt.encode('utf-8'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60
    )
    return result.stdout.decode('utf-8')

def extract_dashboard_list_with_retry(response_func, max_attempts=5):
    for attempt in range(max_attempts):
        print(f"Parsing LLaMA dashboard suggestion attempt {attempt + 1}...")
        response = response_func()

        try:
            start = response.find('[')
            end = response.rfind(']') + 1
            dashboard_json = json.loads(response[start:end])
            return dashboard_json  #Success
        except Exception as e:
            print(f"Failed to parse JSON (attempt {attempt + 1}): {e}")
            with open(f"llama_dashboard_attempt_{attempt + 1}.txt", "w") as f:
                f.write(response)

    print("⚠️ All attempts failed. See llama_dashboard_attempt_*.txt for details.")
    return []


def safe_value(val):
    return val if isinstance(val, (int, float)) else 0

def generate_figure(title, chart_type, financial_data):
    # Basic example for income statement metrics
    income = financial_data.get("income_statement", {})
    keys = ["revenue", "cost_of_goods_sold", "operating_expenses", "net_income"]
    values = [safe_value(income.get(k)) for k in keys]

    if chart_type == "bar":
        return go.Figure(
            data=[go.Bar(x=keys, y=values, marker_color="#f5c147")],
            layout=go.Layout(title=title)
        )
    elif chart_type == "pie":
        return go.Figure(
            data=[go.Pie(labels=keys, values=values)],
            layout=go.Layout(title=title)
        )
    elif chart_type == "line":
        return go.Figure(
            data=[go.Scatter(x=keys, y=values, mode='lines+markers')],
            layout=go.Layout(title=title)
        )
    else:
        return go.Figure()

def build_dash_app(dashboards, financial_data):
    app = Dash(__name__)
    plots = []

    for dash in dashboards:
        fig = generate_figure(dash["title"], dash["chart_type"].lower(), financial_data)
        plots.append(html.Div([
            html.H3(dash["title"], style={"color": "#f5c147"}),
            html.P(dash["description"], style={"color": "#cccccc"}),
            dcc.Graph(figure=fig)
        ], style={"marginBottom": "40px"}))

    app.layout = html.Div(plots, style={
        "backgroundColor": "#1e1e1e",
        "padding": "40px",
        "fontFamily": "Segoe UI"
    })

    return app

def main():
    financial_data = load_json_data()
    json_str = json.dumps(financial_data, indent=2)
    response_func = lambda: ask_llama_for_dashboard_suggestions(json_str)
    dashboards = extract_dashboard_list_with_retry(response_func)

    if dashboards:
        app = build_dash_app(dashboards, financial_data)
        print("Running dashboard at http://127.0.0.1:8050/")
        app.run(debug=True)
    else:
        print("No valid dashboards returned by LLaMA 3.")

if __name__ == "__main__":
    main()

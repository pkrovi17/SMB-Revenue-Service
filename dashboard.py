import json
import subprocess
import plotly.graph_objs as go
from dash import Dash, html, dcc
import json5 as json  # instead of regular json
from prompts import get_dashboard_prompt

def load_json_data(filepath="financial_output.json"):
    with open(filepath, "r") as f:
        return json.load(f)
    
def get_nested_value(data, path):
    keys = path.split('.')
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, None)
        else:
            return None
    return data

def ask_llama_for_dashboard_suggestions(json_str):
    
    prompt = get_dashboard_prompt(json_str)
    
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

    print("All attempts failed. See llama_dashboard_attempt_*.txt for details.")
    return []


def safe_value(val):
    return val if isinstance(val, (int, float)) else 0

def generate_figure(dash_config, financial_data):
    title = dash_config["title"]
    chart_type = dash_config["chart_type"].lower()
    data_points = dash_config.get("data_points", {})

    labels = list(data_points.keys())
    values = [get_nested_value(financial_data, path) or 0 for path in data_points.values()]

    fig = go.Figure()

    if chart_type == "bar":
        fig.add_trace(go.Bar(x=labels, y=values, marker_color="#f5c147"))
    elif chart_type == "pie":
        fig.add_trace(go.Pie(labels=labels, values=values))
    elif chart_type == "line":
        fig.add_trace(go.Scatter(x=labels, y=values, mode='lines+markers'))
    else:
        fig.add_trace(go.Bar(x=labels, y=values))  # fallback

    fig.update_layout(title=title, template="plotly_dark", height=400)
    return fig


def build_dash_app(dashboards, financial_data):
    app = Dash(__name__)
    plots = []

    for dash in dashboards:
        fig = generate_figure(dash, financial_data)
        plots.append(html.Div([
            html.H3(dash["title"], style={"color": "#f5c147"}),
            html.P(dash["description"], style={"color": "#cccccc"}),
            dcc.Graph(figure=fig),
            html.Div(f"💡 Suggestion: {dash.get('insight', 'No insight provided.')}",
                    style={"color": "#aaaaaa", "fontStyle": "italic", "marginTop": "10px"})
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

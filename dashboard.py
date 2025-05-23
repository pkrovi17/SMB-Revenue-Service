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

def extract_dashboard_list_with_retry(json_str, max_attempts=5):
    last_error = ""
    for attempt in range(max_attempts):
        print(f"🔁 Parsing LLaMA dashboard suggestion attempt {attempt + 1}...")

        prompt = get_dashboard_prompt(json_str, error_message=last_error if attempt > 0 else None)
        response = ask_llama_for_dashboard_suggestions(prompt)

        try:
            start = response.find('[')
            end = response.rfind(']') + 1
            dashboard_json = json.loads(response[start:end])
            return dashboard_json  # ✅ Success
        except Exception as e:
            last_error = str(e)
            print(f"❌ Failed to parse JSON (attempt {attempt + 1}): {last_error}")
            with open(f"llama_dashboard_attempt_{attempt + 1}.txt", "w") as f:
                f.write(response)

    print("⚠️ All attempts failed. See llama_dashboard_attempt_*.txt for details.")
    return []


def safe_value(val):
    return val if isinstance(val, (int, float)) else 0

def generate_figure(dash_config, financial_data):
    import numpy as np
    import pandas as pd

    title = dash_config["title"]
    chart_type = dash_config["chart_type"].lower()
    data_points = dash_config.get("data_points", {})

    labels = list(data_points.keys())
    values = [get_nested_value(financial_data, path) or 0 for path in data_points.values()]
    fig = go.Figure()

    if chart_type == "bar":
        fig.add_trace(go.Bar(x=labels, y=values, marker_color="#f5c147"))

    elif chart_type == "horizontal bar":
        fig.add_trace(go.Bar(x=values, y=labels, orientation='h', marker_color="#f5c147"))

    elif chart_type == "line":
        fig.add_trace(go.Scatter(x=labels, y=values, mode='lines+markers'))

    elif chart_type == "cumulative line":
        cumulative = np.cumsum(values)
        fig.add_trace(go.Scatter(x=labels, y=cumulative, mode='lines', name='Cumulative'))

    elif chart_type == "treemap":
        fig.add_trace(go.Treemap(labels=labels, parents=[""]*len(labels), values=values))

    elif chart_type == "heatmap":
        df = pd.DataFrame([values], columns=labels)
        fig = go.Figure(data=go.Heatmap(z=df.values, x=labels, y=["Heatmap"], colorscale='YlOrRd'))

    elif chart_type == "stacked bar":
        fig.update_layout(barmode='stack')
        for label, val in zip(labels, values):
            fig.add_trace(go.Bar(name=label, x=[title], y=[val]))

    elif chart_type == "stacked area":
        for i, label in enumerate(labels):
            fig.add_trace(go.Scatter(
                x=[title], y=[values[i]], name=label,
                stackgroup='one', mode='none'
            ))

    elif chart_type == "bubble":
        sizes = [max(v, 10) for v in values]  # Avoid 0-size bubbles
        fig.add_trace(go.Scatter(x=labels, y=values, mode='markers',
                                marker=dict(size=sizes, color=values, showscale=True)))

    elif chart_type == "waterfall":
        fig.add_trace(go.Waterfall(
            x=labels,
            y=values,
            connector={"line": {"color": "rgb(63, 63, 63)"}}
        ))

    elif chart_type == "pareto":
        # Sort descending and compute cumulative %
        df = pd.DataFrame({"label": labels, "value": values}).sort_values("value", ascending=False)
        df["cum_pct"] = df["value"].cumsum() / df["value"].sum() * 100
        fig.add_trace(go.Bar(x=df["label"], y=df["value"], name="Cost Contribution"))
        fig.add_trace(go.Scatter(
            x=df["label"], y=df["cum_pct"],
            yaxis="y2", name="Cumulative %",
            mode="lines+markers", marker=dict(color="red")
        ))
        fig.update_layout(
            yaxis2=dict(overlaying="y", side="right", title="Cumulative %"),
            barmode="group"
        )

    elif chart_type == "box plot":
        fig.add_trace(go.Box(y=values, name=title))

    else:
        fig.add_trace(go.Bar(x=labels, y=values))  # fallback

    fig.update_layout(title=title, template="plotly_dark", height=400)
    return fig

def build_dash_app(dashboards, financial_data):
    app = Dash(__name__)
    plots = []
    for dash in dashboards:
        if not isinstance(dash, dict):
            print(f"⚠️ Skipping invalid dashboard entry: {dash}")
            continue
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
    #response_func = lambda: ask_llama_for_dashboard_suggestions(json_str)
    #dashboards = extract_dashboard_list_with_retry(response_func)
    dashboards = extract_dashboard_list_with_retry(json_str)

    if dashboards:
        app = build_dash_app(dashboards, financial_data)
        print("Running dashboard at http://127.0.0.1:8050/")
        app.run(debug=True)
    else:
        print("No valid dashboards returned by LLaMA 3.")

if __name__ == "__main__":
    main()

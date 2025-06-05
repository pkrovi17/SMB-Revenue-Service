import json
import subprocess
import plotly.graph_objs as go
from dash import Dash, html, dcc
import json5 as json
from prompts import get_dashboard_prompt
from forecast3 import prepare_prophet_input, forecast_timeseries, generate_forecast_insight
from util3 import get_nested_value

def load_json_data(filepath="financial_output.json"):
    with open(filepath, "r") as f:
        return json.load(f)

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
            json_block = response[start:end].strip()
            if not json_block:
                raise ValueError("Received empty JSON string from LLaMA")
            dashboard_json = json.loads(json_block)
            if isinstance(dashboard_json, dict):
                dashboard_json = [dashboard_json]
            if not isinstance(dashboard_json, list):
                raise ValueError("Expected a list of dashboards")
            return dashboard_json
        except Exception as e:
            last_error = str(e)
            print(f"❌ Failed to parse JSON (attempt {attempt + 1}): {last_error}")
            with open(f"llama_dashboard_attempt_{attempt + 1}.txt", "w", encoding="utf-8") as f:
                f.write(response)
    print("⚠️ All attempts failed. See llama_dashboard_attempt_*.txt for details.")
    return []

def safe_value(val):
    return val if isinstance(val, (int, float)) else 0

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

    # Add Prophet forecast with insights
    prophet_input = prepare_prophet_input(financial_data)
    forecast_results, mode = forecast_timeseries(prophet_input, field_name="Revenue")

    if mode == "multi":
        for sku, fig, forecast_df, units_fig in forecast_results:
            insight = generate_forecast_insight(forecast_df, sku)
            plots.append(html.Div([
                html.H3(f"📦 Forecast for SKU: {sku}", style={"color": "#f5c147"}),
                dcc.Graph(figure=fig),
                html.H4("📊 Units Forecast", style={"color": "#f5c147"}),
                dcc.Graph(figure=units_fig),
                html.P(insight, style={"color": "#cccccc"})
            ]))     

    elif mode == "single":
        for sku, fig, forecast_df, units_fig in forecast_results:
            plots.append(html.Div([
                html.H3("📈 Forecasted Revenue Trend", style={"color": "#f5c147"}),
                dcc.Graph(figure=fig),
                html.P("📊 This forecast projects overall revenue growth. Focus on scaling top-performing channels and reviewing cost centers.", style={"color": "#cccccc"})
            ]))

    app.layout = html.Div(plots, style={
        "backgroundColor": "#1e1e1e",
        "padding": "40px",
        "fontFamily": "Segoe UI"
    })

    return app

def generate_figure(dash_config, financial_data):
    import numpy as np
    import pandas as pd

    title = dash_config["title"]
    chart_type = dash_config["chart_type"].lower()
    data_points = dash_config.get("data_points", {})

    labels = list(data_points.keys())
    values = [get_nested_value(financial_data, path) or 0 for path in data_points.values()]
    fig = go.Figure()

    if chart_type in ["line", "time series"]:
        fig.add_trace(go.Scatter(x=labels, y=values, mode='lines+markers'))
    elif chart_type == "cumulative line":
        cumulative = np.cumsum(values)
        fig.add_trace(go.Scatter(x=labels, y=cumulative, mode='lines', name='Cumulative'))
    elif chart_type == "heatmap":
        df = pd.DataFrame([values], columns=labels)
        fig = go.Figure(data=go.Heatmap(z=df.values, x=labels, y=["Heatmap"], colorscale='YlOrRd'))
    elif chart_type == "box plot":
        fig.add_trace(go.Box(y=values, name=title))
    else:
        fig.add_trace(go.Bar(x=labels, y=values, marker_color="#f5c147"))

    fig.update_layout(title=title, template="plotly_dark", height=400)
    return fig

def main():
    financial_data = load_json_data()
    json_str = json.dumps(financial_data, indent=2)
    dashboards = extract_dashboard_list_with_retry(json_str)
    if dashboards:
        app = build_dash_app(dashboards, financial_data)
        print("Running dashboard at http://127.0.0.1:8050/")
        app.run(debug=True)
    else:
        print("No valid dashboards returned by LLaMA 3.")

if __name__ == "__main__":
    main()

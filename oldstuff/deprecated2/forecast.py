from prophet import Prophet
import pandas as pd
import plotly.graph_objs as go

def forecast_timeseries(data, field_name="revenue", periods=12, freq="M"):
    df = pd.DataFrame(data)
    df.columns = ['ds', 'y']
    df['ds'] = pd.to_datetime(df['ds'])

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)

    # Create plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], name="Actual"))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name="Forecast"))
    fig.update_layout(title=f"{field_name.title()} Forecast", template="plotly_dark")
    return fig, forecast.tail(periods)[['ds', 'yhat']]
# Example format required by Prophet:
# [{'ds': '2023-01-01', 'y': 1000}, {'ds': '2023-02-01', 'y': 1100}, ...]
def prepare_prophet_input(financial_data, path="revenue_analysis.revenue_by_month"):
    from dashboard import get_nested_value
    monthly_data = get_nested_value(financial_data, path)
    if not isinstance(monthly_data, dict):
        return []

    return [{"ds": k, "y": v} for k, v in monthly_data.items()]

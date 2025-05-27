
from prophet import Prophet
import pandas as pd
import plotly.graph_objs as go
from util3 import get_nested_value

def prepare_prophet_input(financial_data, path="revenue_analysis.revenue_by_month"):
    monthly_data = get_nested_value(financial_data, path)
    if not isinstance(monthly_data, dict):
        return []
    try:
        return [{"ds": k, "y": float(v)} for k, v in monthly_data.items()]
    except Exception as e:
        print(f"Error formatting data for Prophet: {e}")
        return []

def forecast_timeseries(data, field_name="revenue", periods=12, freq="M"):
    df = pd.DataFrame(data)
    df.columns = ['ds', 'y']
    df['ds'] = pd.to_datetime(df['ds'])

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], name="Actual"))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name="Forecast"))
    fig.update_layout(title=f"{field_name.title()} Forecast", template="plotly_dark")

    return fig, forecast.tail(periods)[['ds', 'yhat']]

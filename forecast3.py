from prophet import Prophet
import pandas as pd
import plotly.graph_objs as go
from utils import get_nested_value

def prepare_prophet_input(financial_data, path="revenue_analysis.revenue_by_month"):
    # Supports both flat and SKU-labeled time series
    if "sku_forecast" in financial_data:
        result = {}
        for sku, series in financial_data["sku_forecast"].items():
            if isinstance(series, dict):
                try:
                    result[sku] = [{"ds": k, "y": float(v)} for k, v in series.items()]
                except Exception as e:
                    print(f"SKU {sku} parsing failed: {e}")
        return result if result else None

    # Fallback to flat time series (monthly revenue)
    monthly_data = get_nested_value(financial_data, path)
    if not isinstance(monthly_data, dict):
        return None
    try:
        return [{"ds": k, "y": float(v)} for k, v in monthly_data.items()]
    except Exception as e:
        print(f"Error formatting revenue for Prophet: {e}")
        return None

def forecast_timeseries(data, field_name="revenue", periods=12, freq="M"):
    def build_forecast_fig(df, forecast):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=forecast["ds"], y=forecast["yhat_lower"],
            mode='lines', name='Lower Bound', line=dict(dash='dot')))
        fig.add_trace(go.Scatter(
            x=forecast["ds"], y=forecast["yhat_upper"],
            mode='lines', name='Upper Bound', line=dict(dash='dot')))
        fig.add_trace(go.Scatter(
            x=forecast["ds"], y=forecast["yhat"],
            mode='lines+markers', name='Forecast'))
        fig.add_trace(go.Scatter(
            x=df['ds'], y=df['y'],
            mode='markers', name='Actual', marker=dict(color='white')))
        fig.update_layout(
            title=f"📈 Forecasted Trend: {field_name}",
            template="plotly_dark",
            height=450,
            xaxis_title="Month",
            yaxis_title="Forecasted Value"
        )
        return fig

    # Handle multi-SKU
    if isinstance(data, dict):
        figures = {}
        for sku, series in data.items():
            df = pd.DataFrame(series)
            df.columns = ['ds', 'y']
            df['ds'] = pd.to_datetime(df['ds'])
            model = Prophet()
            model.fit(df)
            future = model.make_future_dataframe(periods=periods, freq=freq)
            forecast = model.predict(future)
            figures[sku] = (build_forecast_fig(df, forecast), forecast.tail(periods)[['ds', 'yhat']])
        return figures

    # Handle single series
    elif isinstance(data, list):
        df = pd.DataFrame(data)
        df.columns = ['ds', 'y']
        df['ds'] = pd.to_datetime(df['ds'])
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=periods, freq=freq)
        forecast = model.predict(future)
        return build_forecast_fig(df, forecast), forecast.tail(periods)[['ds', 'yhat']]

    return None

from prophet import Prophet
import pandas as pd
import plotly.graph_objs as go

def clean_price(price_str):
    if isinstance(price_str, str):
        return float(price_str.replace("€", "").replace(",", ".").strip())
    return float(price_str or 0)

def prepare_prophet_input(financial_data):
    if "sku_forecast" in financial_data:
        result = {}
        for sku, month_data in financial_data["sku_forecast"].items():
            records = []
            for month, val in month_data.items():
                try:
                    if isinstance(val, dict):  # full format
                        units = float(val.get("units", 1))
                        price = clean_price(val.get("price", 1))
                        cost = clean_price(val.get("cost", price * 0.7))
                    else:  # simplified format
                        units = 1.0
                        price = clean_price(val)
                        cost = price * 0.7
                    records.append({
                        "ds": month,
                        "y": units,
                        "price": price,
                        "cost": cost
                    })
                except Exception as e:
                    print(f"⚠️ Skipping malformed entry for {sku} in {month}: {e}")
            if records:
                result[sku] = records
        return result
    elif "revenue_analysis" in financial_data and "revenue_by_month" in financial_data["revenue_analysis"]:
        monthly_data = financial_data["revenue_analysis"]["revenue_by_month"]
        return [{"ds": k, "y": float(v)} for k, v in monthly_data.items()]
    else:
        return []

def forecast_timeseries(data, field_name="Revenue", periods=12, freq="ME"):
    if isinstance(data, dict):
        figures = []
        for sku, records in data.items():
            fig, forecast_data, units_fig = _forecast_sku(records, sku, periods, freq)
            if not forecast_data.empty:
                figures.append((sku, fig, forecast_data, units_fig))
        return figures, "multi"
    elif isinstance(data, list):
        fig, forecast_df = _forecast_single(data, label=field_name, periods=periods, freq=freq)
        return [(field_name, fig, forecast_df, None)], "single"
    else:
        return [], "none"

def _forecast_single(data, label="Forecast", periods=12, freq="ME"):
    if not data or not isinstance(data, list) or len(data) < 2:
        print(f"⚠️ Skipping single forecast for '{label}' — not enough data.")
        return go.Figure(), pd.DataFrame()

    df = pd.DataFrame(data)
    if df.shape[1] < 2:
        print(f"⚠️ '{label}' forecast input does not have 2 columns.")
        return go.Figure(), pd.DataFrame()

    df.columns = ['ds', 'y']
    df['ds'] = pd.to_datetime(df['ds'])
    df = df.dropna(subset=['y'])

    if len(df) < 2:
        print(f"⚠️ Skipping forecast for '{label}' — not enough valid data.")
        return go.Figure(), pd.DataFrame()

    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat_lower"],
                             mode='lines', name='Lower Bound', line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat_upper"],
                             mode='lines', name='Upper Bound', line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"],
                             mode='lines+markers', name='Forecast'))

    fig.update_layout(
        title=f"📈 Forecast: {label}",
        template="plotly_dark",
        height=450,
        xaxis_title="Date",
        yaxis_title="Predicted Value"
    )

    return fig, forecast.tail(periods)[["ds", "yhat"]]

def _forecast_sku(data, label="SKU", periods=12, freq="ME"):
    df = pd.DataFrame(data)
    df = df.dropna(subset=["y"])
    if "ds" not in df.columns:
        print(f"⚠️ Data missing 'ds' column for {label}. Skipping.")
        return go.Figure(), pd.DataFrame(), None
    df["ds"] = pd.to_datetime(df["ds"])

    if len(df) < 2:
        print(f"⚠️ Skipping forecast for '{label}' — not enough data.")
        return go.Figure(), pd.DataFrame(), None

    price = df["price"].iloc[-1]
    cost = df["cost"].iloc[-1]

    model = Prophet()
    model.fit(df[["ds", "y"]])
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)

    forecast["price"] = price
    forecast["cost"] = cost
    forecast["revenue"] = forecast["yhat"] * price
    forecast["profit"] = forecast["yhat"] * (price - cost)
    forecast["margin_pct"] = (forecast["profit"] / forecast["revenue"].replace(0, 1)) * 100

    # Revenue/Profit/Margin plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["revenue"], name="Revenue Forecast"))
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["profit"], name="Profit Forecast"))
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["margin_pct"], name="Margin %", yaxis="y2"))
    fig.update_layout(
        title=f"📦 {label} – Revenue, Profit, Margin Forecast",
        template="plotly_dark",
        height=500,
        xaxis_title="Date",
        yaxis_title="Revenue / Profit",
        yaxis2=dict(
            title="Margin %",
            overlaying="y",
            side="right",
            showgrid=False
        )
    )

    # Units forecast plot
    units_fig = go.Figure()
    units_fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"], mode="lines+markers", name="Units Forecast"))
    units_fig.update_layout(
        title=f"📊 Units Forecast Over Time – {label}",
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title="Units Sold",
        height=400
    )

    return fig, forecast.tail(periods)[["ds", "yhat", "revenue", "profit", "margin_pct"]], units_fig

def generate_forecast_insight(df, sku="SKU"):
    if df.empty:
        return f"No forecast insight available for {sku}."

    latest = df.iloc[-1]
    trend = df.tail(3)

    avg_margin = trend["margin_pct"].mean()
    trend_revenue = trend["revenue"].values
    trend_diff = trend_revenue[-1] - trend_revenue[0]

    direction = "increasing" if trend_diff > 0 else "decreasing"
    margin_trend = "healthy" if avg_margin > 25 else "tight"

    return (
        f"📊 Forecast for {sku}: Revenue is {direction} over the next few periods "
        f"(up to ${latest['revenue']:.2f}), with a {margin_trend} margin of "
        f"~{avg_margin:.1f}%. Consider adjusting production, marketing, or pricing accordingly."
    )

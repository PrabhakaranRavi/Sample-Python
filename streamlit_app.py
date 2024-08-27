import streamlit as st
import yfinance as yf
from datetime import datetime, timezone, time, timedelta
import json
from streamlit_lightweight_charts import renderLightweightCharts

# Set the refresh interval in seconds (e.g., 60 seconds)
refresh_interval = 5

# Embed the JavaScript in Streamlit for auto-refresh
st.markdown(
    f"""
    <script>
        function refreshPage() {{
            setTimeout(function() {{
                window.location.reload(1);
            }}, {refresh_interval * 1000});
        }}
        refreshPage();
    </script>
    """,
    unsafe_allow_html=True,
)


# Function to perform the calculation and generate the JSON data
def perform_hourly_prediction(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, interval="60m")
    data = data.drop(columns=["Adj Close", "Volume"])

    # Initialize JSON structure
    jsonDataHourFrame = {
        "candlestick": [],
        "predicted_open1": [],
        "predicted_open2": [],
        "predicted_open3": [],
        "predicted_high1": [],
        "predicted_high2": [],
        "predicted_high3": [],
        "predicted_low1": [],
        "predicted_low2": [],
        "predicted_low3": [],
        "predicted_close1": [],
        "predicted_close2": [],
        "predicted_close3": [],
        "matches": []
    }

    # Push all candlestick data before the loop
    for i in range(len(data)):
        current_data = data.iloc[i]

        # Convert current time to Unix
        time_unix = int(current_data.name.timestamp())

        # Add the current hour's actual OHLC to the candlestick data
        jsonDataHourFrame["candlestick"].append(
            {
                "time": time_unix,
                "open": current_data["Open"],
                "high": current_data["High"],
                "low": current_data["Low"],
                "close": current_data["Close"],
            }
        )

    # Loop through data to calculate predictions
    for i in range(6, len(data)):
        # Use first six hours to predict the next hour
        six_hour_data = data.iloc[i - 6 : i]

        next_hour_data = data.iloc[i]
        # Convert next hour time to Unix
        time_unix = int(next_hour_data.name.timestamp())

        # Calculate sums for the first six hours
        sum_open = six_hour_data["Open"].sum()
        sum_high = six_hour_data["High"].sum()
        sum_low = six_hour_data["Low"].sum()
        sum_close = six_hour_data["Close"].sum()

        # Calculate DiffOH-LC
        diff_oh_lc = (sum_open + sum_high) - (sum_low + sum_close)

        # Calculate predicted values
        predicted_open1 = (sum_open / 6) + (diff_oh_lc / 3)
        predicted_open2 = (sum_open / 6) + (diff_oh_lc / 6)
        predicted_open3 = (sum_open / 6) + (diff_oh_lc / 9)

        predicted_high1 = (sum_high / 6) + (diff_oh_lc / 3)
        predicted_high2 = (sum_high / 6) + (diff_oh_lc / 6)
        predicted_high3 = (sum_high / 6) + (diff_oh_lc / 9)

        predicted_low1 = (sum_low / 6) + (diff_oh_lc / 3)
        predicted_low2 = (sum_low / 6) + (diff_oh_lc / 6)
        predicted_low3 = (sum_low / 6) + (diff_oh_lc / 9)

        predicted_close1 = (sum_close / 6) + (diff_oh_lc / 3)
        predicted_close2 = (sum_close / 6) + (diff_oh_lc / 6)
        predicted_close3 = (sum_close / 6) + (diff_oh_lc / 9)

        # Add predicted values to the JSON structure
        jsonDataHourFrame["predicted_open1"].append(
            {"time": time_unix, "value": predicted_open1}
        )
        jsonDataHourFrame["predicted_open2"].append(
            {"time": time_unix, "value": predicted_open2}
        )
        jsonDataHourFrame["predicted_open3"].append(
            {"time": time_unix, "value": predicted_open3}
        )
        jsonDataHourFrame["predicted_high1"].append(
            {"time": time_unix, "value": predicted_high1}
        )
        jsonDataHourFrame["predicted_high2"].append(
            {"time": time_unix, "value": predicted_high2}
        )
        jsonDataHourFrame["predicted_high3"].append(
            {"time": time_unix, "value": predicted_high3}
        )
        jsonDataHourFrame["predicted_low1"].append(
            {"time": time_unix, "value": predicted_low1}
        )
        jsonDataHourFrame["predicted_low2"].append(
            {"time": time_unix, "value": predicted_low2}
        )
        jsonDataHourFrame["predicted_low3"].append(
            {"time": time_unix, "value": predicted_low3}
        )
        jsonDataHourFrame["predicted_close1"].append(
            {"time": time_unix, "value": predicted_close1}
        )
        jsonDataHourFrame["predicted_close2"].append(
            {"time": time_unix, "value": predicted_close2}
        )
        jsonDataHourFrame["predicted_close3"].append(
            {"time": time_unix, "value": predicted_close3}
        )

    # Handle prediction for the next hour
    last_data_date = data.index[-1].date()

    # Convert end_date to a datetime object
    end_date_obj = datetime.combine(end_date, time(0, 0))

    # Create the datetime object for 9:15 AM UTC on the end_date
    date_time = datetime(
        year=end_date_obj.year,
        month=end_date_obj.month,
        day=end_date_obj.day,
        hour=9,
        minute=15,
        tzinfo=timezone.utc,
    )

    # Convert to Unix timestamp
    next_hour_unix = int(date_time.timestamp())

    if last_data_date == end_date_obj.date():
        # Adjust next hour Unix time within trading hours if the last data date matches the end date
        last_hour = data.index[-1].hour
        next_hour = last_hour + 1

        if next_hour >= 9 and next_hour < 15:  # within trading hours
            next_hour_unix = int(
                datetime.combine(
                    last_data_date, time(hour=next_hour, tzinfo=timezone.utc)
                ).timestamp()
            )
        else:  # wrap-around to the next trading day's first hour (9:15 AM)
            next_hour_unix = int(
                datetime.combine(
                    last_data_date + timedelta(days=1), time(9, 15, tzinfo=timezone.utc)
                ).timestamp()
            )
    else:
        # Set the next hour prediction to end_date + 9:15 AM if the end date does not match the last data date
        next_hour_unix = int(date_time.timestamp())

    # After determining the next hour Unix value, use the last six hours to predict
    six_hour_data = data.iloc[-6:]

    # Calculate sums for the last six hours
    sum_open = six_hour_data["Open"].sum()
    sum_high = six_hour_data["High"].sum()
    sum_low = six_hour_data["Low"].sum()
    sum_close = six_hour_data["Close"].sum()

    # Calculate DiffOH-LC
    diff_oh_lc = (sum_open + sum_high) - (sum_low + sum_close)

    # Calculate predicted values
    predicted_open1 = (sum_open / 6) + (diff_oh_lc / 3)
    predicted_open2 = (sum_open / 6) + (diff_oh_lc / 6)
    predicted_open3 = (sum_open / 6) + (diff_oh_lc / 9)

    predicted_high1 = (sum_high / 6) + (diff_oh_lc / 3)
    predicted_high2 = (sum_high / 6) + (diff_oh_lc / 6)
    predicted_high3 = (sum_high / 6) + (diff_oh_lc / 9)

    predicted_low1 = (sum_low / 6) + (diff_oh_lc / 3)
    predicted_low2 = (sum_low / 6) + (diff_oh_lc / 6)
    predicted_low3 = (sum_low / 6) + (diff_oh_lc / 9)

    predicted_close1 = (sum_close / 6) + (diff_oh_lc / 3)
    predicted_close2 = (sum_close / 6) + (diff_oh_lc / 6)
    predicted_close3 = (sum_close / 6) + (diff_oh_lc / 9)

    # Add predicted values to the JSON structure
    jsonDataHourFrame["predicted_open1"].append(
        {"time": next_hour_unix, "value": predicted_open1}
    )
    jsonDataHourFrame["predicted_open2"].append(
        {"time": next_hour_unix, "value": predicted_open2}
    )
    jsonDataHourFrame["predicted_open3"].append(
        {"time": next_hour_unix, "value": predicted_open3}
    )
    jsonDataHourFrame["predicted_high1"].append(
        {"time": next_hour_unix, "value": predicted_high1}
    )
    jsonDataHourFrame["predicted_high2"].append(
        {"time": next_hour_unix, "value": predicted_high2}
    )
    jsonDataHourFrame["predicted_high3"].append(
        {"time": next_hour_unix, "value": predicted_high3}
    )
    jsonDataHourFrame["predicted_low1"].append(
        {"time": next_hour_unix, "value": predicted_low1}
    )
    jsonDataHourFrame["predicted_low2"].append(
        {"time": next_hour_unix, "value": predicted_low2}
    )
    jsonDataHourFrame["predicted_low3"].append(
        {"time": next_hour_unix, "value": predicted_low3}
    )
    jsonDataHourFrame["predicted_close1"].append(
        {"time": next_hour_unix, "value": predicted_close1}
    )
    jsonDataHourFrame["predicted_close2"].append(
        {"time": next_hour_unix, "value": predicted_close2}
    )
    jsonDataHourFrame["predicted_close3"].append(
        {"time": next_hour_unix, "value": predicted_close3}
    )

    # # Identify matches within 5% for actual open value
    # def is_within_5_percent(actual, predicted):
    #     return abs((actual - predicted) / actual) <= 0.01

    # matches = []
    # for i in range(6, len(jsonDataHourFrame["candlestick"])):
    #     actual_open = jsonDataHourFrame["candlestick"][i]["open"]

    #     predicted_opens = [
    #         jsonDataHourFrame["predicted_open1"][i - 6]["value"],
    #         jsonDataHourFrame["predicted_open2"][i - 6]["value"],
    #         jsonDataHourFrame["predicted_open3"][i - 6]["value"],
    #     ]

    #     for predicted in predicted_opens:
    #         if is_within_5_percent(actual_open, predicted):
    #             match = {
    #                 "time": jsonDataHourFrame["candlestick"][i]["time"],
    #                 "actual_open": actual_open,
    #                 "predicted_open": predicted,
    #             }
    #             matches.append(match)
    # Identify matches and add to matches list
    for i in range(len(data)):
        actual_open = data.iloc[i]["Open"]
        time_unix = int(data.index[i].timestamp())

        # Check against predicted values for the current hour
        if len(jsonDataHourFrame["predicted_open1"]) > i:
            if abs(actual_open - jsonDataHourFrame["predicted_open1"][i]["value"]) / actual_open <= 0.01:
                jsonDataHourFrame["matches"].append(
                    {"time": time_unix, "value": jsonDataHourFrame["predicted_open1"][i]["value"]}
                )

            if abs(actual_open - jsonDataHourFrame["predicted_open2"][i]["value"]) / actual_open <= 0.01:
                jsonDataHourFrame["matches"].append(
                    {"time": time_unix, "value": jsonDataHourFrame["predicted_open2"][i]["value"]}
                )

            if abs(actual_open - jsonDataHourFrame["predicted_open3"][i]["value"]) / actual_open <= 0.01:
                jsonDataHourFrame["matches"].append(
                    {"time": time_unix, "value": jsonDataHourFrame["predicted_open3"][i]["value"]}
                )
    return jsonDataHourFrame


# Sidebar inputs
stock_ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., MARUTI.NS)", "FSL.NS")
start_date = st.sidebar.date_input("Start Date", datetime.strptime("2024-08-01", "%Y-%m-%d"))
end_date = st.sidebar.date_input("End Date", datetime.today())

if st.sidebar.button("Run Prediction"):
    # Call the function to perform predictions and get results
    jsonDataHourFrame = perform_hourly_prediction(
        stock_ticker, start_date, end_date
    )

    # Display the results
    st.json(jsonDataHourFrame)
    st.write("Matches within 5% for actual open value:")

# Fetch and display the candlestick chart
if stock_ticker and start_date and end_date:

    json_dataHour = perform_hourly_prediction(stock_ticker, start_date, end_date)
    json_strHour = json.dumps(json_dataHour, indent=4)
    chart_optionsHour = {
        "width": 600,  # Enlarged chart width
        "height": 400,  # Enlarged chart height
        "layout": {
            "background": {"type": "solid", "color": "white"},
            "textColor": "black",
        },
        "grid": {
            "vertLines": {"color": "rgba(197, 203, 206, 0.5)"},
            "horzLines": {"color": "rgba(197, 203, 206, 0.5)"},
        },
        "crosshair": {"mode": 0},
        "priceScale": {"borderColor": "rgba(197, 203, 206, 0.8)"},
        "timeScale": {
            "borderColor": "rgba(197, 203, 206, 0.8)",
            "barSpacing": 10,
            "minBarSpacing": 8,
            "timeVisible": True,
            "secondsVisible": False,
        },
    }

    # Subheader for the chart
    st.subheader("Predicted Values")
    # Horizontal alignment of checkboxes for Predicted Values - 1
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        show_open1 = st.checkbox("Open 1")
    with col2:
        show_high1 = st.checkbox("High 1")
    with col3:
        show_low1 = st.checkbox("Low 1")
    with col4:
        show_close1 = st.checkbox("Close 1")

        # Horizontal alignment of checkboxes for Predicted Values - 2
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        show_open2 = st.checkbox("Open 2")
    with col6:
        show_high2 = st.checkbox("High 2")
    with col7:
        show_low2 = st.checkbox("Low 2")
    with col8:
        show_close2 = st.checkbox("Close 2")

    # Horizontal alignment of checkboxes for Predicted Values - 3
    col9, col10, col11, col12, col13 = st.columns(5)
    with col9:
        show_open3 = st.checkbox("Open 3")
    with col10:
        show_high3 = st.checkbox("High 3")
    with col11:
        show_low3 = st.checkbox("Low 3")
    with col12:
        show_close3 = st.checkbox("Close 3")
    with col13:  # New column for Matches checkbox
        show_matches = st.checkbox("Show Matches")
        # Prepare the candlestick series
    series_chartHour = [
        {
            "type": "Candlestick",
            "data": json_dataHour["candlestick"],
            "options": {
                "upColor": "#26a69a",
                "downColor": "#ef5350",
                "borderVisible": False,
                "wickUpColor": "#26a69a",
                "wickDownColor": "#ef5350",
            },
        }
    ]

    # Add the selected predicted values to the chart
    if show_open1:
        series_chartHour.append(
            {
                "type": "Line",
                "data": json_dataHour["predicted_open1"],
                "options": {"color": "blue", "title": "Predicted Open 1"},
            }
        )

    if show_high1:
        series_chartHour.append(
            {
                "type": "Line",
                "data": json_dataHour["predicted_high1"],
                "options": {"color": "purple", "title": "Predicted High 1"},
            }
        )

    if show_low1:
        series_chartHour.append(
            {
                "type": "Line",
                "data": json_dataHour["predicted_low1"],
                "options": {"color": "cyan", "title": "Predicted Low 1"},
            }
        )

    if show_close1:
        series_chartHour.append(
            {
                "type": "Line",
                "data": json_dataHour["predicted_close1"],
                "options": {"color": "teal", "title": "Predicted Close 1"},
            }
        )

    if show_open2:
        series_chartHour.append(
            {
                "type": "Line",
                "data": json_dataHour["predicted_open2"],
                "options": {"color": "green", "title": "Predicted Open 2"},
            }
        )

    if show_high2:
        series_chartHour.append(
            {
                "type": "Line",
                "data": json_dataHour["predicted_high2"],
                "options": {"color": "orange", "title": "Predicted High 2"},
            }
        )

    if show_low2:
        series_chartHour.append(
            {
                "type": "Line",
                "data": json_dataHour["predicted_low2"],
                "options": {"color": "yellow", "title": "Predicted Low 2"},
            }
        )

    if show_close2:
        series_chartHour.append(
            {
                "type": "Line",
                "data": json_dataHour["predicted_close2"],
                "options": {"color": "pink", "title": "Predicted Close 2"},
            }
        )

    if show_open3:
        series_chartHour.append(
            {
                "type": "Line",
                "data": json_dataHour["predicted_open3"],
                "options": {"color": "red", "title": "Predicted Open 3"},
            }
        )

    if show_high3:
        series_chartHour.append(
            {
                "type": "Line",
                "data": json_dataHour["predicted_high3"],
                "options": {"color": "magenta", "title": "Predicted High 3"},
            }
        )

    if show_low3:
        series_chartHour.append(
            {
                "type": "Line",
                "data": json_dataHour["predicted_low3"],
                "options": {"color": "brown", "title": "Predicted Low 3"},
            }
        )

    if show_close3:
        series_chartHour.append(
            {
                "type": "Line",
                "data": json_dataHour["predicted_close3"],
                "options": {"color": "gray", "title": "Predicted Close 3"},
            }
        )

        # Render the combined chart
    renderLightweightCharts(
        [
            {
                "series": series_chartHour,
                "chart": chart_optionsHour,
            }
        ],
        "candlestick_combined",
    )

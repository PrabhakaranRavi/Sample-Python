import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import datetime
import json

# Set the refresh interval in seconds (e.g., 60 seconds)
refresh_interval = 5

# Embed the JavaScript in Streamlit for auto-refresh
st.markdown(f"""
    <script>
        function refreshPage() {{
            setTimeout(function() {{
                window.location.reload(1);
            }}, {refresh_interval * 1000});
        }}
        refreshPage();
    </script>
    """, unsafe_allow_html=True)

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
    end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    year = end_date_obj.year
    month = end_date_obj.month
    day = end_date_obj.day
    date_time = datetime.datetime(year, month, day, 9, 15, 0, tzinfo=datetime.timezone.utc)
    next_hour_unix = int(date_time.timestamp())
    if last_data_date == end_date_obj.date():
        last_hour = data.index[-1].hour
        next_hour = last_hour + 1

        if next_hour >= 9 and next_hour < 15:
            next_hour_unix = int(
                datetime.datetime.combine(last_data_date, datetime.time(hour=next_hour, tzinfo=datetime.timezone.utc)).timestamp()
            )
        else:
            next_hour_unix = int(
                datetime.datetime.combine(last_data_date + datetime.timedelta(days=1), datetime.time(9, 15, tzinfo=datetime.timezone.utc)).timestamp()
            )
    else:
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

    # Identify matches within 5% for actual open value
    def is_within_5_percent(actual, predicted):
        return abs((actual - predicted) / actual) <= 0.01

    matches = []
    for i in range(6, len(jsonDataHourFrame["candlestick"])):
        actual_open = jsonDataHourFrame["candlestick"][i]["open"]

        predicted_opens = [
            jsonDataHourFrame["predicted_open1"][i - 6]["value"],
            jsonDataHourFrame["predicted_open2"][i - 6]["value"],
            jsonDataHourFrame["predicted_open3"][i - 6]["value"],
        ]

        for predicted in predicted_opens:
            if is_within_5_percent(actual_open, predicted):
                match = {
                    "time": jsonDataHourFrame["candlestick"][i]["time"],
                    "actual_open": actual_open,
                    "predicted_open": predicted,
                }
                matches.append(match)

    return jsonDataHourFrame, matches


# Streamlit UI
st.title("Stock OHLC Prediction")

# Input fields
ticker = st.text_input("Enter stock ticker")
start_date = st.date_input("Select start date")
end_date = st.date_input("Select end date")

if st.button("Run Prediction"):
    # Call the function to perform predictions and get results
    jsonDataHourFrame, matches = perform_hourly_prediction(
        ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    )

    # Display the results
    st.json(jsonDataHourFrame)
    st.write("Matches within 5% for actual open value:")
    st.json(matches)

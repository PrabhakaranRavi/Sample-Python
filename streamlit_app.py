# import streamlit as st
# import yfinance as yf
# from datetime import datetime, timezone, time, timedelta
# import json
# from streamlit_lightweight_charts import renderLightweightCharts

# # Set the refresh interval in seconds (e.g., 60 seconds)
# refresh_interval = 5

# # Embed the JavaScript in Streamlit for auto-refresh
# st.markdown(
#     f"""
#     <script>
#         function refreshPage() {{
#             setTimeout(function() {{
#                 window.location.reload(1);
#             }}, {refresh_interval * 1000});
#         }}
#         refreshPage();
#     </script>
#     """,
#     unsafe_allow_html=True,
# )


# # Function to perform the calculation and generate the JSON data
# def perform_hourly_prediction(ticker, start_date, end_date):
#     data = yf.download(ticker, start=start_date, interval="60m")
#     data = data.drop(columns=["Adj Close", "Volume"])

#     # Initialize JSON structure
#     jsonDataHourFrame = {
#         "candlestick": [],
#         "predicted_open1": [],
#         "predicted_open2": [],
#         "predicted_open3": [],
#         "predicted_high1": [],
#         "predicted_high2": [],
#         "predicted_high3": [],
#         "predicted_low1": [],
#         "predicted_low2": [],
#         "predicted_low3": [],
#         "predicted_close1": [],
#         "predicted_close2": [],
#         "predicted_close3": [],
#         "matches": []
#     }

#     # Push all candlestick data before the loop
#     for i in range(len(data)):
#         current_data = data.iloc[i]

#         # Convert current time to Unix
#         time_unix = int(current_data.name.timestamp())

#         # Add the current hour's actual OHLC to the candlestick data
#         jsonDataHourFrame["candlestick"].append(
#             {
#                 "time": time_unix,
#                 "open": current_data["Open"],
#                 "high": current_data["High"],
#                 "low": current_data["Low"],
#                 "close": current_data["Close"],
#             }
#         )

#     # Loop through data to calculate predictions
#     for i in range(6, len(data)):
#         # Use first six hours to predict the next hour
#         six_hour_data = data.iloc[i - 6 : i]

#         next_hour_data = data.iloc[i]
#         # Convert next hour time to Unix
#         time_unix = int(next_hour_data.name.timestamp())

#         # Calculate sums for the first six hours
#         sum_open = six_hour_data["Open"].sum()
#         sum_high = six_hour_data["High"].sum()
#         sum_low = six_hour_data["Low"].sum()
#         sum_close = six_hour_data["Close"].sum()

#         # Calculate DiffOH-LC
#         diff_oh_lc = (sum_open + sum_high) - (sum_low + sum_close)

#         # Calculate predicted values
#         predicted_open1 = (sum_open / 6) + (diff_oh_lc / 30)
#         predicted_open2 = (sum_open / 6) + (diff_oh_lc / 60)
#         predicted_open3 = (sum_open / 6) + (diff_oh_lc / 90)

#         predicted_high1 = (sum_high / 6) + (diff_oh_lc / 30)
#         predicted_high2 = (sum_high / 6) + (diff_oh_lc / 60)
#         predicted_high3 = (sum_high / 6) + (diff_oh_lc / 90)

#         predicted_low1 = (sum_low / 6) + (diff_oh_lc / 3)
#         predicted_low2 = (sum_low / 6) + (diff_oh_lc / 6)
#         predicted_low3 = (sum_low / 6) + (diff_oh_lc / 9)

#         predicted_close1 = (sum_close / 6) + (diff_oh_lc / 3)
#         predicted_close2 = (sum_close / 6) + (diff_oh_lc / 6)
#         predicted_close3 = (sum_close / 6) + (diff_oh_lc / 9)

#         # Add predicted values to the JSON structure
#         jsonDataHourFrame["predicted_open1"].append(
#             {"time": time_unix, "value": predicted_open1}
#         )
#         jsonDataHourFrame["predicted_open2"].append(
#             {"time": time_unix, "value": predicted_open2}
#         )
#         jsonDataHourFrame["predicted_open3"].append(
#             {"time": time_unix, "value": predicted_open3}
#         )
#         jsonDataHourFrame["predicted_high1"].append(
#             {"time": time_unix, "value": predicted_high1}
#         )
#         jsonDataHourFrame["predicted_high2"].append(
#             {"time": time_unix, "value": predicted_high2}
#         )
#         jsonDataHourFrame["predicted_high3"].append(
#             {"time": time_unix, "value": predicted_high3}
#         )
#         jsonDataHourFrame["predicted_low1"].append(
#             {"time": time_unix, "value": predicted_low1}
#         )
#         jsonDataHourFrame["predicted_low2"].append(
#             {"time": time_unix, "value": predicted_low2}
#         )
#         jsonDataHourFrame["predicted_low3"].append(
#             {"time": time_unix, "value": predicted_low3}
#         )
#         jsonDataHourFrame["predicted_close1"].append(
#             {"time": time_unix, "value": predicted_close1}
#         )
#         jsonDataHourFrame["predicted_close2"].append(
#             {"time": time_unix, "value": predicted_close2}
#         )
#         jsonDataHourFrame["predicted_close3"].append(
#             {"time": time_unix, "value": predicted_close3}
#         )

#     # Handle prediction for the next hour
#     last_data_date = data.index[-1].date()

#     # Convert end_date to a datetime object
#     end_date_obj = datetime.combine(end_date, time(0, 0))

#     # Create the datetime object for 9:15 AM UTC on the end_date
#     date_time = datetime(
#         year=end_date_obj.year,
#         month=end_date_obj.month,
#         day=end_date_obj.day,
#         hour=9,
#         minute=15,
#         tzinfo=timezone.utc,
#     )

#     # Convert to Unix timestamp
#     next_hour_unix = int(date_time.timestamp())

#     if last_data_date == end_date_obj.date():
#         # Adjust next hour Unix time within trading hours if the last data date matches the end date
#         last_hour = data.index[-1].hour
#         next_hour = last_hour + 1

#         if next_hour >= 9 and next_hour < 15:  # within trading hours
#             next_hour_unix = int(
#                 datetime.combine(
#                     last_data_date, time(hour=next_hour, tzinfo=timezone.utc)
#                 ).timestamp()
#             )
#         else:  # wrap-around to the next trading day's first hour (9:15 AM)
#             next_hour_unix = int(
#                 datetime.combine(
#                     last_data_date + timedelta(days=1), time(9, 15, tzinfo=timezone.utc)
#                 ).timestamp()
#             )
#     else:
#         # Set the next hour prediction to end_date + 9:15 AM if the end date does not match the last data date
#         next_hour_unix = int(date_time.timestamp())

#     # After determining the next hour Unix value, use the last six hours to predict
#     six_hour_data = data.iloc[-6:]

#     # Calculate sums for the last six hours
#     sum_open = six_hour_data["Open"].sum()
#     sum_high = six_hour_data["High"].sum()
#     sum_low = six_hour_data["Low"].sum()
#     sum_close = six_hour_data["Close"].sum()

#     # Calculate DiffOH-LC
#     diff_oh_lc = (sum_open + sum_high) - (sum_low + sum_close)

#     # Calculate predicted values
#     predicted_open1 = (sum_open / 6) + (diff_oh_lc / 3)
#     predicted_open2 = (sum_open / 6) + (diff_oh_lc / 6)
#     predicted_open3 = (sum_open / 6) + (diff_oh_lc / 9)

#     predicted_high1 = (sum_high / 6) + (diff_oh_lc / 3)
#     predicted_high2 = (sum_high / 6) + (diff_oh_lc / 6)
#     predicted_high3 = (sum_high / 6) + (diff_oh_lc / 9)

#     predicted_low1 = (sum_low / 6) + (diff_oh_lc / 3)
#     predicted_low2 = (sum_low / 6) + (diff_oh_lc / 6)
#     predicted_low3 = (sum_low / 6) + (diff_oh_lc / 9)

#     predicted_close1 = (sum_close / 6) + (diff_oh_lc / 3)
#     predicted_close2 = (sum_close / 6) + (diff_oh_lc / 6)
#     predicted_close3 = (sum_close / 6) + (diff_oh_lc / 9)

#     # Add predicted values to the JSON structure
#     jsonDataHourFrame["predicted_open1"].append(
#         {"time": next_hour_unix, "value": predicted_open1}
#     )
#     jsonDataHourFrame["predicted_open2"].append(
#         {"time": next_hour_unix, "value": predicted_open2}
#     )
#     jsonDataHourFrame["predicted_open3"].append(
#         {"time": next_hour_unix, "value": predicted_open3}
#     )
#     jsonDataHourFrame["predicted_high1"].append(
#         {"time": next_hour_unix, "value": predicted_high1}
#     )
#     jsonDataHourFrame["predicted_high2"].append(
#         {"time": next_hour_unix, "value": predicted_high2}
#     )
#     jsonDataHourFrame["predicted_high3"].append(
#         {"time": next_hour_unix, "value": predicted_high3}
#     )
#     jsonDataHourFrame["predicted_low1"].append(
#         {"time": next_hour_unix, "value": predicted_low1}
#     )
#     jsonDataHourFrame["predicted_low2"].append(
#         {"time": next_hour_unix, "value": predicted_low2}
#     )
#     jsonDataHourFrame["predicted_low3"].append(
#         {"time": next_hour_unix, "value": predicted_low3}
#     )
#     jsonDataHourFrame["predicted_close1"].append(
#         {"time": next_hour_unix, "value": predicted_close1}
#     )
#     jsonDataHourFrame["predicted_close2"].append(
#         {"time": next_hour_unix, "value": predicted_close2}
#     )
#     jsonDataHourFrame["predicted_close3"].append(
#         {"time": next_hour_unix, "value": predicted_close3}
#     )

#     # # Identify matches within 5% for actual open value
#     # def is_within_5_percent(actual, predicted):
#     #     return abs((actual - predicted) / actual) <= 0.01

#     # matches = []
#     # for i in range(6, len(jsonDataHourFrame["candlestick"])):
#     #     actual_open = jsonDataHourFrame["candlestick"][i]["open"]

#     #     predicted_opens = [
#     #         jsonDataHourFrame["predicted_open1"][i - 6]["value"],
#     #         jsonDataHourFrame["predicted_open2"][i - 6]["value"],
#     #         jsonDataHourFrame["predicted_open3"][i - 6]["value"],
#     #     ]

#     #     for predicted in predicted_opens:
#     #         if is_within_5_percent(actual_open, predicted):
#     #             match = {
#     #                 "time": jsonDataHourFrame["candlestick"][i]["time"],
#     #                 "actual_open": actual_open,
#     #                 "predicted_open": predicted,
#     #             }
#     #             matches.append(match)
#     # Identify matches and add to matches list
#     for i in range(len(data)):
#         actual_open = data.iloc[i]["Open"]
#         time_unix = int(data.index[i].timestamp())

#         # Check against predicted values for the current hour
#         if len(jsonDataHourFrame["predicted_open1"]) > i:
#             if abs(actual_open - jsonDataHourFrame["predicted_open1"][i]["value"]) / actual_open <= 0.01:
#                 jsonDataHourFrame["matches"].append(
#                     {"time": time_unix, "value": jsonDataHourFrame["predicted_open1"][i]["value"]}
#                 )

#             if abs(actual_open - jsonDataHourFrame["predicted_open2"][i]["value"]) / actual_open <= 0.01:
#                 jsonDataHourFrame["matches"].append(
#                     {"time": time_unix, "value": jsonDataHourFrame["predicted_open2"][i]["value"]}
#                 )

#             if abs(actual_open - jsonDataHourFrame["predicted_open3"][i]["value"]) / actual_open <= 0.01:
#                 jsonDataHourFrame["matches"].append(
#                     {"time": time_unix, "value": jsonDataHourFrame["predicted_open3"][i]["value"]}
#                 )
#     return jsonDataHourFrame


# # Sidebar inputs
# stock_ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., MARUTI.NS)", "FSL.NS")
# start_date = st.sidebar.date_input("Start Date", datetime.strptime("2024-08-01", "%Y-%m-%d"))
# end_date = st.sidebar.date_input("End Date", datetime.today())

# if st.sidebar.button("Run Prediction"):
#     # Call the function to perform predictions and get results
#     jsonDataHourFrame = perform_hourly_prediction(
#         stock_ticker, start_date, end_date
#     )

#     # Display the results
#     st.json(jsonDataHourFrame)
#     st.write("Matches within 5% for actual open value:")

# # Fetch and display the candlestick chart
# if stock_ticker and start_date and end_date:

#     json_dataHour = perform_hourly_prediction(stock_ticker, start_date, end_date)
#     json_strHour = json.dumps(json_dataHour, indent=4)
#     chart_optionsHour = {
#         "width": 600,  # Enlarged chart width
#         "height": 400,  # Enlarged chart height
#         "layout": {
#             "background": {"type": "solid", "color": "white"},
#             "textColor": "black",
#         },
#         "grid": {
#             "vertLines": {"color": "rgba(197, 203, 206, 0.5)"},
#             "horzLines": {"color": "rgba(197, 203, 206, 0.5)"},
#         },
#         "crosshair": {"mode": 0},
#         "priceScale": {"borderColor": "rgba(197, 203, 206, 0.8)"},
#         "timeScale": {
#             "borderColor": "rgba(197, 203, 206, 0.8)",
#             "barSpacing": 10,
#             "minBarSpacing": 8,
#             "timeVisible": True,
#             "secondsVisible": False,
#         },
#     }

#     # Subheader for the chart
#     st.subheader("Predicted Values")
#     # Horizontal alignment of checkboxes for Predicted Values - 1
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         show_open1 = st.checkbox("Open 1")
#     with col2:
#         show_high1 = st.checkbox("High 1")
#     with col3:
#         show_low1 = st.checkbox("Low 1")
#     with col4:
#         show_close1 = st.checkbox("Close 1")

#         # Horizontal alignment of checkboxes for Predicted Values - 2
#     col5, col6, col7, col8 = st.columns(4)
#     with col5:
#         show_open2 = st.checkbox("Open 2")
#     with col6:
#         show_high2 = st.checkbox("High 2")
#     with col7:
#         show_low2 = st.checkbox("Low 2")
#     with col8:
#         show_close2 = st.checkbox("Close 2")

#     # Horizontal alignment of checkboxes for Predicted Values - 3
#     col9, col10, col11, col12, col13 = st.columns(5)
#     with col9:
#         show_open3 = st.checkbox("Open 3")
#     with col10:
#         show_high3 = st.checkbox("High 3")
#     with col11:
#         show_low3 = st.checkbox("Low 3")
#     with col12:
#         show_close3 = st.checkbox("Close 3")
#     with col13:  # New column for Matches checkbox
#         show_matches = st.checkbox("Matches")
#         # Prepare the candlestick series
#     series_chartHour = [
#         {
#             "type": "Candlestick",
#             "data": json_dataHour["candlestick"],
#             "options": {
#                 "upColor": "#26a69a",
#                 "downColor": "#ef5350",
#                 "borderVisible": False,
#                 "wickUpColor": "#26a69a",
#                 "wickDownColor": "#ef5350",
#             },
#         }
#     ]

#     # Add the selected predicted values to the chart
#     if show_open1:
#         series_chartHour.append(
#             {
#                 "type": "Line",
#                 "data": json_dataHour["predicted_open1"],
#                 "options": {"color": "blue", "title": "Predicted Open 1"},
#             }
#         )

#     if show_high1:
#         series_chartHour.append(
#             {
#                 "type": "Line",
#                 "data": json_dataHour["predicted_high1"],
#                 "options": {"color": "purple", "title": "Predicted High 1"},
#             }
#         )

#     if show_low1:
#         series_chartHour.append(
#             {
#                 "type": "Line",
#                 "data": json_dataHour["predicted_low1"],
#                 "options": {"color": "cyan", "title": "Predicted Low 1"},
#             }
#         )

#     if show_close1:
#         series_chartHour.append(
#             {
#                 "type": "Line",
#                 "data": json_dataHour["predicted_close1"],
#                 "options": {"color": "teal", "title": "Predicted Close 1"},
#             }
#         )

#     if show_open2:
#         series_chartHour.append(
#             {
#                 "type": "Line",
#                 "data": json_dataHour["predicted_open2"],
#                 "options": {"color": "green", "title": "Predicted Open 2"},
#             }
#         )

#     if show_high2:
#         series_chartHour.append(
#             {
#                 "type": "Line",
#                 "data": json_dataHour["predicted_high2"],
#                 "options": {"color": "orange", "title": "Predicted High 2"},
#             }
#         )

#     if show_low2:
#         series_chartHour.append(
#             {
#                 "type": "Line",
#                 "data": json_dataHour["predicted_low2"],
#                 "options": {"color": "yellow", "title": "Predicted Low 2"},
#             }
#         )

#     if show_close2:
#         series_chartHour.append(
#             {
#                 "type": "Line",
#                 "data": json_dataHour["predicted_close2"],
#                 "options": {"color": "pink", "title": "Predicted Close 2"},
#             }
#         )

#     if show_open3:
#         series_chartHour.append(
#             {
#                 "type": "Line",
#                 "data": json_dataHour["predicted_open3"],
#                 "options": {"color": "red", "title": "Predicted Open 3"},
#             }
#         )

#     if show_high3:
#         series_chartHour.append(
#             {
#                 "type": "Line",
#                 "data": json_dataHour["predicted_high3"],
#                 "options": {"color": "magenta", "title": "Predicted High 3"},
#             }
#         )

#     if show_low3:
#         series_chartHour.append(
#             {
#                 "type": "Line",
#                 "data": json_dataHour["predicted_low3"],
#                 "options": {"color": "brown", "title": "Predicted Low 3"},
#             }
#         )

#     if show_close3:
#         series_chartHour.append(
#             {
#                 "type": "Line",
#                 "data": json_dataHour["predicted_close3"],
#                 "options": {"color": "gray", "title": "Predicted Close 3"},
#             }
#         )
#     if show_matches:
#         series_chartHour.append(
#             {
#                 "type": "Line",
#                 "data": json_dataHour["matches"],
#                 "options": {"color": "gray", "title": "Matches Open"},
#             }
#         )
#         # Render the combined chart
#     renderLightweightCharts(
#         [
#             {
#                 "series": series_chartHour,
#                 "chart": chart_optionsHour,
#             }
#         ],
#         "candlestick_combined",
#     )

#     # Additional chart for matches
#     if show_matches:
#         # Prepare match data for highlighting
#         match_highlight_data = []
#         for match in json_dataHour["matches"]:
#             match_highlight_data.append({
#                 "time": match["time"],
#                 "value": match["value"],
#                 "color": "black",
#                 "size": 5
#             })

#         # Prepare the new chart options for the match highlights
#         match_chart_options = {
#             "width": 600,
#             "height": 400,
#             "layout": {
#                 "background": {"type": "solid", "color": "white"},
#                 "textColor": "black",
#             },
#             "grid": {
#                 "vertLines": {"color": "rgba(197, 203, 206, 0.5)"},
#                 "horzLines": {"color": "rgba(197, 203, 206, 0.5)"},
#             },
#             "crosshair": {"mode": 0},
#             "priceScale": {"borderColor": "rgba(197, 203, 206, 0.8)"},
#             "timeScale": {
#                 "borderColor": "rgba(197, 203, 206, 0.8)",
#                 "barSpacing": 10,
#                 "minBarSpacing": 8,
#                 "timeVisible": True,
#                 "secondsVisible": False,
#             },
#         }

#         # Prepare the series for the matches
#         match_series = [
#             {
#                 "type": "Candlestick",
#                 "data": json_dataHour["candlestick"],
#                 "options": {
#                     "upColor": "#26a69a",
#                     "downColor": "#ef5350",
#                     "borderVisible": False,
#                     "wickUpColor": "#26a69a",
#                     "wickDownColor": "#ef5350",
#                 },
#             },
#             {
#                 "type": "Scatter",
#                 "data": match_highlight_data,
#                 "options": {"color": "black", "title": "Matches Open", "lineWidth": 0, "dotSize": 5},
#             }
#         ]

#         # Render the chart with matches highlighted
#         renderLightweightCharts(
#             [
#                 {
#                     "series": match_series,
#                     "chart": match_chart_options,
#                 }
#             ],
#             "matches_highlighted_chart",
#         )

import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timezone, time, timedelta
from streamlit_lightweight_charts import renderLightweightCharts
import json

# Sidebar inputs
stock_ticker = st.sidebar.text_input(
    "Enter Stock Ticker (e.g., MARUTI.NS)", "FSL.NS"
)
start_date = st.sidebar.date_input("Start Date", datetime.strptime("2024-08-01", "%Y-%m-%d"))
end_date = st.sidebar.date_input("End Date", datetime.today())

custom_start = st.sidebar.date_input(
    "Custom Start", datetime.strptime("2024-08-19", "%Y-%m-%d")
)
custom_end = st.sidebar.date_input(
    "Custom End", datetime.strptime("2024-08-27", "%Y-%m-%d")
)

start_30d = st.sidebar.date_input(
    "30D Start", datetime.strptime("2024-07-12", "%Y-%m-%d")
)
end_30d = st.sidebar.date_input("30D End", datetime.strptime("2024-08-27", "%Y-%m-%d"))

start_12w = st.sidebar.date_input(
    "12W Start", datetime.strptime("2024-06-03", "%Y-%m-%d")
)
end_12w = st.sidebar.date_input("12W End", datetime.strptime("2024-08-24", "%Y-%m-%d"))

start_6m = st.sidebar.date_input(
    "6M Start", datetime.strptime("2024-02-01", "%Y-%m-%d")
)
end_6m = st.sidebar.date_input("6M End", datetime.strptime("2024-07-31", "%Y-%m-%d"))


# Function to remove entries with null values
def remove_null_values(data):
    return [entry for entry in data if entry["value"] is not None]


# Function to format DataFrame with 2 decimal places
def format_dataframe(df):
    return df.applymap(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)


# Function to prepare line chart data
def prepare_line_chart_data(data):
    return [
        {"time": date, "value": round(values["Day_HL Diff"], 2)}
        for date, values in data["OHLCValues"].items()
    ]


# Extract and format OHLC values
def format_ohlc_values(data, key):
    formatted_data = []

    # Extract the key for the 'HL Diff' based on the time period
    hl_diff_key = None
    if key == "Last6Days":
        hl_diff_key = "Day_HL Diff"
    elif key == "Last30Days":
        hl_diff_key = "Day_HL Diff"
    elif key == "Last12Weeks":
        hl_diff_key = "Week_HL Diff"
    elif key == "Last6Months":
        hl_diff_key = "Month_HL Diff"

    if hl_diff_key is None:
        st.error("Invalid key provided.")
        return formatted_data

    # Format OHLC values
    for date, values in data[key]["OHLCValues"].items():
        hl_diff_value = values.get(hl_diff_key)
        if hl_diff_value is not None:
            formatted_data.append({"time": date, "value": hl_diff_value})

    return formatted_data


# Function to perform the calculation and generate the JSON data
def perform_calculation(ticker, start_date, end_date):
    # Download hourly data
    data = yf.download(ticker, start=start_date, interval="60m")

    data = data[data.index.hour < 15].copy()
    data["Stock"] = ticker
    data["Date"] = data.index.date
    data["Time"] = data.index.time
    data = data.drop(columns=["Adj Close", "Volume"])

    # Group by the date and calculate daily sums
    daily_sums = data.drop(columns=["Time", "Stock"]).groupby("Date").sum()
    daily_sums = daily_sums.rename(
        columns={
            "Open": "SumOpen",
            "High": "SumHigh",
            "Low": "SumLow",
            "Close": "SumClose",
        }
    )

    # Calculate HighDiv, LowDiv, and DiffOH-LC
    daily_sums["HighDiv"] = daily_sums["SumHigh"] / 6
    daily_sums["LowDiv"] = daily_sums["SumLow"] / 6
    daily_sums["DiffOH-LC"] = (daily_sums["SumOpen"] + daily_sums["SumHigh"]) - (
        daily_sums["SumLow"] + daily_sums["SumClose"]
    )

    # Calculate TS1, TS2, TS3, TR1, TR2, TR3
    daily_sums["TS1"] = daily_sums["HighDiv"] + (daily_sums["DiffOH-LC"] / 3)
    daily_sums["TS2"] = daily_sums["HighDiv"] + (daily_sums["DiffOH-LC"] / 6)
    daily_sums["TS3"] = daily_sums["HighDiv"] + (daily_sums["DiffOH-LC"] / 9)
    daily_sums["TR1"] = daily_sums["LowDiv"] - (daily_sums["DiffOH-LC"] / 3)
    daily_sums["TR2"] = daily_sums["LowDiv"] - (daily_sums["DiffOH-LC"] / 6)
    daily_sums["TR3"] = daily_sums["LowDiv"] - (daily_sums["DiffOH-LC"] / 9)

    # Merge daily sums with daily data
    daily_data = yf.download(ticker, start=start_date, interval="1d")
    daily_data = daily_data.drop(columns=["Adj Close", "Volume"])
    daily_data["Date"] = daily_data.index.date

    # Add TS and TR values from daily_sums shifted by one day
    daily_data["TS1"] = np.nan
    daily_data["TS2"] = np.nan
    daily_data["TS3"] = np.nan
    daily_data["TR1"] = np.nan
    daily_data["TR2"] = np.nan
    daily_data["TR3"] = np.nan

    daily_dates = daily_data["Date"].values

    for i in range(0, len(daily_sums) - 1):
        date = daily_sums.index[i]
        dailyDateForShift = daily_dates[i + 1]
        ts_tr_values = daily_sums.loc[date, ["TS1", "TS2", "TS3", "TR1", "TR2", "TR3"]]
        daily_data.loc[
            daily_data["Date"] == dailyDateForShift,
            ["TS1", "TS2", "TS3", "TR1", "TR2", "TR3"],
        ] = ts_tr_values.values

    # Drop the Date column
    daily_data.set_index("Date", inplace=True)

    # Last 6 Days
    data_6days = yf.download(ticker, start=custom_start, end=custom_end, interval="1d")
    data_6days["Day_HL Diff"] = data_6days["High"] - data_6days["Low"]
    last_6_days_avg_hl_diff = data_6days["Day_HL Diff"][-6:].sum() / 6
    last_6_days_avg_hl_diff = round(last_6_days_avg_hl_diff, 2)
    data_6days = data_6days.drop(columns=["Adj Close", "Volume"])
    data_6days.index = data_6days.index.strftime("%Y-%m-%d")
    last_6_days_ohlc = data_6days.to_dict(orient="index")

    # Last 30 Days
    data_30days = yf.download(ticker, start=start_30d, end=end_30d, interval="1d")
    data_30days["Day_HL Diff"] = data_30days["High"] - data_30days["Low"]
    last_30_days_avg_hl_diff = data_30days["Day_HL Diff"][-30:].sum() / 30
    last_30_days_avg_hl_diff = round(last_30_days_avg_hl_diff, 2)
    data_30days = data_30days.drop(columns=["Adj Close", "Volume"])
    data_30days.index = data_30days.index.strftime("%Y-%m-%d")
    last_30_days_ohlc = data_30days.to_dict(orient="index")

    # Last 12 Weeks
    data_12weeks = yf.download(ticker, start=start_12w, end=end_12w, interval="1wk")
    data_12weeks["Week_HL Diff"] = data_12weeks["High"] - data_12weeks["Low"]
    last_12_weeks_avg_hl_diff = data_12weeks["Week_HL Diff"].sum() / 12
    last_12_weeks_avg_hl_diff = round(last_12_weeks_avg_hl_diff, 2)
    data_12weeks = data_12weeks.drop(columns=["Adj Close", "Volume"])
    data_12weeks.index = data_12weeks.index.strftime("%Y-%m-%d")
    last_12_weeks_ohlc = data_12weeks.to_dict(orient="index")

    # Last 6 Months
    data_6months = yf.download(ticker, start=start_6m, end=end_6m, interval="1mo")
    data_6months["Month_HL Diff"] = data_6months["High"] - data_6months["Low"]
    last_6_months_avg_hl_diff = data_6months["Month_HL Diff"].sum() / 6
    last_6_months_avg_hl_diff = round(last_6_months_avg_hl_diff, 2)
    data_6months = data_6months.drop(columns=["Adj Close", "Volume"])
    data_6months.index = data_6months.index.strftime("%Y-%m-%d")
    last_6_months_ohlc = data_6months.to_dict(orient="index")

    # Get Market Capital, EPS, PE Ratio, Outstanding Shares, previousClose, floatShares, currentPrice, and revenuePerShare
    ticker_info = yf.Ticker(ticker)
    info = ticker_info.info
    market_cap = info.get("marketCap", "N/A")
    eps = info.get("trailingEps", "N/A")
    pe_ratio = info.get("trailingPE", "N/A")
    outstanding_shares = info.get("sharesOutstanding", "N/A")
    previous_close = info.get("previousClose", "N/A")
    float_shares = info.get("floatShares", "N/A")
    current_price = info.get("currentPrice", "N/A")
    revenue_per_share = info.get("revenuePerShare", "N/A")

    # Convert data to JSON format
    json_data = {
        "candlestick": [],
        "ts1": [],
        "ts2": [],
        "ts3": [],
        "tr1": [],
        "tr2": [],
        "tr3": [],
        "open": [],
        "high": [],
        "low": [],
        "close": [],
        "Last6Days": {"OHLCValues": last_6_days_ohlc, "Avg": last_6_days_avg_hl_diff},
        "Last30Days": {
            "OHLCValues": last_30_days_ohlc,
            "Avg": last_30_days_avg_hl_diff,
        },
        "Last12Weeks": {
            "OHLCValues": last_12_weeks_ohlc,
            "Avg": last_12_weeks_avg_hl_diff,
        },
        "Last6Months": {
            "OHLCValues": last_6_months_ohlc,
            "Avg": last_6_months_avg_hl_diff,
        },
        "Market_Capital": market_cap,
        "EPS": eps,
        "PE_Ratio": pe_ratio,
        "Outstanding_Shares": outstanding_shares,
        "Previous_Close": previous_close,
        "Float_Shares": float_shares,
        "Current_Price": current_price,
        "Revenue_Per_Share": revenue_per_share,
    }

    for row in daily_data.itertuples():
        time_unix = int(datetime.combine(row.Index, datetime.min.time()).timestamp())
        json_data["candlestick"].append(
            {
                "time": time_unix,
                "open": row.Open if not np.isnan(row.Open) else None,
                "high": row.High if not np.isnan(row.High) else None,
                "low": row.Low if not np.isnan(row.Low) else None,
                "close": row.Close if not np.isnan(row.Close) else None,
            }
        )
        json_data["ts1"].append(
            {
                "time": row.Index.strftime("%Y-%m-%d"),
                "value": row.TS1 if not np.isnan(row.TS1) else None,
            }
        )
        json_data["ts2"].append(
            {
                "time": row.Index.strftime("%Y-%m-%d"),
                "value": row.TS2 if not np.isnan(row.TS2) else None,
            }
        )
        json_data["ts3"].append(
            {
                "time": row.Index.strftime("%Y-%m-%d"),
                "value": row.TS3 if not np.isnan(row.TS3) else None,
            }
        )
        json_data["tr1"].append(
            {
                "time": row.Index.strftime("%Y-%m-%d"),
                "value": row.TR1 if not np.isnan(row.TR1) else None,
            }
        )
        json_data["tr2"].append(
            {
                "time": row.Index.strftime("%Y-%m-%d"),
                "value": row.TR2 if not np.isnan(row.TR2) else None,
            }
        )
        json_data["tr3"].append(
            {
                "time": row.Index.strftime("%Y-%m-%d"),
                "value": row.TR3 if not np.isnan(row.TR3) else None,
            }
        )
        json_data["open"].append(
            {
                "time": row.Index.strftime("%Y-%m-%d"),
                "value": row.Open if not np.isnan(row.Open) else None,
            }
        )
        json_data["high"].append(
            {
                "time": row.Index.strftime("%Y-%m-%d"),
                "value": row.High if not np.isnan(row.High) else None,
            }
        )
        json_data["low"].append(
            {
                "time": row.Index.strftime("%Y-%m-%d"),
                "value": row.Low if not np.isnan(row.Low) else None,
            }
        )
        json_data["close"].append(
            {
                "time": row.Index.strftime("%Y-%m-%d"),
                "value": row.Close if not np.isnan(row.Close) else None,
            }
        )

    return json_data


# Function to perform the calculation and generate the JSON data
def perform_hourly_prediction(stock_ticker, start_date, end_date):

    data = yf.download(stock_ticker, start=start_date, interval="60m")
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

    # Convert end_date to a datetime object
    end_date_obj = datetime.combine(end_date, time(0, 0))
    
    # Create the datetime object for 9:15 AM UTC on the end_date
    date_time = datetime(year=end_date_obj.year, month=end_date_obj.month, day=end_date_obj.day, hour=9, minute=15, tzinfo=timezone.utc)
    
    # Convert to Unix timestamp
    next_hour_unix = int(date_time.timestamp())

    if last_data_date == end_date_obj.date():
    # Adjust next hour Unix time within trading hours if the last data date matches the end date
        last_hour = data.index[-1].hour
        next_hour = last_hour + 1

        if next_hour >= 9 and next_hour < 15:  # within trading hours
            next_hour_unix = int(
                datetime.combine(last_data_date, time(hour=next_hour, tzinfo=timezone.utc)).timestamp()
            )
        else:  # wrap-around to the next trading day's first hour (9:15 AM)
            next_hour_unix = int(
                datetime.combine(last_data_date + timedelta(days=1), time(9, 15, tzinfo=timezone.utc)).timestamp()
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
    return jsonDataHourFrame

# Fetch and display the candlestick chart
if stock_ticker and start_date and end_date:
    json_data = perform_calculation(stock_ticker, start_date, end_date)
    json_dataHour = perform_hourly_prediction(stock_ticker, start_date, end_date)
    
    # Convert JSON data to string
    json_str = json.dumps(json_data, indent=4)
    json_strHour = json.dumps(json_data, indent=4)

    # Format data for each period
    last_6_days_data = format_ohlc_values(json_data, "Last6Days")
    last_30_days_data = format_ohlc_values(json_data, "Last30Days")
    last_12_weeks_data = format_ohlc_values(json_data, "Last12Weeks")
    last_6_months_data = format_ohlc_values(json_data, "Last6Months")
    
    # Clean the data
    json_data["ts1"] = remove_null_values(json_data["ts1"])
    json_data["ts2"] = remove_null_values(json_data["ts2"])
    json_data["ts3"] = remove_null_values(json_data["ts3"])
    json_data["tr1"] = remove_null_values(json_data["tr1"])
    json_data["tr2"] = remove_null_values(json_data["tr2"])
    json_data["tr3"] = remove_null_values(json_data["tr3"])

    if json_data and json_data["candlestick"]:
        # Prepare the chart options
        chart_options = {
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
            # "watermark": {
            #     "visible": True,
            #     "fontSize": 48,
            #     "horzAlign": 'center',
            #     "vertAlign": 'center',
            #     "color": 'rgba(171, 71, 188, 0.3)',
            #     "text": 'Intraday',
            # }
        }

        series_candlestick_chart = [
            {
                "type": "Candlestick",
                "data": json_data["candlestick"],
                "options": {
                    "upColor": "#26a69a",
                    "downColor": "#ef5350",
                    "borderVisible": False,
                    "wickUpColor": "#26a69a",
                    "wickDownColor": "#ef5350",
                },
            }
        ]

        # Additional series (TS1, TS2, TS3, TR1, TR2, TR3)
        ts_tr_series = [
            {
                "type": "Line",
                "data": json_data["ts1"],
                "options": {"color": "blue", "title": "TS1"},
            },
            {
                "type": "Line",
                "data": json_data["ts2"],
                "options": {"color": "green", "title": "TS2"},
            },
            {
                "type": "Line",
                "data": json_data["ts3"],
                "options": {"color": "purple", "title": "TS3"},
            },
            {
                "type": "Line",
                "data": json_data["tr1"],
                "options": {"color": "red", "title": "TR1"},
            },
            {
                "type": "Line",
                "data": json_data["tr2"],
                "options": {"color": "orange", "title": "TR2"},
            },
            {
                "type": "Line",
                "data": json_data["tr3"],
                "options": {"color": "yellow", "title": "TR3"},
            },
        ]

        st.subheader(f"{stock_ticker} from {start_date} to {end_date}")

        # Render the charts
        renderLightweightCharts(
            [
                {
                    "series": series_candlestick_chart + ts_tr_series,
                    "chart": chart_options,
                }
            ],
            "candlestick",
        )

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
        col9, col10, col11, col12 = st.columns(4)
        with col9:
            show_open3 = st.checkbox("Open 3")
        with col10:
            show_high3 = st.checkbox("High 3")
        with col11:
            show_low3 = st.checkbox("Low 3")
        with col12:
            show_close3 = st.checkbox("Close 3")

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
            series_chartHour.append({
                "type": "Line",
                "data": json_dataHour["predicted_open1"],
                "options": {"color": "blue", "title": "Predicted Open 1"},
            })

        if show_high1:
            series_chartHour.append({
                "type": "Line",
                "data": json_dataHour["predicted_high1"],
                "options": {"color": "purple", "title": "Predicted High 1"},
            })

        if show_low1:
            series_chartHour.append({
                "type": "Line",
                "data": json_dataHour["predicted_low1"],
                "options": {"color": "cyan", "title": "Predicted Low 1"},
            })

        if show_close1:
            series_chartHour.append({
                "type": "Line",
                "data": json_dataHour["predicted_close1"],
                "options": {"color": "teal", "title": "Predicted Close 1"},
            })

        if show_open2:
            series_chartHour.append({
                "type": "Line",
                "data": json_dataHour["predicted_open2"],
                "options": {"color": "green", "title": "Predicted Open 2"},
            })

        if show_high2:
            series_chartHour.append({
                "type": "Line",
                "data": json_dataHour["predicted_high2"],
                "options": {"color": "orange", "title": "Predicted High 2"},
            })

        if show_low2:
            series_chartHour.append({
                "type": "Line",
                "data": json_dataHour["predicted_low2"],
                "options": {"color": "yellow", "title": "Predicted Low 2"},
            })

        if show_close2:
            series_chartHour.append({
                "type": "Line",
                "data": json_dataHour["predicted_close2"],
                "options": {"color": "pink", "title": "Predicted Close 2"},
            })

        if show_open3:
            series_chartHour.append({
                "type": "Line",
                "data": json_dataHour["predicted_open3"],
                "options": {"color": "red", "title": "Predicted Open 3"},
            })

        if show_high3:
            series_chartHour.append({
                "type": "Line",
                "data": json_dataHour["predicted_high3"],
                "options": {"color": "magenta", "title": "Predicted High 3"},
            })

        if show_low3:
            series_chartHour.append({
                "type": "Line",
                "data": json_dataHour["predicted_low3"],
                "options": {"color": "brown", "title": "Predicted Low 3"},
            })

        if show_close3:
            series_chartHour.append({
                "type": "Line",
                "data": json_dataHour["predicted_close3"],
                "options": {"color": "gray", "title": "Predicted Close 3"},
            })

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

        # Prepare the combined data for the table
        combined_data = {
            "Metric": [
                "Last 6 Days Avg HL Diff", "Last 30 Days Avg HL Diff", "Last 12 Weeks Avg HL Diff", "Last 6 Months Avg HL Diff",
                "Previous Day", "Previous Day Open", "Previous Day High",
                "Previous Day Low", "Previous Day Close",
                "TS1", "TS2", "TS3", "TR1", "TR2", "TR3",
                "Market Capital", "EPS", "PE Ratio", "Outstanding Shares",
                "Previous Close", "Float Shares", "Current Price", "Revenue Per Share"
            ],
            "Value": [
                json_data["Last6Days"]["Avg"], json_data["Last30Days"]["Avg"], json_data["Last12Weeks"]["Avg"], json_data["Last6Months"]["Avg"],
                datetime.fromtimestamp(json_data["candlestick"][-2]["time"], timezone.utc).strftime('%Y-%m-%d'), 
                f"{json_data['candlestick'][-2]['open']:.2f}", 
                f"{json_data['candlestick'][-2]['high']:.2f}", 
                f"{json_data['candlestick'][-2]['low']:.2f}", 
                f"{json_data['candlestick'][-2]['close']:.2f}",
                f"{json_data['ts1'][-1]['value']:.2f}", f"{json_data['ts2'][-1]['value']:.2f}", f"{json_data['ts3'][-1]['value']:.2f}", f"{json_data['tr1'][-1]['value']:.2f}", f"{json_data['tr2'][-1]['value']:.2f}", f"{json_data['tr3'][-1]['value']:.2f}",
                json_data["Market_Capital"], json_data["EPS"], json_data["PE_Ratio"], json_data["Outstanding_Shares"],
                json_data["Previous_Close"], json_data["Float_Shares"], json_data["Current_Price"], json_data["Revenue_Per_Share"]
            ]
        }

        # Convert to DataFrame and display as a table
        # df_combined = pd.DataFrame(combined_data)
        # st.subheader("Combined Financial Data")
        # st.table(df_combined)

        # Define chart options for each line chart
        chart_options_6_days = {
            "layout": {
                "width": 600,
                "height": 100,
                "textColor": "black",
                "background": {"type": "solid", "color": "white"},
            }
        }

        chart_options_30_days = {
            "layout": {
                "width": 600,
                "height": 100,
                "textColor": "black",
                "background": {"type": "solid", "color": "white"},
            }
        }

        chart_options_12_weeks = {
            "layout": {
                "width": 600,
                "height": 100,
                "textColor": "black",
                "background": {"type": "solid", "color": "white"},
            }
        }

        chart_options_6_months = {
            "layout": {
                "width": 600,
                "height": 100,
                "textColor": "black",
                "background": {"type": "solid", "color": "white"},
            }
        }

        # Define series data for each line chart
        series_6_days = [
            {
                "type": "Line",
                "data": last_6_days_data,
                "options": {"color": "blue", "title": "Last 6 Days"},
            }
        ]

        series_30_days = [
            {
                "type": "Line",
                "data": last_30_days_data,
                "options": {"color": "green", "title": "Last 30 Days"},
            }
        ]

        series_12_weeks = [
            {
                "type": "Line",
                "data": last_12_weeks_data,
                "options": {"color": "purple", "title": "Last 12 Weeks"},
            }
        ]

        series_6_months = [
            {
                "type": "Line",
                "data": last_6_months_data,
                "options": {"color": "orange", "title": "Last 6 Months"},
            }
        ]
        renderLightweightCharts([
            {
                "chart": chart_options_6_days,
                "series": series_6_days
            },
            {
                "chart": chart_options_30_days,
                "series": series_30_days
            },
             {
                "chart": chart_options_12_weeks,
                "series": series_12_weeks
            },
             {
                "chart": chart_options_6_months,
                "series": series_6_months
            }
        ], 'line')
        
        # Add the following code here to display the additional data:
        if json_data:
            # Display Last 6 Days OHLC Values and Average HL Difference
            st.subheader("Last 6 Days OHLC Values and Average HL Difference")
            st.write(
                "Average HL Difference for Last 6 Days:",
                f"{json_data['Last6Days']['Avg']:.2f}",
            )
            df_last_6_days = pd.DataFrame(
                json_data["Last6Days"]["OHLCValues"]
            ).transpose()
            st.table(format_dataframe(df_last_6_days))

            # Display Last 30 Days OHLC Values and Average HL Difference
            st.subheader("Last 30 Days OHLC Values and Average HL Difference")
            st.write(
                "Average HL Difference for Last 30 Days:",
                f"{json_data['Last30Days']['Avg']:.2f}",
            )
            df_last_30_days = pd.DataFrame(
                json_data["Last30Days"]["OHLCValues"]
            ).transpose()
            st.table(format_dataframe(df_last_30_days))

            # Display Last 12 Weeks OHLC Values and Average HL Difference
            st.subheader("Last 12 Weeks OHLC Values and Average HL Difference")
            st.write(
                "Average HL Difference for Last 12 Weeks:",
                f"{json_data['Last12Weeks']['Avg']:.2f}",
            )
            df_last_12_weeks = pd.DataFrame(
                json_data["Last12Weeks"]["OHLCValues"]
            ).transpose()
            st.table(format_dataframe(df_last_12_weeks))

            # Display Last 6 Months OHLC Values and Average HL Difference
            st.subheader("Last 6 Months OHLC Values and Average HL Difference")
            st.write(
                "Average HL Difference for Last 6 Months:",
                f"{json_data['Last6Months']['Avg']:.2f}",
            )
            df_last_6_months = pd.DataFrame(
                json_data["Last6Months"]["OHLCValues"]
            ).transpose()
            st.table(format_dataframe(df_last_6_months))
    else:
        st.error("No data available for the selected date range.")

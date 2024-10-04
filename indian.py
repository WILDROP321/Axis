import yfinance as yf
import datetime
import pytz
import pandas as pd
import plotly.graph_objs as go
import numpy as np
import csv
import os
import shutil





def readStocks():
    with open('IND.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        
        # Loop through the rows and store values from column 3 (index 2)
        for row in reader:
            symbol_list.append(row[0])
# Define the stock symbol and number of days


def clearData():
    # Check if the folder exists
    folder_path = "DATA"
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return

    # Loop through the files and directories in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        try:
            # Check if it's a file and remove it
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                print(f"Deleted file: {file_path}")
            # If it's a directory, remove it and its contents
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f"Deleted directory: {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


# Function to fetch data
def fetch_data(symbol):
    timezone = pytz.timezone('Asia/Kolkata')

    # Get the current time and the start date (60 days ago)
    end_time = datetime.datetime.now(timezone)
    today = end_time.date()
    start_time = today - datetime.timedelta(days=my_days)

    # Convert start and end times to naive (no timezone)
    start_time = timezone.localize(datetime.datetime.combine(start_time, datetime.time(9, 30)))
    end_time = timezone.localize(datetime.datetime.combine(today, datetime.time(16, 0)))

    # Fetch data with a 1-day interval
    data = yf.download(symbol, start=start_time, end=end_time, interval= myInterval, progress=False)

    if data.empty:
        raise ValueError("No data returned from Yahoo Finance.")

    return data

# Function to calculate ohlc4
def calculate_ohlc4(data):
    ohlc4 = (data['Open'] + data['High'] + data['Low'] + data['Close']) / 4
    return ohlc4

# Calculate Heikin-Ashi parameters
def hieken_params(data):
    pd.options.mode.chained_assignment = None  # default='warn'
    # Calculate OHLC4
    data['ohlc4'] = calculate_ohlc4(data)

    # Initialize haOpen and haC columns with NaN values
    data['haOpen'] = data['ohlc4'].copy() # change 0.0
    data['haC'] = data['ohlc4'].copy()

    # Initialize the first value of haOpen to the first OHLC4 value
    data['haOpen'].iloc[0] = data['ohlc4'].iloc[0]

    # Loop through the data to calculate haOpen and haC for each day
    for i in range(1, len(data)):
        # Heikin-Ashi Open (haOpen) formula: (src + nz(haOpen[1])) / 2
        data['haOpen'].iloc[i] = (data['ohlc4'].iloc[i] + data['haOpen'].iloc[i - 1]) / 2

        # Heikin-Ashi Close (haC) formula
        data['haC'].iloc[i] = (
            data['ohlc4'].iloc[i] + data['haOpen'].iloc[i] +
            max(data['High'].iloc[i], data['haOpen'].iloc[i]) +
            min(data['Low'].iloc[i], data['haOpen'].iloc[i])
        ) / 4

    return data[['Open', 'High', 'Low', 'Close', 'ohlc4', 'haOpen', 'haC']]

# Function to calculate the Heikin-Ashi indicators
def calculate_heikin_ashi():
    data = fetch_data(symbol)
    data = hieken_params(data)

    ema_length = 55

    # Calculate first set of EMAs (for Heikin-Ashi Close - haC)
    data['EMA1'] = data['haC'].ewm(span=ema_length, adjust=False).mean()
    data['EMA2'] = data['EMA1'].ewm(span=ema_length, adjust=False).mean()
    data['EMA3'] = data['EMA2'].ewm(span=ema_length, adjust=False).mean()

    # Calculate TMA1
    data['TMA1'] = 3 * data['EMA1'] - 3 * data['EMA2'] + data['EMA3']

    # Calculate next set of EMAs and TMAs
    data['EMA4'] = data['TMA1'].ewm(span=ema_length, adjust=False).mean()
    data['EMA5'] = data['EMA4'].ewm(span=ema_length, adjust=False).mean()
    data['EMA6'] = data['EMA5'].ewm(span=ema_length, adjust=False).mean()

    # Calculate TMA2
    data['TMA2'] = 3 * data['EMA4'] - 3 * data['EMA5'] + data['EMA6']

    # Calculate IPEK and YASIN (Red Line)
    data['IPEK'] = data['TMA1'] - data['TMA2']
    data['YASIN'] = data['TMA1'] + data['IPEK']

    # Calculate second set of EMAs (for hlc3)
    data['hlc3'] = (data['High'] + data['Low'] + data['Close']) / 3
    data['EMA7'] = data['hlc3'].ewm(span=ema_length, adjust=False).mean()
    data['EMA8'] = data['EMA7'].ewm(span=ema_length, adjust=False).mean()
    data['EMA9'] = data['EMA8'].ewm(span=ema_length, adjust=False).mean()

    # Calculate TMA3
    data['TMA3'] = 3 * data['EMA7'] - 3 * data['EMA8'] + data['EMA9']

    # Calculate next set of EMAs and TMAs
    data['EMA10'] = data['TMA3'].ewm(span=ema_length, adjust=False).mean()
    data['EMA11'] = data['EMA10'].ewm(span=ema_length, adjust=False).mean()
    data['EMA12'] = data['EMA11'].ewm(span=ema_length, adjust=False).mean()

    # Calculate TMA4
    data['TMA4'] = 3 * data['EMA10'] - 3 * data['EMA11'] + data['EMA12']

    # Calculate IPEK1 and YASIN1 (Blue Line)
    data['IPEK1'] = data['TMA3'] - data['TMA4']
    data['YASIN1'] = data['TMA3'] + data['IPEK1']

    return data[['Open', 'High', 'Low', 'Close', 'ohlc4', 'haOpen', 'haC', 'YASIN', 'YASIN1']]

# Function to generate buy/sell signals based on YASIN crossovers
def generate_signals(data):
    # Buy signal: YASIN crosses above YASIN1
    data['Buy'] = np.where((data['YASIN1'] > data['YASIN']) & (data['YASIN1'].shift(1) <= data['YASIN'].shift(1)), 1, 0)
    
    # Sell signal: YASIN crosses below YASIN1
    data['Sell'] = np.where((data['YASIN1'] < data['YASIN']) & (data['YASIN1'].shift(1) >= data['YASIN'].shift(1)), 1, 0)


    return data

# Function to plot the Heikin-Ashi candles and buy/sell signals
def plot_heikin_ashi(data):
    # Heikin-Ashi candlesticks
    heikin_ashi = go.Candlestick(x=data.index,
                                 open=data['haOpen'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['haC'],
                                 name='Heikin-Ashi')

    # Plot YASIN (red) and YASIN1 (blue)
    yasin = go.Scatter(x=data.index, y=data['YASIN'], line=dict(color='red', width=3), name='YASIN (Red Line)')
    yasin1 = go.Scatter(x=data.index, y=data['YASIN1'], line=dict(color='blue', width=3), name='YASIN1 (Blue Line)')

    # Buy/Sell signals
    buys = go.Scatter(x=data[data['Buy'] == 1].index, y=data[data['Buy'] == 1]['haC'], mode='markers', marker=dict(symbol='triangle-up', color='green', size=30), name='Buy Signal')
    sells = go.Scatter(x=data[data['Sell'] == 1].index, y=data[data['Sell'] == 1]['haC'], mode='markers', marker=dict(symbol='triangle-down', color='red', size=30), name='Sell Signal')

    # Layout
    layout = go.Layout(title=f'Heikin-Ashi Candlestick with Buy/Sell Signals for {symbol}',
                       xaxis_title='Date',
                       yaxis_title='Price',
                       xaxis_rangeslider_visible=False)

    # Create figure
    fig = go.Figure(data=[heikin_ashi, yasin, yasin1, buys, sells], layout=layout)
    fig.show()

# Main function to run everything
def main(symbol):
    data = calculate_heikin_ashi()
    generate_signals(data)
    info = (data[['haC', 'YASIN', 'YASIN1', 'Buy', 'Sell', 'Close']])
    info.to_csv(f'DATA/{symbol}.csv', index=True)
    #plot_heikin_ashi(data)

def prediction():
    timezone = pytz.timezone('Asia/Kolkata')
    today_date = datetime.datetime.now(timezone).date()

    with open(f'PREDICTIONS/{today_date} ~ India predictions.csv', 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        # Write the header
        writer.writerow(["Symbol", "Action", "Price"])

        for i in range(len(symbol_list)):
            symbol = symbol_list[i]
            with open(f"DATA/{symbol}.csv", 'r') as file:
                reader = csv.reader(file)
                last_row = None
                for row in reader:
                    last_row = row
                
                # Check for 'BUY' or 'SELL' and write to the output CSV file
                if last_row[4] == '1':
                    writer.writerow([symbol, "BUY", last_row[6]])
                
                if last_row[5] == '1':
                    writer.writerow([symbol, "SELL", last_row[6]])





if __name__ == "__main__":
    clearData()

    symbol_list = []
    readStocks()

    my_days = 60
    myInterval = '1d'

    print(len(symbol_list))



    for i in range(len(symbol_list)):
        symbol = symbol_list[i]
        try:
            main(symbol)
        except:
            print(symbol)


    prediction()



# API Key: 9M4TJBS45SVG391Z
import json
import requests
import os 
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import numpy as np

model = Prophet(daily_seasonality=True)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_highest(symbol):
    with open(f'{CURRENT_DIR}\{symbol}.json') as f:
        stock_data = json.load(f)
        highest_opening, highest, highest_low, highest_close = 0, 0, 0, 0
    
        for _, values in stock_data["Monthly Time Series"].items(): 
            current_opening = float(values['1. open'])
            current_high = float(values['2. high'])
            current_low = float(values['3. low'])
            current_close = float(values['4. close'])
            if highest_opening < current_opening: highest_opening = current_opening
            if highest < current_high: highest = current_high
            if highest_low < current_low: highest_low = current_low
            if highest_close < current_close: highest_close = current_close
        
        return highest_opening, highest, highest_low, highest_close 

def get_full_data(symbol):
    request = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey=9M4TJBS45SVG391Z'
    r = requests.get(request)
    if r.status_code == 200:
        stock_data = r.json()

        with open(f'{CURRENT_DIR}\{symbol}.json', 'w') as f:
            json.dump(stock_data, f, ensure_ascii=False, indent=4)
            return 200
    else:
        return r.status_code

def get_values(symbol):
    if os.path.isfile(f'{CURRENT_DIR}\{symbol}.json'):
        with open(f'{CURRENT_DIR}\{symbol}.json') as f:
            data = json.load(f)
            dates = []
            opening_values = []
            for date, values in data['Time Series (Daily)'].items():
                opening_values.insert(0, float(values['1. open']))
                dates.insert(0, date)
            return dates, opening_values
    else:
        print('File does not exist\nfetching data...')
        r = get_full_data(symbol)
        if r != 200:
            print('Failed to create file')
            print(r)
        else:
            print('Successfully created file')
            return get_values(symbol)

def create_stock_data_frame(dates, values):
    d_range = pd.DatetimeIndex(data=dates)
    date_strings = [date.strftime('%Y-%m-%d') for date in d_range]
    df = pd.DataFrame({
        'ds': d_range,
        'y': values
    })
    return df, date_strings

def create_plot(symbol, prediction_amount):
    
    dates, values = get_values(symbol)
    data_frame, dates = create_stock_data_frame(dates, values)
    model.fit(data_frame)    
    future_dates = model.make_future_dataframe(periods=prediction_amount, freq='D')
    forecast = model.predict(future_dates)
    forecast_values = (forecast['yhat'])[len(values):]
    dates = (forecast['ds'])[len(dates):]
    dates = np.array(dates.dt.to_pydatetime())
    dates = [date.strftime('%Y-%m-%d') for date in dates]

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)


    plt.figure(figsize=(10, 6))

    plt.plot(dates, forecast_values, marker='o', markersize=2, color='b', linestyle='-')
    plt.title(f'{symbol} forecast for next {prediction_amount} days')
    plt.xlabel('Dates')
    plt.ylabel('Value')

    plt.grid(True) 
    plt.xticks(rotation=45)  
    plt.tight_layout()
    return plt

def save_plot(symbol, plot):
    path = f'{CURRENT_DIR}\{symbol}_forecast.png'
    plot.savefig(path)
    print('saved plot to', path)

plot = create_plot('ADBE', 12)
save_plot('ADBE', plot)
plot.show()


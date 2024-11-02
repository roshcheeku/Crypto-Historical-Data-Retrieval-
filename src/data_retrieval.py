import os
import requests
import pandas as pd
from datetime import datetime
import openpyxl

# Step 1: Identify a Reliable API for Crypto Data Retrieval 1. API
def fetch_crypto_data(crypto_pair,start_date):
    api_key = os.getenv('CRYPTO_API_KEY')
    base_url = "https://min-api.cryptocompare.com/data/v2/histoday"
    if not api_key:
        raise ValueError("API KEY NOT SET IN ENVIRONMENT VARIABLES")
    
    dt=datetime.strptime(start_date,'%Y-%m-%d')
    start_timestamp=int(dt.timestamp())

    params={
         "fsym": crypto_pair.split('/')[0].upper(),
        "tsym": crypto_pair.split('/')[1].upper(),
        "limit": 2000,
        "toTs": start_timestamp,
        "api_key": api_key
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data=response.json()


    if 'Data' in data and 'Data' in data['Data']:
        prices = data['Data']['Data']
        df = pd.DataFrame(prices)
        df['Date'] = pd.to_datetime(df['time'], unit='s')
        df['Open'] = df['open']
        df['High'] = df['high']
        df['Low'] = df['low']
        df['Close'] = df['close']
        return df[['Date', 'Open', 'High', 'Low', 'Close']]
    else:
        raise ValueError("No data available.")
#Step 2: Retrieve Historical Data  and Calculate metrics
def calculate_metrics(df, variable1=7, variable2=5):
    df['High_Last_{}_Days'.format(variable1)] = df['High'].rolling(window=variable1).max()
    df['Days_Since_High_Last_{}_Days'.format(variable1)] = (df['Date'] - df['Date'].shift(variable1)).dt.days
    df['%_Diff_From_High_Last_{}_Days'.format(variable1)] = ((df['Close'] - df['High_Last_{}_Days'.format(variable1)]) / df['High_Last_{}_Days'.format(variable1)]) * 100

    df['Low_Last_{}_Days'.format(variable1)] = df['Low'].rolling(window=variable1).min()
    df['Days_Since_Low_Last_{}_Days'.format(variable1)] = (df['Date'] - df['Date'].shift(variable1)).dt.days
    df['%_Diff_From_Low_Last_{}_Days'.format(variable1)] = ((df['Close'] - df['Low_Last_{}_Days'.format(variable1)]) / df['Low_Last_{}_Days'.format(variable1)]) * 100
    for i in range(1, variable2 + 1):
        df['High_Next_{}_Days'.format(i)] = df['High'].shift(-i)
        df['%_Diff_From_High_Next_{}_Days'.format(i)] = ((df['High_Next_{}_Days'.format(i)] - df['Close']) / df['Close']) * 100
        df['Low_Next_{}_Days'.format(i)] = df['Low'].shift(-i)
        df['%_Diff_From_Low_Next_{}_Days'.format(i)] = ((df['Low_Next_{}_Days'.format(i)] - df['Close']) / df['Close']) * 100
    return df
def export_to_excel(dataframes, filename="crypto_data.xlsx"):
       with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Data successfully written to {filename}")

if __name__ == "__main__":
    crypto_pairs = ['BTC/USD', 'ETH/USD']
    start_date = '2023-01-01'
    dataframes = {}

    for crypto_pair in crypto_pairs:
        print(f"Fetching data for {crypto_pair}...")
        df = fetch_crypto_data(crypto_pair, start_date)
        print("Successfully fetched data:")
        print(df.head())

        print(f"Calculating metrics for {crypto_pair}...")
        df_with_metrics = calculate_metrics(df, variable1=7, variable2=5)
        dataframes[crypto_pair.replace('/', '_')] = df_with_metrics

    export_to_excel(dataframes, filename="crypto_data.xlsx")


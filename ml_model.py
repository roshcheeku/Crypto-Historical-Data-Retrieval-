import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import pickle
#Step 3: Calculate Highest, Lowest, and Percentage Difference Metrics
variable2=5
def calculate_future_metrics(df,variable2):
    df['High_Next_{}_days'.format(variable2)]=df['High'].shift(-variable2).rolling(variable2).max()
    df['Low_Next_{}_days'.format(variable2)]=df['Low'].shift(-variable2).rolling(variable2).min()
    df['%_Diff_From_High_Next_{}_Days'.format(variable2)] = (
        (df['High_Next_{}_Days'.format(variable2)] - df['Close']) / df['Close'] * 100
    )
    
    df['%_Diff_From_Low_Next_{}_Days'.format(variable2)] = (
        (df['Low_Next_{}_Days'.format(variable2)] - df['Close']) / df['Close'] * 100
    )

    return df
def train_model():
    data=pd.read_excel('crypto_data.xlsx', sheet_name=None)

    for sheet_name in data.keys():
        df=data[sheet_name]
        df=calculate_future_metrics(df,variable2)
        data[sheet_name]=df

    with pd.ExcelWriter('crypto_data_with_future_metrics.xlsx') as writer:
         for sheet_name, df in data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print("Future metrics successfully calculated and saved to crypto_data_with_future_metrics.xlsx")
    btc_data = data.get('BTC_USD', None)
    if btc_data is None:
         raise ValueError("Error: 'BTC_USD' sheet not found. Please check the sheet name and try again.")

    btc_data=btc_data.dropna()
    X = btc_data[['Open', 'High', 'Low', 'Close']]
    y_high = btc_data['%_Diff_From_High_Next_{}_Days'.format(variable2)]
    y_low = btc_data['%_Diff_From_Low_Next_{}_Days'.format(variable2)]
 # Split the data into training and testing sets
    X_train, X_test, y_high_train, y_high_test = train_test_split(X, y_high, test_size=0.2, random_state=42)
    X_train, X_test, y_low_train, y_low_test = train_test_split(X, y_low, test_size=0.2, random_state=42)
    model_high = RandomForestRegressor(n_estimators=100, random_state=42)
    model_high.fit(X_train, y_high_train)

    model_low = RandomForestRegressor(n_estimators=100, random_state=42)
    model_low.fit(X_train, y_low_train)

    # Predict
    y_high_pred = model_high.predict(X_test)
    y_low_pred = model_low.predict(X_test)
    mse_high = mean_squared_error(y_high_test, y_high_pred)
    mse_low = mean_squared_error(y_low_test, y_low_pred)

    print(f"Mean Squared Error for High price prediction: {mse_high}")
    print(f"Mean Squared Error for Low price prediction: {mse_low}")

    with open('model_high.pkl', 'wb') as file_high:
         pickle.dump(model_high, file_high)
    with open('model_low.pkl', 'wb') as file_low:
        pickle.dump(model_low, file_low)

    print("Models saved as model_high.pkl and model_low.pkl.")

    return mse_high, mse_low
def predict_outcomes(open_value, high_value, low_value, close_value):
    # Load the trained models
    with open('model_high.pkl', 'rb') as file_high:
        model_high = pickle.load(file_high)

    with open('model_low.pkl', 'rb') as file_low:
        model_low = pickle.load(file_low)

    input_data =pd.DataFrame([[open_value, high_value, low_value, close_value]],columns=['Open','High','Low','Close'])

    high_diff_pred = model_high.predict(input_data)
    low_diff_pred = model_low.predict(input_data)

    return high_diff_pred[0], low_diff_pred[0]

if __name__ == "__main__":
    train_model()
    try:
        open_value = float(input("Enter the Open value: "))
        high_value = float(input("Enter the High value: "))
        low_value = float(input("Enter the Low value: "))
        close_value = float(input("Enter the Close value: "))
        high_prediction, low_prediction = predict_outcomes(open_value, high_value, low_value, close_value)
        print(f"Predicted % Difference from High for {variable2} Days: {high_prediction:.2f}%")
        print(f"Predicted % Difference from Low for {variable2} Days: {low_prediction:.2f}%")

    except ValueError:
        print("Invalid input. Please enter numerical values.")


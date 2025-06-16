import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
from keras.callbacks import EarlyStopping

# Read the Excel file
file_path = './input data/2016-2030_PEV_data.xlsx'
df = pd.read_excel(file_path)

# Data preprocessing
features = ['total_GDP', 'Urbanization_rate', 'SumBaidu', 'people', 'Urban_population', 'EV_Subsidy funds']
target = 'PEV_number'

# Prepare an empty DataFrame to store results
result_df = pd.DataFrame()

for city in df['City'].unique():
    city_data = df[df['City'] == city]

    # Skip if there is insufficient data for the city
    if len(city_data) < 2:
        continue

    # Split data into training and testing sets
    train_data = city_data[city_data['Year'] <= 2023]
    test_data = city_data[city_data['Year'] > 2023]

    # Feature scaling
    scaler = MinMaxScaler()
    train_scaled = scaler.fit_transform(train_data[features])
    test_scaled = scaler.transform(test_data[features])

    # Set the time step length, here set to 3, meaning each sample contains features and target variables for three time steps
    look_back = 3

    # Create time series data
    def create_dataset(dataset, look_back=1):
        X, Y = [], []
        for i in range(len(dataset) - look_back):
            a = dataset[i:(i + look_back), :]
            X.append(a)
            Y.append(dataset[i + look_back, 0])  # Assume the target variable is in the first column
        return np.array(X), np.array(Y)

    # Use only features for scaling, excluding the target variable
    trainX, trainY = create_dataset(np.hstack((train_scaled, train_data[target].values.reshape(-1, 1))), look_back)

    # Build the LSTM model
    model = Sequential()
    model.add(LSTM(50, input_shape=(look_back, len(features) + 1), return_sequences=True))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')

    # Set early stopping
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    # Train the model
    model.fit(trainX, trainY, epochs=100, batch_size=1, verbose=0, validation_split=0.2, callbacks=[early_stopping])

    # Prediction
    # Create input for test data
    test_input = np.hstack((test_scaled, np.zeros((len(test_scaled), 1))))  # Initialize prediction values to 0
    predictions = []

    for i in range(len(test_scaled)):
        # Use the current input for prediction
        if i < look_back:
            input_data = test_input[:look_back, :].reshape(1, look_back, len(features) + 1)
        else:
            input_data = test_input[i - look_back + 1:i + 1, :].reshape(1, look_back, len(features) + 1)
        prediction = model.predict(input_data)
        predictions.append(prediction[0, 0])

        # Update the test_input with the prediction for the next step
        if i < len(test_scaled):
            test_input[i, -1] = prediction[0, 0]

    if len(predictions) < len(test_data):
        predictions = np.pad(predictions, (0, len(test_data) - len(predictions)), 'constant', constant_values=np.nan)

    # Reverse scale the predictions
    predictions = np.array(predictions).reshape(-1, 1)
    predictions = np.hstack((predictions, np.zeros((len(predictions), len(features)))))

    # Ensure the shape of predictions matches the shape of scaler's min_ attribute
    if predictions.shape[1] != scaler.min_.shape[0]:
        predictions = predictions[:, :scaler.min_.shape[0]]

    predictions = scaler.inverse_transform(predictions)[:, 0]

    # Ensure the length of predictions matches the length of test data
    if len(predictions) < len(test_data):
        predictions = np.pad(predictions, (0, len(test_data) - len(predictions)), 'constant', constant_values=np.nan)

    # Combine actual values, predictions, and original features
    result = test_data.copy()
    result['Predicted_PEV_number'] = predictions
    result = result[['CN_City', 'City', 'Year', 'CN_Procince', 'Procince', target] + ['Predicted_PEV_number']]

    # Add to the final result DataFrame
    result_df = pd.concat([result_df, result], ignore_index=True)

    # Save results to Excel
    result_df.to_excel('./output data_prediction/PEV_Predictions_results.xlsx', index=False)

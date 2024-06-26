import math
import matplotlib.pyplot as plt
import tensorflow as tf
from keras import Sequential
from tensorflow.keras.layers import Dense, LSTM
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Wczytanie danych
df = pd.read_csv('dataset_btc2017.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Wizualizacja danych
plt.figure(figsize=(16,8))
plt.title('Close Price History', fontsize=24)
plt.plot(df['timestamp'], df['close'])
plt.xlabel('Date', fontsize=14)
plt.ylabel('USD', fontsize=14)
plt.show()

# Przygotowanie danych
data = df[['timestamp', 'close']].copy()
dataset = data['close'].values
training_data_len = math.ceil(len(dataset) * 0.8)

scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(dataset.reshape(-1, 1))

# Definiowanie długości sekwencji
sequence_length = 60
forecast_length = 7

# Przygotowanie danych treningowych
X_train = []
Y_train = []

for i in range(sequence_length, len(scaled_data) - forecast_length + 1):
    X_train.append(scaled_data[i-sequence_length:i, 0])
    Y_train.append(scaled_data[i:i+forecast_length, 0])

X_train, Y_train = np.array(X_train), np.array(Y_train)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

# Podział na dane treningowe i testowe
train_size = int(len(X_train) * 0.8)
X_test = X_train[train_size:]
Y_test = Y_train[train_size:]
X_train = X_train[:train_size]
Y_train = Y_train[:train_size]

# Budowa modelu LSTM
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
model.add(LSTM(50))
model.add(Dense(50))
model.add(Dense(forecast_length))

model.compile(optimizer='adam', loss='mse')
model.fit(X_train, Y_train, epochs=10, batch_size=1)

# Predykcje
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)

# Przygotowanie danych do wizualizacji
train = data.iloc[:training_data_len]
valid = data.iloc[training_data_len:].copy()

# Wstawianie przewidywań do odpowiednich miejsc w dataframe
for i in range(len(predictions)):
    for j in range(forecast_length):
        if (training_data_len + i + j) < len(data):
            valid.loc[training_data_len + i + j, 'Prediction'] = predictions[i][j]

# Wizualizacja
plt.figure(figsize=(20,10))
plt.title('Model Predictions vs Real Data')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD', fontsize=18)
plt.plot(train['timestamp'], train['close'])
plt.plot(valid['timestamp'], valid['Prediction'], color='r')
plt.legend(['Train', 'Prediction'], loc='lower right')
plt.show()

# Wypisanie przewidywanych wartości dla kolejnych 7 dni
last_7_days_predictions = predictions[-1]  # Ostatnie przewidywania z testowego zbioru danych
print("Przewidywane wartości na kolejne 7 dni:")
for i, price in enumerate(last_7_days_predictions, 1):
    print(f"Dzień {i}: {price:.2f} USD")
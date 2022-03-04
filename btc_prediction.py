# -*- coding: utf-8 -*-
"""BTC_prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BgAbhAyPlP_4FhYSJjRD3GJlE-oG2j1u
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential

# IMPORTING DATA
data = pd.read_csv('dataset.csv') # data for 5 years

print(data)

# Adding values (days) to the dataset to predict the next day: 
# I was adding one day after another and tried to predict each next day.
# Further explanation could be found in the report.
# (I only changed the 5th value - close price and the date)

#data.loc[len(data.index)] = ['2021-12-25', 50854.92, 51176.60, 50236.71, 50429.86, 50429.86, 19030650914]
#data.loc[len(data.index)] = ['2021-12-26', 50428.69, 51196.38, 49623.11, 50809.52, 50809.52, 20964372926]
#data.loc[len(data.index)] = ['2021-12-27', 50428.69, 51196.38, 49623.11, 50640.42, 50809.52, 20964372926]
#data.loc[len(data.index)] = ['2021-12-28', 50428.69, 51196.38, 49623.11, 47588.86, 50809.52, 20964372926]
#data.loc[len(data.index)] = ['2021-12-29', 50428.69, 51196.38, 49623.11, 46444.71, 50809.52, 20964372926]
#print(data)

# PREPARING DATA
# scaling the values between 0 and 1:
scaler = MinMaxScaler(feature_range=(0,1)) 
scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1,1))

# how many days we want to base our prediciton on:
pred_days = 60 # we look at 60 days and then we predict the 61st day

x_train = []
y_train = []

# filling the training lists with data
for x in range(pred_days, len(scaled_data)):
  x_train.append(scaled_data[x-pred_days:x, 0]) # from 0 to len(data), x goes from 60 to len(data) -> (0, 59), (1, 60),...
  y_train.append(scaled_data[x, 0]) # only x -> predicting (60), predicting (61)

# transforming in numpy array
x_train = np.array(x_train)
y_train = np.array(y_train)

# adding third dimension
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

# TRAINING NEURAL NETWORK MODEL
# we have sequential data:
model = Sequential()

# using LSTM:
model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1],1))) # first LSTM layer
model.add(Dropout(0.2))   # using dropout layer to prevent overfitting 

model.add(LSTM(units=100, return_sequences=True))
model.add(Dropout(0.2))

model.add(LSTM(units=100, return_sequences=True))
model.add(Dropout(0.2))

model.add(LSTM(units=50))
model.add(Dropout(0.2))

# at the end we want it to return just 1 value indicating the predicted price:
model.add(Dense(units=1))

# compiling the model:
model.compile(optimizer='adam', loss='mean_squared_error')

# training the model:
model.fit(x_train, y_train, epochs=30, batch_size = 32)

# TESTING THE MODEL
# testing the model on the last 169 days:
data_test = data.loc[1650:]
#print(data_test)

actual_prices = data_test['Close'].values

data_total = pd.concat((data['Close'], data_test['Close']), axis=0)

model_inputs = data_total[len(data_total) - len(data_test) - pred_days : ].values
model_inputs = model_inputs.reshape(-1, 1)
model_inputs = scaler.fit_transform(model_inputs)

x_test = []

for x in range(pred_days, len(model_inputs)):
  x_test.append(model_inputs[x - pred_days:x, 0])

x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

prediction_prices = model.predict(x_test)
prediction_prices = scaler.inverse_transform(prediction_prices)

# VISUALIZING RESULTS
plt.plot(actual_prices, color='black', label='Actual prices')
plt.plot(prediction_prices, color='green', label='Predicted prices')
plt.title('BTC price prediction')
plt.xlabel('Time [days]')
plt.ylabel('Price [$]')
plt.legend(loc='upper left')
plt.show()

df_pred = pd.DataFrame(prediction_prices)
df_act = pd.DataFrame(actual_prices)

df = pd.concat([df_pred, df_act], axis=1)
df.columns = ['Predicted Price', 'Actual Price']
print(df)
# *row 168 is 24.12.2021

# PREDICTING THE NEXT DAY
real_data = [model_inputs[len(model_inputs) - pred_days : len(model_inputs) +1, 0]]
real_data = np.array(real_data)
real_data = np.reshape(real_data, (real_data.shape[0], real_data.shape[1], 1))

prediction = model.predict(real_data)
prediction = scaler.inverse_transform(prediction)
#print(prediction) # predicted price for the next day
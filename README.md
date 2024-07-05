-# Importing necessary libraries
import numpy as np
from sklearn.linear_model import LinearRegression

# Example dataset (you should replace this with your actual data)
# Features (input)
X_train = np.array([[1], [2], [3], [4], [5]])  # Example: 1-dimensional feature
# Target variable (output)
y_train = np.array([2, 4, 6, 8, 10])  # Example: corresponding targets

# Creating a linear regression model
model = LinearRegression()

# Training the model (learning)
model.fit(X_train, y_train)

# Now the model has "learned" from the training data
# You can now use it to make predictions on new data

# Example of making predictions
X_test = np.array([[6], [7]])  # New data points to predict
predictions = model.predict(X_test)

# Printing the predictions
for i, pred in enumerate(predictions):
    print(f"Prediction for X_test[{i}]: {pred}")


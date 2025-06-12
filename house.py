import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# Sample dataset (you can load CSV too)
data = {
    'area': [1000, 1500, 1800, 2400, 3000],
    'bedrooms': [2, 3, 3, 4, 4],
    'bathrooms': [1, 2, 2, 3, 3],
    'stories': [1, 2, 2, 2, 3],
    'parking': [1, 1, 2, 2, 3],
    'price': [50, 80, 95, 130, 160]  # price in lakhs (example)
}

df = pd.DataFrame(data)

# Features and target
X = df.drop('price', axis=1)
y = df['price']

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

# Model
model = DecisionTreeRegressor()
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))

# Predict new house price
new_house = [[2000, 3, 2, 2, 2]]  # [area, bedrooms, bathrooms, stories, parking]
predicted_price = model.predict(new_house)
print("Predicted house price (in lakhs):", predicted_price[0])

import os
import sys
import pandas as pd
from src.exception import CustomException
from src.utils import load_object

class CustomData:
    def __init__(self,
                 km_driven: float,
                 fuel: str,
                 seller_type: str,
                 transmission: str,
                 owner: str,
                 mileage: float,
                 engine: float,
                 max_power: float,
                 seats: int,
                 age: int
                 ):
        
        self.km_driven = km_driven
        self.fuel = fuel
        self.seller_type = seller_type
        self.transmission = transmission
        self.owner = owner
        self.mileage = mileage
        self.engine = engine
        self.max_power = max_power
        self.seats = seats
        self.age = age
        
    # Convert the input data from user to dataframe
    def get_data_as_data_frame(self):
        try:
            custom_data_input_dict = {
                "km_driven": [self.km_driven],
                "fuel": [self.fuel],
                "seller_type": [self.seller_type],
                "transmission": [self.transmission],
                "owner": [self.owner],
                "mileage": [self.mileage],
                "engine": [self.engine],
                "max_power": [self.max_power],
                "seats": [self.seats],
                "age": [self.age]
                }

            return pd.DataFrame(custom_data_input_dict)

        except Exception as e:
            raise CustomException(e, sys)

class PredictPipeline:
    def __init__(self):
        pass
    
    # Makes predictions on input data
    def predict(self, features):
        try:
            # Model and Preprocessor path
            model_path = os.path.join("artifacts", "model.pkl")
            preprocessor_path = os.path.join('artifacts', 'preprocessor.pkl')
            
            # Load Model and Preprocessor
            model = load_object(file_path = model_path)
            preprocessor = load_object(file_path = preprocessor_path)
            
            # Scale the inpurt features
            data_scaled = preprocessor.transform(features)
            
            # Make prediction on input features
            preds = model.predict(data_scaled)
            
            return preds
        
        except Exception as e:
            raise CustomException(e, sys)
from flask import Flask,request,render_template
import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from src.pipeline.predict_pipeline import CustomData, PredictPipeline

application=Flask(__name__)

app=application

## Route for a home page

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/predictdata', methods = ['GET','POST'])
def predict_datapoint():
    if request.method == 'GET':
        return render_template('home.html')
    else:
        data = CustomData(
            km_driven=request.form.get('km_driven'),
            fuel=request.form.get('fuel'),
            seller_type=request.form.get('seller_type'),
            transmission=request.form.get('transmission'),
            owner=request.form.get('owner'),
            mileage=request.form.get('mileage'),
            engine=request.form.get('engine'),
            max_power=request.form.get('max_power'),
            seats=request.form.get('seats'),
            age=request.form.get('age')
        )
        pred_df = data.get_data_as_data_frame()
        print(pred_df)
        print("Before Prediction")

        predict_pipeline=PredictPipeline()
        print("Mid Prediction")
        results=predict_pipeline.predict(pred_df)
        print("After Prediction")
        return render_template('home.html', results = results[0])
    

if __name__ == "__main__":      
    app.run(debug = True, host = "0.0.0.0", port = 80) 

import numpy as np
import xgboost
import pickle, joblib
import json
import pandas as pd
import math
from sklearn.base import BaseEstimator,TransformerMixin

# __locations = None
__model_features = None
__data_pipeline = None
__data_locations = None
__models = None
# __path = "/home/app/server/artifacts"
__path = "/home/hugo/Personal/Processing/git/home-prices-santiago/app/server/artifacts"


class CustomOrdinalEncoder(TransformerMixin, BaseEstimator):
    """
    Class defining a custom transformer that applies ordinal encoding.
    For any given feature in the input dataset, this transformation assigns 
    the value of the defined threshold to values which are higher the threshold.
    While feature values which lower or equal than the threshold are kept 
    unchanged.

    Parameters
    ----------
    TransformerMixin: class
        Implements method fit_transform().
    BaseEstimator: class
        Implements methods set_params() and get_params().

    Returns
    -------
        pandas.dataframe
        Dataframe containing transformed data.                
    """    
    def __init__(self, threshold=None):
        self.threshold = threshold
        
    def fit(self,X,y=None):
        return self
    
    def transform(self,X,y=None):
        """Apply ordinal encoding transformation to input dataset."""        
        if isinstance(X, pd.DataFrame):
            # convert dataframe to series
            X = X.squeeze('columns').copy()
        else:
            X = pd.Series(X).copy()
        X = X.apply(
            lambda x: int(x) if x < self.threshold else int(self.threshold)
        )
        return X.to_frame()

class DimensionReducer(BaseEstimator,TransformerMixin):
    """
    Class defining a custom transformer that applies dimensionality reduction.
    For any given feature in the input dataset, this transformation assigns 
    the value 'value_lower' to values with count lower than the defined 'threshold'.
    While feature values with count higher or equal than the 'threshold' are 
    kept unchanged. 

    Parameters
    ----------
    TransformerMixin: class
        Implements method fit_transform().
    BaseEstimator: class
        Implements methods set_params() and get_params().
    threshold: int
        Cutoff value of feature count.
    value_lower: int or str
        Value used to replace transformed feature values.

    Returns
    -------
        pandas.dataframe
        Dataframe containing transformed data.                
    """    
    def __init__(self, threshold=None, value_lower=None):
        self.threshold = threshold
        self.value_lower = value_lower 
        
    def feature_selector(self,X,y=None):
        """Define dimensionality reduction transformation."""                        
        if isinstance(X, pd.DataFrame):
            # convert dataframe to series
            X = X.squeeze('columns').copy()         
        else:
            X = pd.Series(X).copy()
        series_feature = X.value_counts(ascending=False)
        self.series_feature_above = series_feature[series_feature >= self.threshold]
        self.series_feature_below = series_feature[series_feature < self.threshold]
        print(f"Total categories in feature: {len(series_feature)}")
        print(f"Total categories in feature (above threshold = {self.threshold}): {len(self.series_feature_above)}")
        print(f"Total categories in feature (below threshold = {self.threshold}): {len(self.series_feature_below)}")          

    def fit(self,X,y=None):
        """Fit dimensionality reduction transformation to the input dataset."""                                
        self.feature_selector(X)
        return self
    
    def transform(self,X,y=None):
        """Apply dimensionality reduction transformation to input dataset."""                
        if isinstance(X, pd.DataFrame):
            # convert dataframe to series
            X = X.squeeze('columns').copy()        
        else:
            X = pd.Series(X).copy()        
        X = X.apply(
            lambda x: self.value_lower if x in self.series_feature_below else x
        )        
        return X.to_frame()

def predict_price(flat_surface=None,flat_bedrooms=None,flat_bathrooms=None,flat_location=None):
    """
    Predict rent price for an apartment described by the entered fields.
    
    Parameters
    ----------
    flat_surface: float
        Apartment surface in square meters.
    flat_bedrooms: int
        Number of bedrooms in apartment.
    flat_bathrooms: int
        Number of bathrooms in apartment.       
    flat_location: str
        Location of the apartment.                
        
    Returns
    -------
        int.
        Predicted rent price for the apartment.        
    """       
    df = pd.DataFrame({
        'Surface': [flat_surface],
        'Bedrooms': [flat_bedrooms],
        'Bathrooms': [flat_bathrooms],
        'Location': [flat_location]
    })
    # print(df)
    
    x_pred = []
    for i, model in enumerate(__models):
        idx_features = [int(i) for i in __model_features[i]]        
        x = __data_pipeline.transform(df).toarray()
        x = x[:, idx_features]
        x_pred.append(__models[i].predict(x)[0])

    # print(round(np.array(x_pred).mean(),2))
    return int(np.array(x_pred).mean())

def load_saved_artifacts():
    """
    Set global variables to artifacts loaded from local directory.            
    """     

    global __data_pipeline
    global __data_locations    
    global __models    
    global __model_features    

    if __data_pipeline is None:
        # __data_pipeline = joblib.load('/home/app/server/artifacts/pipe_all.pkl')        
        __data_pipeline = joblib.load(f"{__path}/pipe_all.pkl")                

    if __data_locations is None:
        # locations = sorted(joblib.load('/home/app/server/artifacts/list_location_geojson.pkl'))
        locations = sorted(joblib.load(f"{__path}/list_location_geojson.pkl"))        
        __data_locations = [l.title() for l in locations]
        # __data_locations = sorted(joblib.load('server/artifacts/list_location_encoded.pkl'))        

    if __models is None:
        # features = joblib.load('/home/app/server/artifacts/RENT_APARTMENT_RM_features.pkl')
        features = joblib.load(f"{__path}/RENT_APARTMENT_RM_features.pkl")        
        
        __models = []
        __model_features = []
        fs = ['model_xgb_f15_t436.pkl', 'model_xgb_f15_t474.pkl']
        
        for f in fs:
            key_feature = int(f.split('_f')[-1][:2])
            __model_features.append(features[key_feature])
            # __models.append(joblib.load(f"/home/app/server/artifacts/{f}"))
            __models.append(joblib.load(f"{__path}/{f}"))            

def get_location_names():
    """
    Retrieve names of the available apartment locations.
    
    Returns
    -------
        List containing available apartment locations.                  
    """         
    return __data_locations

if __name__ == '__main__':
    load_saved_artifacts()
    print(get_location_names())
    print(predict_price(flat_surface=50,flat_bedrooms=2,flat_bathrooms=1,flat_location='Independencia'))    
    print(predict_price(flat_surface=50,flat_bedrooms=2,flat_bathrooms=1,flat_location='Santiago'))
    print(predict_price(flat_surface=50,flat_bedrooms=2,flat_bathrooms=1,flat_location='Vitacura'))
    print(predict_price(flat_surface=50,flat_bedrooms=2,flat_bathrooms=1,flat_location='Las Condes'))
    print(predict_price(flat_surface=100,flat_bedrooms=3,flat_bathrooms=2,flat_location='Independencia'))
    print(predict_price(flat_surface=100,flat_bedrooms=3,flat_bathrooms=2,flat_location='Santiago'))    
    print(predict_price(flat_surface=100,flat_bedrooms=3,flat_bathrooms=2,flat_location='Vitacura'))
    print(predict_price(flat_surface=100,flat_bedrooms=3,flat_bathrooms=2,flat_location='Las Condes'))        
    
from flask import Flask, request, jsonify
import util
from util import CustomOrdinalEncoder, DimensionReducer

app = Flask(__name__)

@app.route('/get_location_names', methods=['GET'])
def get_location_names():
    """
    Retrieve response of a GET request that returns the names of the available. 
    apartment locations.
    
    Returns
    -------
        response: instance of flask.wrappers.Response
        Response to the GET request, serialized to JSON.                  
    """      
    response = jsonify({
        'locations': util.get_location_names()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    print(type(response))

    return response

@app.route('/predict_price', methods=['POST'])
def predict_price():
    """
    Retrieve response of a POST request that returns predicted rent price for 
    an apartment. 
    
    Returns
    -------
        response: instance of flask.wrappers.Response
        Response to the POST request, serialized to JSON.                  
    """        
    flat_surface = float(request.form['flat_surface'])
    flat_bedrooms = int(request.form['flat_bedrooms'])
    flat_bathrooms = int(request.form['flat_bathrooms'])
    flat_location = str(request.form['flat_location'])

    response = jsonify({
        'predicted_price': util.predict_price(flat_surface,flat_bedrooms,flat_bathrooms,flat_location)
    })
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

if __name__ == "__main__":
    print("Starting Python Flask Server...")
    util.load_saved_artifacts()
    # print(util.__data_pipeline)    
    # print(util.__data_locations)
    # app.run()
    app.run(host='0.0.0.0', port=8080, debug=True)
function onClickedPredictPrice() {
  console.log("Estimate price button clicked");
  var area = document.getElementById("uiArea");
  var bedrooms = document.getElementById("uiBedrooms");
  var bathrooms = document.getElementById("uiBathrooms");  
  // var type = getType();
  var location = document.getElementById("uiLocations");
  var price = document.getElementById("uiPredictPrice");

  // var url = "http://127.0.0.1:5000/predict_price"; // Use this when nginx is NOT used
  var url = "/api/predict_price"; // Use this when nginx is used

  $.post(url, {
      flat_surface: parseFloat(area.value),
      flat_bedrooms: parseInt(bedrooms.value),
      flat_bathrooms: parseInt(bathrooms.value),      
      flat_location: location.value
  },function(data, status) {
      console.log(data.predicted_price);
      price.innerHTML = "<h2>" + data.predicted_price.toString() + " CLP</h2>";
      // price.innerHTML = "<h2>" + type + "</h2>";
      console.log(status);
  });
}

function onPageLoad() {
  console.log( "document loaded" );
  // var url = "http://127.0.0.1:5000/get_location_names"; // Use this when nginx is NOT used
  var url = "/api/get_location_names"; // Use this when nginx is used
  $.get(url,function(data, status) {
      // console.log(data);
      console.log("got response for get_location_names request");
      // console.log(data.locations);
      if(data) {
          var locations = data.locations;
          var uiLocations = document.getElementById("uiLocations");
          $('#uiLocations').empty();
          for(var i in locations) {
              var opt = new Option(locations[i]);
              $('#uiLocations').append(opt);
          }
      }
  });
}

window.onload = onPageLoad;

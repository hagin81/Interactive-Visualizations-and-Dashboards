// send request to /names and populate select dropdown

var names_url = '/names';

Plotly.d3.json(names_url, function(error, response) {

    if (error) return console.warn(error);

    // Grab values from the response json object to build the plots
    //alert( response );

    var select = document.getElementById("selDataset");  


for (var i = 0; i < response.length; i++) {
    var opt = response[i];
    var el = document.createElement("option");
    el.textContent = opt;
    el.value = opt;
    select.appendChild(el);
}
   
   
 });

// default plot on page load
plot("BB_940");

// handle sample change
function optionChanged(data) {
   
   plot(data);
} 

function plot(data) {

   // title of plot 
   var selected = document.getElementById('selDataset').value;
   document.getElementById('chart-title').innerHTML = selected;

   sample_url =  `/samples/${data}`;

   Plotly.d3.json(sample_url, function(error, response) {

    if (error) return console.warn(error);

    console.log( response )
    window.mydata = response;

    var values, otu_ids; 
    for ( var i in response ) {

    	values = response[i]['sample_values'];
    	otu_ids = response[i]['otu_ids'];
    }

    values_ten =  values.slice(0, 10);
     ids_ten = otu_ids.slice(0,10);

    var data = [{
  values:  values_ten,
  labels: ids_ten,
  type: 'pie'
}];

var layout = {
  height: 400,
  width: 500
};


// pie chart 
Plotly.newPlot('chart', data, layout);

// bubble chart 
var trace1 = {
  x: ids_ten,
  y: values_ten,
  mode: 'markers',
  marker: {
    size: values_ten
  }
};

var bubble_data = [trace1];

var bubble_layout = {
  showlegend: false,
  height: 400,
  width: 500
};

Plotly.newPlot('bubble', bubble_data, bubble_layout);

});


// update meta section 
meta_url = `/metadata/${data}`;

Plotly.d3.json(meta_url, function(error, response) {

console.log( response );
document.getElementById('meta').innerHTML = '';

for ( var i in response ) {

     
	 document.getElementById('meta').innerHTML += i + ':' + response[i] + '<br>';
}

});

}

# import necessary libraries
import json
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Column, Integer, String, Numeric, Text, Float, Date
from flask import (
    Flask,
    render_template,
    url_for,
    jsonify,
    request)

engine = create_engine("sqlite:///belly_button_biodiversity.sqlite")
conn = engine.connect()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/names')
def names():    
    """List of sample names.

    Returns a list of sample names in the format
    [
        "BB_940",
        "BB_941",
        "BB_943",
        "BB_944",
        "BB_945",
        "BB_946",
        "BB_947",
        ...
    ]

    """
    conn = engine.connect()
    query = 'select * from samples'
    row = conn.execute( query ).fetchone()
    names  = row.keys()
    return jsonify( names ) 
    
@app.route('/otu')
def otu():
    """List of OTU descriptions.

    Returns a list of OTU descriptions in the following format

    [
        "Archaea;Euryarchaeota;Halobacteria;Halobacteriales;Halobacteriaceae;Halococcus",
        "Archaea;Euryarchaeota;Halobacteria;Halobacteriales;Halobacteriaceae;Halococcus",
        "Bacteria",
        "Bacteria",
        "Bacteria",
        ...
    ]
    """

    conn = engine.connect()
    query = 'select lowest_taxonomic_unit_found  from otu'
    results = conn.execute( query ).fetchall()
    data = [i['lowest_taxonomic_unit_found']  for i in results ]
    return jsonify( data )


@app.route('/metadata/<sample>')
def metadata(sample):
    """MetaData for a given sample.

    Args: Sample in the format: `BB_940`

    Returns a json dictionary of sample metadata in the format

    {
        AGE: 24,
        BBTYPE: "I",
        ETHNICITY: "Caucasian",
        GENDER: "F",
        LOCATION: "Beaufort/NC",
        SAMPLEID: 940
    }
    """
    conn = engine.connect()
    sampleid = sample.replace('BB_','')
    query = 'select * from samples_metadata where sampleid={}'.format(sampleid)

    results = conn.execute( query ).fetchall()
    data = {}
    for i in results:
        data['AGE'] = i['AGE']
        data['BBTYPE'] = i['BBTYPE']
        data['ETHNICITY'] = i['ETHNICITY']
        data['GENDER'] = i['GENDER']
        data['LOCATION'] = i['LOCATION']
        data['SAMPLEID'] = i['SAMPLEID']  

    return jsonify( data )

@app.route('/wfreq/<sample>')
def wfreq(sample):
    """Weekly Washing Frequency as a number.

    Args: Sample in the format: `BB_940`

    Returns an integer value for the weekly washing frequency `WFREQ`
    """
    conn = engine.connect()
    sampleid = sample.replace('BB_','')
    query = "select WFREQ from samples_metadata where sampleid={}".format(sampleid)
    results = conn.execute( query ).fetchall()
    data = ''
    for i in results:
        data = str(i['WFREQ'])

    return data


@app.route('/samples/<sample>')
def samples(sample):
    """OTU IDs and Sample Values for a given sample.

    Sort your Pandas DataFrame (OTU ID and Sample Value)
    in Descending Order by Sample Value

    Return a list of dictionaries containing sorted lists  for `otu_ids`
    and `sample_values`

    [
        {
            otu_ids: [
                1166,
                2858,
                481,
                ...
            ],
            sample_values: [
                163,
                126,
                113,
                ...
            ]
        }
    ]
    """
    conn = engine.connect()
    query = 'select samples.otu_id, otu.lowest_taxonomic_unit_found, samples.{}  from samples  inner join  otu on samples.otu_id=otu.otu_id'.format(sample)
    
    results = conn.execute( query ).fetchall()
    otu_ids = [ i['otu_id'] for i in  results ]
    sample_values = [ i[sample] for i in results ]
    
    # read data into pandas DataFrame and sort desc by sample_values
    df = pd.DataFrame([ otu_ids, sample_values ]).transpose()
    df.columns = [ 'otu_ids', 'sample_values']
    df.sort_values(by='sample_values', ascending=False, inplace=True )

    ids = df['otu_ids'].tolist()
    samples = df['sample_values'].tolist()

    data = { "otu_ids": ids, "sample_values": samples } 

    return jsonify([ data ])

if __name__ == "__main__":
    app.run(debug=True)

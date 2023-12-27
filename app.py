# Importing necessary libraries
from flask import Flask, render_template, request
import pandas as pd
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch('http://localhost:9200')
index_name = 'data'

# Indexing documents in Elasticsearch
df = pd.read_csv(r'C:\Users\Zeh\Desktop\search\Charts.csv')
documents = df.to_dict(orient='records')
for doc in documents:
    es.index(index=index_name, body=doc)

# Creating flask routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']

# Search function
    search_query = {
        'query': {
            'bool': {
                'should': [
                    {'match': {'song': query}},
                    {'match': {'performer': query}}
                ]
            }
        }
    }

    res = es.search(index=index_name, body=search_query)

    hits = res['hits']['hits']

    results = []
    for hit in hits:
        result = hit['_source']
        results.append(result)

    df = pd.DataFrame(results)

    return render_template('results.html', df=df)

# Adding new songs to database
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        song = request.form['song']
        performer = request.form['performer']

        new_doc = {
            'song': song,
            'performer': performer
        }

        es.index(index=index_name, body=new_doc)

        return render_template('add.html', message='Document added successfully!')
    
    return render_template('add.html', message='')


if __name__ == '__main__':
    app.run()
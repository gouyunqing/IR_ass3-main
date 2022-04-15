from flask import Flask, render_template, request, Response
import yaml
from elasticsearch import Elasticsearch
import yaml
import nltk
from nltk.corpus import PlaintextCorpusReader,wordnet
from nltk import sent_tokenize, word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from pprint import pprint
import json
import pickle

from search import search, parse_query

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('search.html')


@app.route("/search", methods=['GET', 'POST'])
def get_es():
    if request.method == 'POST':
        raw_query = request.form.get('query')
        query = parse_query(query=raw_query, lem=lem, english_punctuations=english_punctuations)

        result = search(query=raw_query, es=es, index_name=index_name, id2page_rank=id2page_rank)

        print(result)

        return Response(json.dumps(result), mimetype='application/json')


if __name__ == '__main__':
    # load config from config.yaml
    f = open('config/config.yaml', 'r', encoding='utf-8')
    cfg = f.read()
    config_dict = yaml.load(cfg, Loader=yaml.FullLoader)

    path = config_dict['data_config']['path']
    index_name = config_dict['es_config']['index_name']
    host = config_dict['es_config']['host']
    port = config_dict['es_config']['port']

    with open('id2page_rank.pickle', 'rb') as f:
        id2page_rank = pickle.load(f)

    es = Elasticsearch(host=host, port=port)
    english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']
    lem = WordNetLemmatizer()
    print('ES object instantiation')

    app.debug=True
    app.run()
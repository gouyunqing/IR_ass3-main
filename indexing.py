from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

import pickle
import yaml


def insert_data(path, es, index_name):
    with open(path, 'rb') as f:
        id2corpus = pickle.load(f)
        try:
            for id in id2corpus.keys():
                print(id)
                text = id2corpus[id]
                data = {'id': id, 'text': text}

                print(text)

                es.index(index=index_name,
                         body=data)
        except:
            print('Error: unable to insert data')


if __name__ == '__main__':
    setting = {
        "settings": {
            "analysis": {
                "filter": {
                    "english_stop": {
                        "type": "stop",
                        "stopwords": "_english_"
                    },
                    "english_keywords": {
                        "type": "keyword_marker",
                        "keywords": ["example"]
                    },
                    "english_stemmer": {
                        "type": "stemmer",
                        "language": "english"
                    },
                    "english_possessive_stemmer": {
                        "type": "stemmer",
                        "language": "possessive_english"
                    }
                },
                "analyzer": {
                    "english": {
                        "tokenizer": "standard",
                        "filter": [
                            "english_possessive_stemmer",
                            "lowercase",
                            "english_stop",
                            "english_keywords",
                            "english_stemmer"
                        ]
                    }
                }
            },
            "index": {
                "similarity": {
                    "my_similarity": {
                        "type": "BM25",
                        "b": "0.75",
                        "k1": "1"
                    }
                }
            },
            "number_of_replicas": 1,
            "number_of_shards": 1
        }
    }

    mapping = {
        "properties": {
            "id": {
                "type": "integer"
            },
            "text": {
                "type": "text",
                "analyzer": "english",
                "similarity": "my_similarity",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            }
                    }
    }

    # load config from config.yaml
    f = open('config/config.yaml', 'r', encoding='utf-8')
    cfg = f.read()
    config_dict = yaml.load(cfg, Loader=yaml.FullLoader)

    path = config_dict['data_config']['path']
    index_name = config_dict['es_config']['index_name']
    host = config_dict['es_config']['host']
    port = config_dict['es_config']['port']

    es = Elasticsearch(host=host, port=port)

    es.indices.create(index=index_name,
                      body=setting)
    es.indices.put_mapping(body=mapping, index=index_name)

    insert_data(path, es, index_name)
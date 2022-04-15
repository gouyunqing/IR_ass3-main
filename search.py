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


def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def parse_query(query, lem, english_punctuations):

    query_tokens = word_tokenize(query)
    # remove punctuation
    tokens = [token.lower() for token in query_tokens if token not in english_punctuations]
    # lemmitize

    tokens_pos = nltk.pos_tag(tokens)
    pos_list = [token_pos[1] for token_pos in tokens_pos]
    lemed_tokens = []
    for i in range(len(tokens)):
        pos = get_wordnet_pos(pos_list[i])
        if pos:
            lemed_tokens.append(lem.lemmatize(tokens[i], pos))
        else:
            lemed_tokens.append(lem.lemmatize(tokens[i]))
    #         lemed_tokens = [lem.lemmatize(tokens[i], get_wordnet_pos(pos_list[i])) for i in range(len(tokens)) ]

    # remove stopwords
    query = [word for word in lemed_tokens if word not in stopwords.words('english')]
    query = ' '.join(query)

    return query


def search(query, es, index_name, id2page_rank):
    body = {
        'query': {
            'match': {
                'text': query
            }
        }
    }

    result = es.search(index=index_name, body=body)
    # pprint(result)
    id2text = {}
    id2score = {}
    final_result = {}
    hits_list = result['hits']['hits']
    # print(hits_list['hits'])
    for hit in hits_list:
        entity = hit['_source']
        id = entity['id']
        text = entity['text']
        score = hit['_score']
        if id in id2page_rank.keys():
            pr = id2page_rank[id]
        else:
            pr = 0.5
        final_score = score+pr

        id2text[id] = text
        id2score[id] = final_score

    new_id2score = sorted(id2score.items(), key=lambda x: x[1], reverse=True)
    # print(new_id2score[0][0])
    for i in range(len(new_id2score)):
        final_result[new_id2score[i][0]] = id2text[new_id2score[i][0]]

    # add pagerank

    return final_result


# if __name__ == '__main__':
#     # load config from config.yaml
#     f = open('config/config.yaml', 'r', encoding='utf-8')
#     cfg = f.read()
#     config_dict = yaml.load(cfg, Loader=yaml.FullLoader)
#
#     host = config_dict['es_config']['host']
#     port = config_dict['es_config']['port']
#     index_name = config_dict['es_config']['index_name']
#
#     # body = {"query": {"match_all": {}}}
#
#     es = Elasticsearch(host=host, port=port)
#     with open('id2page_rank.pickle', 'rb') as f:
#         id2page_rank = pickle.load(f)
#     # result = es.search(index="ir_ass3", doc_type="_doc", body=body)
#     # print(result)
#
#     english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']
#     lem = WordNetLemmatizer()
#
#     result = search('Minimum memory', es, index_name, id2page_rank)
#
#     print(result)
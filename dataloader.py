import pandas as pd
import numpy as np

import bigjson

from tqdm import tqdm

import nltk
from nltk.corpus import PlaintextCorpusReader,wordnet
from nltk import sent_tokenize, word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

import pickle


count = 0
references_dict = {'id': [],
                   'title': [],
                   'doc_type': [],
                   'publisher': [],
                   'venue_name': [],
                   'venue_ID': [],
                   'references': []}

with open('./data/dblp.v12.json', 'rb') as f:
    j = bigjson.load(f)
    print('begin')
    while count < 1000:
        element = j[count]
        if count%1000 == 0:
            print(count)
        if 'references' in element.keys():
            for i, val in enumerate(element['references']):
                references_dict['references'].append(element['references'][i])
                references_dict['id'].append(element['id'])
                references_dict['title'].append(element['title'])
                if element['publisher'] != "":
                    references_dict['publisher'].append(element['publisher'])
                else:
                    references_dict['publisher'].append(np.nan)
                if element['doc_type'] != "":
                    references_dict['doc_type'].append(element['doc_type'])
                else:
                    references_dict['doc_type'].append(np.nan)
                if 'venue' in element.keys():
                    if 'raw' in element['venue'].keys():
                        references_dict['venue_name'].append(element['venue']['raw'])
                    else:
                        references_dict['venue_name'].append(np.nan)
                    if 'id' in element['venue'].keys():
                        references_dict['venue_ID'].append(element['venue']['id'])
                    else:
                        references_dict['venue_ID'].append(np.nan)
                else:
                    references_dict['venue_name'].append(np.nan)
                    references_dict['venue_ID'].append(np.nan)

        else:
            references_dict['references'].append(np.nan)
            references_dict['id'].append(element['id'])
            references_dict['title'].append(element['title'])

            if element['publisher'] != "":
                references_dict['publisher'].append(element['publisher'])
            else:
                references_dict['publisher'].append(np.nan)

            if element['doc_type'] != "":
                references_dict['doc_type'].append(element['doc_type'])
            else:
                references_dict['doc_type'].append(np.nan)

            if 'venue' in element.keys():
                if 'raw' in element['venue'].keys():
                    references_dict['venue_name'].append(element['venue']['raw'])
                else:
                    references_dict['venue_name'].append(np.nan)
                if 'id' in element['venue'].keys():
                    references_dict['venue_ID'].append(element['venue']['id'])
                else:
                    references_dict['venue_ID'].append(np.nan)
            else:
                references_dict['venue_name'].append(np.nan)
                references_dict['venue_ID'].append(np.nan)

        count = count + 1

data = pd.DataFrame.from_dict(references_dict)
print(data.shape)

lem = WordNetLemmatizer()
english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']

# indexing using tf-idf
id2new_corpus = {}
id2reference = {}

new_corpus = []


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


for i in range(data.shape[0]):
    # add reference
    reference = data.iloc[i][6]
    id = data.iloc[i][0]

    if id not in id2reference.keys():
        if reference == reference:
            id2reference[id] = [int(reference)]
    elif reference == reference:
        id2reference[id].append(int(reference))
    # indexing
    if data.iloc[i][0] not in id2new_corpus.keys():
        title = data.iloc[i][1]
        tokens = word_tokenize(title)
        # remove punctuation
        tokens = [token.lower() for token in tokens if token not in english_punctuations]
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
        filtered_words = [word for word in lemed_tokens if word not in stopwords.words('english')]
        new_corpus.append(' '.join(filtered_words))
        id2new_corpus[id] = ' '.join(filtered_words)

with open('corpus.pickle', 'wb') as f:
    pickle.dump(new_corpus, f, pickle.HIGHEST_PROTOCOL)

with open('id2reference.pickle', 'wb') as f:
    pickle.dump(id2reference, f, pickle.HIGHEST_PROTOCOL)

with open('id2corpus.pickle', 'wb') as f:
    pickle.dump(id2new_corpus, f, pickle.HIGHEST_PROTOCOL)

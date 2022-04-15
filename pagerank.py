import numpy as np
import pickle
import yaml


def move_matrix(m):
    num = (m.sum(axis = 0) + 1)
    return m/num


def V(c):
    pr = np.ones((c.shape[0],1),dtype=float)/len(c)
    return pr


def PR(p,m,v):
    i = 0
    while 1:
        v1 = p*np.dot(m,v) + (1-p) * v
        if np.abs((v-v1).all()) < 0.001:
            break
        else:
            v = v1
        i += 1
        if i==20:break

    return v


def page_rank(id2reference):
    id2page_rank = {}
    matrix_id2id = {}
    id2matrix_id = {}

    i = 0
    for key in id2reference.keys():
        if key not in matrix_id2id.values():
            matrix_id2id[i] = key
            id2matrix_id[key] = i
            i += 1
        for value in id2reference[key]:
            if value not in matrix_id2id.values():
                matrix_id2id[i] = value
                id2matrix_id[value] = 1
                i += 1
    M = np.zeros((i, i), dtype=float)

    for key in id2reference.keys():
        matrix_key = id2matrix_id[key]
        values = id2reference[key]
        for value in values:
            matrix_value = id2matrix_id[value]
            M[matrix_key][matrix_value] = 1000

    M1 = move_matrix(M)
    V1 = V(M1)
    a = 0.85

    pr = PR(a, M1, V1)

    for i in range(pr.shape[0]):
        id2page_rank[matrix_id2id[i]] = pr[i][0] * 1e20

    return id2page_rank


if __name__ == '__main__':
    f = open('config/config.yaml', 'r', encoding='utf-8')
    cfg = f.read()
    config_dict = yaml.load(cfg, Loader=yaml.FullLoader)

    ref_path = config_dict['data_config']['ref_path']
    with open(ref_path, 'rb') as f:
        id2reference = pickle.load(f)

    id2page_rank = page_rank(id2reference)
    with open('id2page_rank.pickle', 'wb') as f:
        pickle.dump(id2page_rank, f, pickle.HIGHEST_PROTOCOL)
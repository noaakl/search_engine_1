import json
import os
import string
import utils




def expand_query(query,word_index, index_word_table):
    if index_word_table == {} or word_index == {} : return query
    tokens_to_add = []
    for word in query:
        if word.lower() in word_index.keys():
            associate_index = word_index[word.lower()][2][0]
            if associate_index != -1 and  word_index[word.lower()][2][1] != 0 :
                if word_index[word.lower()]:
                    associate_index = word_index[word.lower()][2][0]
                    tokens_to_add.append(index_word_table[str(associate_index)])
        elif word.upper() in word_index:
            associate_index = word_index[word.upper()][2][0]
            if associate_index != -1 and  word_index[word.upper()][2][1] != 0:
                if word_index[word.upper()]:
                    tokens_to_add.append(index_word_table[str(associate_index)])
    return tokens_to_add + query

def get_matrix_shape(minimum_df ,inv_index):
    shape = 0
    for word in inv_index:
        if minimum_df <= inv_index[word][0] and word.isalpha():
            shape += 1
    return shape


def create_association_matrix(inv_index, posting_dict):
    """
    this function expand the given query
    :param config:
    :param inv_index:
    :return: list of tokens
    """
    list_of_dfs = [value[0] for key, value in inv_index.items() if value[0] > 5 and key.isalpha()]
    minimum_df = sum(list_of_dfs)/len(list_of_dfs)
    index_word_table = {}
    word_index = {}  # {word: [index, {doc1: f, doc2: f...}, [index,corolation]}

    size = get_matrix_shape(minimum_df,inv_index)
    association_matrix = [[0 for i in range(size)] for j in range(size)]


    index = 0

    num_of_terms = 0


    for word1 in posting_dict:
        # if the word is important
        try:
            if minimum_df <= inv_index[word1.lower()][0] and word1.isalpha():
                # add index to word index
                word_index[word1.lower()] = [index, {}, [-1, -1]]  # index in matrix, {documents} , [index,corolation]
                index_word_table[index] = word1.lower()
                num_of_terms += 1
            else:
                continue
        except:
            if minimum_df <= inv_index[word1.upper()][0] and word1.isalpha():
                word1 = word1.upper()
                word_index[word1] = [index, {}, [-1, -1]]
                index_word_table[index] = word1.upper()
                num_of_terms += 1
            else:
                continue
            # add docID and frequency to word index
        for doc in posting_dict[word1.lower()].items():
            word_index[word1][1][doc[0]] = doc[1][1]

        index += 1
        # i is the index of word1 in the matrix
        i = word_index[word1][0]
        for word2 in word_index.keys():
            # j is the index of word2 in the matrix
            j = word_index[word2][0]
            for d in word_index[word1][1].keys():
                if d in word_index[word2][1].keys():
                    try:
                        association_matrix[i][j] += word_index[word1][1][d] * word_index[word2][1][d]
                        if word1 != word2:
                            association_matrix[j][i] += word_index[word1][1][d] * word_index[word2][1][d]
                    except:
                        print(str(i), word1, " , ", str(j), word2)
                        print("num_of_terms = " + num_of_terms, " size = " + size)
    for word in word_index:
        word_index[word][1] =0
    final_association_matrix = [[0 for i in range(size)] for j in range(size)]
    if len(word_index) != size:
        print("size not equal ")
        return
    for i in range(size):
        for j in range(size):
            try:
                if i == j:
                    final_association_matrix[i][j] = 0
                else:
                    final_association_matrix[i][j] = association_matrix[i][j] / (
                                association_matrix[i][i] + association_matrix[j][j] - association_matrix[i][j])
                    word1 = index_word_table[i]
                    if 1 > final_association_matrix[i][j] > 0.8:
                        if final_association_matrix[i][j] > word_index[word1][2][1]:
                            word_index[word1][2][1] = final_association_matrix[i][j]
                            word_index[word1][2][0] = j
            except:
                print('i= ' + str(i) + ', j= ' + str(j) + ' down= ' + str(
                    association_matrix[i][i] + association_matrix[j][j] - association_matrix[i][j]))

    utils.save_obj(final_association_matrix, "association_matrix")
    utils.save_obj(word_index, "word_index")
    utils.save_obj(index_word_table, "index_word_table")





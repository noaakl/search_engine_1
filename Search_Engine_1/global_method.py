

def get_matrix_shape(minimum_df, inv_index):
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
    list_of_dfs = [value[0] for key, value in inv_index.items() if value[0] > 12 and key.isalpha()]
    minimum_df = sum(list_of_dfs) / len(list_of_dfs)
    index_word_table = {}
    word_index = {}  # {word: [index, {doc1: f, doc2: f...}, [index,corolation]}

    size = get_matrix_shape(minimum_df, inv_index)
    association_matrix = {}
    print("start first matrix")
    index = 0

    num_of_terms = 0

    for word1 in posting_dict:
        # if the word is important
        try:
            if minimum_df <= inv_index[word1.lower()][0] and word1.isalpha():
                # add index to word index
                word_index[word1.lower()] = [index, {}]  # index in matrix, {documents} , [index,corolation]
                index_word_table[index] = word1.lower()
                num_of_terms += 1
            else:
                continue
        except:
            if minimum_df <= inv_index[word1.upper()][0] and word1.isalpha():
                word1 = word1.upper()
                word_index[word1] = [index, {}]
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
                        if (i, j) in association_matrix:
                            association_matrix[(i, j)] += word_index[word1][1][d] * word_index[word2][1][d]
                        else:
                            association_matrix[(i, j)] = word_index[word1][1][d] * word_index[word2][1][d]

                    except:
                        print(str(i), word1, " , ", str(j), word2)
                        print("num_of_terms = " + num_of_terms, " size = " + size)
    for word in word_index:
        word_index[word][1] = 0


    # final_association_matrix = [[0 for i in range(size)] for j in range(size)]
    print("start second matrix")
    final_association_matrix = {}
    if len(word_index) != size:
        print("size not equal ")
        return
    for i in range(size):
        for j in range(size):
            try:
                if i != j:
                    if (i, j) in association_matrix:
                        calculation = association_matrix[(i, j)] / (
                                association_matrix[(i, i)] + association_matrix[(j, j)] - association_matrix[(i, j)])
                        if calculation >= 0.8:
                            final_association_matrix[(i, j)] = calculation
                    elif (j, i) in association_matrix:
                        calculation = association_matrix[(j, i)] / (
                                association_matrix[(i, i)] + association_matrix[(j, j)] - association_matrix[(j, i)])
                        if calculation >= 0.8:
                            final_association_matrix[(j, i)] = calculation
            except:
                print(i, j)
    print("start correlated words")
    correlated_words = {}
    for word1_idx, word2_idx in final_association_matrix.keys():
        word1 = index_word_table[word1_idx]
        word2 = index_word_table[word2_idx]
        try:
            if correlated_words[word1][0] > final_association_matrix[(word1_idx, word2_idx)]:
                correlated_words[word1] = [final_association_matrix[(word1_idx, word2_idx)], word2]

        except:
            correlated_words[word1] = [final_association_matrix[(word1_idx, word2_idx)], word2]
        try:
            if correlated_words[word2][0] > final_association_matrix[(word1_idx, word2_idx)]:
                correlated_words[word2] = [final_association_matrix[(word1_idx, word2_idx)], word1]

        except:
            correlated_words[word2] = [final_association_matrix[(word1_idx, word2_idx)], word1]


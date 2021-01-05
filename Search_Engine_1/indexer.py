import math


def get_info_for_posting(word, document, is_term):
    if is_term:
        df = document.term_doc_dictionary[word.lower()]
    else:
        df = document.entity_dict[word.upper()]
    tf = int(df) / document.get_num_of_uniq_words()
    is_upper = word.isupper()  # TODO: check
    return [tf, df, is_upper]

# DO NOT MODIFY CLASS NAME
class Indexer:
    num_of_docs = 0
    sum_of_appearances = 0

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implmentation as you see fit.
    def __init__(self, config):
        self.inverted_idx = {}  # term: [df, f ,idf]
        self.postingDict = {}  # term: {doc: [tf, df, is_upper]}
        self.config = config
        self.doc_file = {}
        self.entities = {}  # dictionary for pending entities (only one time so far in corpus)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implmentation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        doc_term_dict = document.term_doc_dictionary
        doc_entity_dict = document.entity_dict
        # Go over each term in the doc
        for term in doc_term_dict.keys():
            try:
                self.add_term(document, term)
            except:
                print('problem with the following key {}'.format(term))

        for entity in doc_entity_dict:
            try:
                self.add_entity(document, entity)
            except:
                print('problem with the following key {}'.format(entity))

        # self.postingDict[term].append((document.tweet_id, doc_term_dict[term])) TODO: check if ok or change to this format

        self.doc_file[document.tweet_id] = document.get_doc_info()
        Indexer.num_of_docs += 1

    def add_term(self, document, term):
        """
        This function perform indexing process for all the terms in the document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param term: a term needs to be indexed
        :param document: curr document.
        :return: -
        """
        if term == "fuck":
            noaa = 'stop'
        doc_term_dict = document.term_doc_dictionary
        # Update inverted index
        change_upper_to_lower = False
        # term is already in inverted_idx
        if term.lower() in self.inverted_idx:
            self.inverted_idx[term.lower()][0] += 1
            self.inverted_idx[term.lower()][1] += doc_term_dict[term]

        # term is already in inverted_idx as an entity
        elif term.upper() in self.inverted_idx:
            change_upper_to_lower = True  # TODO: add if term.islower() ?
            self.inverted_idx[term.upper()][0] += 1
            self.inverted_idx[term.upper()][1] += doc_term_dict[term]

        # add a new term to inverted_idx
        else:
            self.inverted_idx[term.lower()] = [1, doc_term_dict[term]]

        # Update posting dict
        info = get_info_for_posting(term, document, True)
        if term.lower() in self.postingDict:  # term is already in postingDict
            self.postingDict[term.lower()][document.tweet_id] = info
        else:  # add new term to postingDict
            self.postingDict[term.lower()] = {}
            self.postingDict[term.lower()][document.tweet_id] = info

        # change term from upper to lower case in inverted_idx
        if change_upper_to_lower:
            to_lower_idx = self.inverted_idx.pop(term.upper())
            self.inverted_idx[term.lower()] = to_lower_idx

        Indexer.sum_of_appearances += 1

    def add_entity(self, document, entity):
        """
        This function perform indexing process for all the terms in the document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param entity: an entity needs to be indexed
        :param document: curr document.
        :return: -
        """
        doc_entity_dict = document.entity_dict
        prev_entity = None
        # Update inverted index
        # entity already appear twice in corpus in lowerCase
        if entity.lower() in self.inverted_idx:
            self.inverted_idx[entity.lower()][0] += 1
            self.inverted_idx[entity.lower()][1] += doc_entity_dict[entity]

        # entity already appear twice in corpus in upperCase
        elif entity.upper() in self.inverted_idx:
            self.inverted_idx[entity.upper()][0] += 1
            self.inverted_idx[entity.upper()][1] += doc_entity_dict[entity]

        # second time in corpus - append both tweets to invert_idx and posting
        elif entity.upper() in self.entities:
            prev_entity = self.entities.pop(entity.upper())
            if entity.lower() in self.inverted_idx:
                self.inverted_idx[entity.lower()][0] += 2
                self.inverted_idx[entity.lower()][1] += doc_entity_dict[entity] + prev_entity[1]
            else:
                self.inverted_idx[entity.upper()] = [2, doc_entity_dict[entity] + prev_entity[1]]
            Indexer.sum_of_appearances += 1

        # first time entity in corpus
        else:
            entity_info = get_info_for_posting(entity, document, False)
            self.entities[entity.upper()] = [{document.tweet_id: entity_info}, entity_info[1]]
            return

        # Update posting dict
        if entity.lower() in self.postingDict:
            if prev_entity:
                self.postingDict[entity.lower()].update(prev_entity[0])
            self.postingDict[entity.lower()][document.tweet_id] =\
                get_info_for_posting(entity, document, False)
        else:
            if prev_entity:
                self.postingDict[entity.lower()] = prev_entity[0]
            self.postingDict[entity.lower()] = {
                document.tweet_id: get_info_for_posting(entity, document, False)}

        Indexer.sum_of_appearances += 1

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implmentation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        raise NotImplementedError

    # feel free to change the signature and/or implmentation of this function 
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.postingDict

    # feel free to change the signature and/or implmentation of this function 
    # or drop altogether.
    def get_term_posting_list(self, term):
        """
        Return the posting list from the index for a term.
        """
        return self.postingDict[term] if self._is_term_exist(term) else []

    def check_pending_list(self):
        for entity in self.entities.keys():
            if entity.lower() in self.inverted_idx:
                # Update inverted index
                self.inverted_idx[entity.lower()][0] += 1
                self.inverted_idx[entity.lower()][1] += self.entities[entity][1]

                # Update posting dict
                if entity.lower() in self.postingDict:
                    self.postingDict[entity.lower()].update(self.entities[entity][0])
                else:
                    self.postingDict[entity.lower()] = self.entities[entity][0]

    def calculate_and_add_idf(self):
        """
        adds idf to the end of the list in the values in the inverted index.
        """
        for word in self.inverted_idx.items():
            word[1].append(math.log(Indexer.num_of_docs / word[1][0], 10))


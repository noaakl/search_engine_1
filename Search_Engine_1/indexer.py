import math
import utils


# DO NOT MODIFY CLASS NAME
class Indexer:
    num_of_docs = 0
    sum_of_appearances = 0

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implmentation as you see fit.
    def __init__(self, config):
        self.inverted_idx = {}  # term: [df ,idf]
        self.postingDict = {}  # term: {doc: [tf, df]}
        self.config = config
        self.doc_file = {}  # doc_id : [term_dict, date] later term_dict become sigmaWij fo save space
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
                pass

        for entity in doc_entity_dict:
            try:
                self.add_entity(document, entity)
            except:
                pass

        doc_term_dict.update(doc_entity_dict)
        self.doc_file[document.tweet_id] = document.get_doc_info()
        self.doc_file[document.tweet_id][0] = doc_term_dict  # doc_id : [ term_dict, date]
        Indexer.num_of_docs += 1

    def add_term(self, document, term):
        """
        This function perform indexing process for all the terms in the document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param term: a term needs to be indexed
        :param document: curr document.
        :return: -
        """
        doc_term_dict = document.term_doc_dictionary
        # Update inverted index
        change_upper_to_lower = False
        # term is already in inverted_idx
        if term.lower() in self.inverted_idx:
            self.inverted_idx[term.lower()][0] += 1

        # term is already in inverted_idx as an entity
        elif term.upper() in self.inverted_idx:
            change_upper_to_lower = True
            self.inverted_idx[term.upper()][0] += 1

        # add a new term to inverted_idx
        else:
            self.inverted_idx[term.lower()] = [1]

        # Update posting dict
        info = self.get_info_for_posting(term, document, True)

        if term.lower() in self.postingDict:  # term is already in postingDict
            self.postingDict[term.lower()][document.tweet_id] = info
        else:  # add new term to postingDict
            self.postingDict[term.lower()] = {}
            self.postingDict[term.lower()][document.tweet_id] = info

        # change term from upper to lower case in inverted_idx
        if change_upper_to_lower:
            to_lower_idx = self.inverted_idx.pop(term.upper())
            self.inverted_idx[term.lower()] = to_lower_idx

    def add_entity(self, document, entity):
        """
        This function perform indexing process for all the terms in the document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param entity: an entity needs to be indexed
        :param document: curr document.
        :return: -
        """
        prev_entity = None
        # Update inverted index
        # entity already appear twice in corpus in lowerCase
        if entity.lower() in self.inverted_idx:
            self.inverted_idx[entity.lower()][0] += 1

        # entity already appear twice in corpus in upperCase
        elif entity.upper() in self.inverted_idx:
            self.inverted_idx[entity.upper()][0] += 1

        # second time in corpus - append both tweets to invert_idx and posting
        elif entity.upper() in self.entities:
            prev_entity = self.entities.pop(entity.upper())
            if entity.lower() in self.inverted_idx:
                self.inverted_idx[entity.lower()][0] += 2
            else:
                self.inverted_idx[entity.upper()] = [2]

        # first time entity in corpus
        else:
            entity_info = self.get_info_for_posting(entity, document, False)
            self.entities[entity.upper()] = [{document.tweet_id: entity_info}, entity_info[1]]
            return

        # Update posting dict
        if entity.lower() in self.postingDict:
            if prev_entity:
                self.postingDict[entity.lower()].update(prev_entity[0])
            self.postingDict[entity.lower()][document.tweet_id] = \
                self.get_info_for_posting(entity, document, False)
        else:
            if prev_entity:
                self.postingDict[entity.lower()] = prev_entity[0]
            self.postingDict[entity.lower()] = {
                document.tweet_id: self.get_info_for_posting(entity, document, False)}

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implmentation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        with open(fn, 'rb') as f:
            indexer = pickle.load(f)
        self.inverted_idx = indexer[0]
        self.postingDict = indexer[1]
        self.doc_file = indexer[2]
        self.entities = {}

    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        utils.save_obj([self.inverted_idx, self.postingDict, self.doc_file], fn)

    # feel free to change the signature and/or implmentation of this function 
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.postingDict

    def get_posting_dict(self):
        return self.postingDict

    # feel free to change the signature and/or implmentation of this function 
    # or drop altogether.
    def get_term_posting_list(self, term):
        """
        Return the posting list from the index for a term.
        """
        try:
            result = self.postingDict[term]
            return result
        except:
            return {}

    def get_doc_information(self, doc_id):
        try:
            result = self.doc_file[doc_id]
            return result
        except:
            return {}

    def get_index(self):
        return self.inverted_idx

    def calculate_sigma_Wij(self):
        for doc_id, doc_info in self.doc_file.items():
            try:
                num_of_uniqe_words = len(doc_info[0])
            except:
                continue
            sigma_Wij_squere = 0
            for term in doc_info[0]:
                try:
                    # compute sigma Wij
                    sigma_Wij_squere += math.pow(
                        self.inverted_idx[term.lower()][1] * doc_info[0][term] / num_of_uniqe_words, 2)
                except:
                    try:
                        sigma_Wij_squere += math.pow(
                            self.inverted_idx[term.upper()][1] * doc_info[0][term] / num_of_uniqe_words, 2)
                    except:
                        pass
            self.doc_file[doc_id][0] = sigma_Wij_squere

    def check_pending_list(self):
        for entity in self.entities.keys():
            if entity.lower() in self.inverted_idx:
                # Update inverted index
                self.inverted_idx[entity.lower()][0] += 1
                # self.inverted_idx[entity.lower()][1] += self.entities[entity][1]

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

    def get_info_for_posting(self, word, document, is_term):
        if is_term:
            df = document.term_doc_dictionary[word.lower()]
        else:
            df = document.entity_dict[word.upper()]
        # tf = int(df) / document.get_num_of_uniq_words()
        tf = int(df) / document.doc_length
        return [tf, df]

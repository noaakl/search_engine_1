import pickle
import time

import pandas as pd

import utils
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import json
from nltk.corpus import wordnet


def word_net(terms):
    # TODO: without corona
    # TODO: think if save num of words or set
    # TODO: לחשוב על דרך לתת למילים המוספות פחות משקל
    extended_terms = set()
    for query_word in terms:
        # print("word: " + query_word)
        synset = wordnet.synsets(query_word)
        if len(synset) > 0:
            synset_lemmas = synset[0].lemmas()
            # if len(synset_lemmas) > 2:synset_lemmas = synset_lemmas[:2]  # add not more than 3
            # print("sort list is: ")
            syn = synset_lemmas[0]  # add only one
            name = syn.name()
            if name.islower() and not name.__contains__('_') and not name.__contains__('-') and name != "corona":
                extended_terms.add(name)
                # print(name)
    return list(extended_terms)


# DO NOT CHANGE THE CLASS NAME
class SearchEngine:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        if not config:
            self._config = ConfigClass()
        else:
            self._config = config
        self._parser = Parse()
        self._indexer = Indexer(config)
        self._model = None
        self._reader = ReadFile(self._config.get__corpusPath())

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implmentation as you see fit.
    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """
        df = pd.read_parquet(fn, engine="pyarrow")
        documents_list = df.values.tolist()
        # Iterate over every document in the file
        number_of_documents = 0
        for idx, document in enumerate(documents_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document)

            number_of_documents += 1
            # index the document data
            self._indexer.add_new_doc(parsed_document)

        self._indexer.check_pending_list()
        self._indexer.calculate_and_add_idf()
        self._indexer.calculate_sigma_Wij()

        # save inverted index
        utils.save_obj(self._indexer.inverted_idx, "idx_bench")
        # save posting dict
        utils.save_obj(self._indexer.postingDict, "posting")

        print('Finished parsing and indexing.')

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implmentation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        with open(fn, 'rb') as f:
            return pickle.load(f)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implmentation as you see fit.
    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and
        assign to self._model, which is passed on to the searcher at query time.
        """
        pass

    def search(self, query, k=None):  # TODO: change
        """
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and
            a list of tweet_ids where the first element is the most relavant
            and the last is the least relevant result.
        """

        terms, entities = self._parser.parse_sentence(query)
        query_as_list = terms + entities
        # word net
        extended_query = word_net(terms)
        searcher = Searcher(self._parser, self._indexer, model=self._model)
        return searcher.search_with_extension(query_as_list, extended_query, k)
        # return searcher.search(query_as_list, k)
        # return extended_query


def main():
    config = ConfigClass()
    search_engine = SearchEngine(config)
    # r'C:\Users\noaa\pycharm projects\search_engine_partC\Search_Engine_1\data\benchmark_data_train.snappy.parquet'#
    search_engine.build_index_from_parquet(
        r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\Search_Engine_1\data\benchmark_data_train.snappy.parquet')
    # search_engine.build_index_from_parquet(r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\\data\covid19_07-16.snappy.parquet')
    # search_engine.build_index_from_parquet(r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\\data\covid19_07-19.snappy.parquet')
    # results =search_engine.search("covid is fun 2020 US new  wear", 40)
    # for res in results[1]:
    #     print(res)


# terms = ["donald", "trump", "covid", "corona", "donald trump", "covid 19"]
# extended_terms = set(terms)
# for query_word in terms:
#     # print("word: " + query_word)
#     synset = wordnet.synsets(query_word)
#     if len(synset) > 0:
#         synset_lemmas = synset[0].lemmas()
#         if len(synset_lemmas) > 3:synset_lemmas = synset_lemmas[:3]  # add not more than 3
#         # print("sort list is: ")
#         for syn in synset_lemmas:
#         # syn = synset_lemmas[0]  # add only one
#             name = syn.name()
#             if name.islower() and not name.__contains__('_') and not name.__contains__('-'):
#                 print(query_word + ": " + name)
#                 extended_terms.add(name)
#                 # print(name)
# print(list(extended_terms))


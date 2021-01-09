import pickle
import time

import pandas as pd
from spellchecker import SpellChecker

import global_method
import utils
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import json


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
        utils.save_obj(self._indexer.postingDict, "posting")

        # save posting dict


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

    def search(self, query,k = None):
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
        start = time.time()
        terms, entities = self._parser.parse_sentence(query)
        query_as_list = terms + entities
        self.spell = SpellChecker()
        self.spell._distance = 2
        corrected_words = []
        for word in query_as_list:
            in_dictionary = word.upper() in self._indexer.inverted_idx or word.lower() in self._indexer.inverted_idx
            if not in_dictionary and not word.isupper():
                corrected_words.append(self.spell.correction(word))
            else:
                corrected_words.append(word)
        searcher = Searcher(self._parser, self._indexer, model=self._model)
        return searcher.search(corrected_words, k)


def main():
    config = ConfigClass()
    search_engine = SearchEngine(config)
    # r'C:\Users\noaa\pycharm projects\search_engine_partC\Search_Engine_1\data\benchmark_data_train.snappy.parquet'#
    search_engine.build_index_from_parquet(r'C:\Users\Ophir Porat\PycharmProjects\search_engine_1\Search_Engine_1\data\benchmark_data_train.snappy.parquet')
    # search_engine.build_index_from_parquet(r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\\Search_Engine_1\\data\covid19_08-04.snappy.parquet')
    # search_engine.build_index_from_parquet(r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\\Search_Engine_1\\data\covid19_07-19.snappy.parquet')



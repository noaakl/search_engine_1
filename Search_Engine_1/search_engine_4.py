import pandas as pd

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
        with open("inverted_index.json", 'w') as json_file:
            json.dump(self._indexer.inverted_idx, json_file)

        # save posting dict
        with open("posting_file.json", 'w') as json_file:
            json.dump(self._indexer.postingDict, json_file)

        # global_method.create_association_matrix(self._indexer.inverted_idx,
        #                                         self._indexer.get_posting_dict())

        print('Finished parsing and indexing.')

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implmentation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        self._indexer.load_index(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implmentation as you see fit.
    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and
        assign to self._model, which is passed on to the searcher at query time.
        """
        pass

    def search(self, query, k=None):
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

        query_as_tuple = self._parser.parse_sentence(query)
        query_as_list = query_as_tuple[0] + query_as_tuple[1]
        searcher = Searcher(self._parser, self._indexer, model=self._model)
        extended_query = self.expand_query(query_as_list)
        return searcher.search_with_extension(query_as_list, extended_query, k)
        # return searcher.search(query_as_list, k)

    def expand_query(self, query):
        #TODO:corrolated words
        query_expanded = []
        with open("correlated_words.json", "r") as f:
            correlated_words = json.load(f)
        for word in query:
            if word in correlated_words:
                query_expanded.append(correlated_words[word][1])
                # print(word, correlated_words[word][1])
            # query_expanded.append(word)
        return query_expanded


def main():
    config = ConfigClass()
    search_engine = SearchEngine(config)
    # r'C:\Users\noaa\pycharm projects\search_engine_partC\Search_Engine_1\data\benchmark_data_train.snappy.parquet'#
    search_engine.build_index_from_parquet(
        r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\Search_Engine_1\data\benchmark_data_train.snappy.parquet')
    search_engine.build_index_from_parquet(
        r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\\Search_Engine_1\data\covid19_08-04.snappy.parquet')
    search_engine.build_index_from_parquet(
        r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\\Search_Engine_1\data\covid19_07-08.snappy.parquet')
    search_engine.build_index_from_parquet(
        r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\Search_Engine_1\data\covid19_07-25.snappy.parquet')
    search_engine.build_index_from_parquet(
        r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\Search_Engine_1\data\covid19_08-06.snappy.parquet')
    search_engine.build_index_from_parquet(
        r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\Search_Engine_1\data\covid19_08-03.snappy.parquet')
    # search_engine.build_index_from_parquet(
        # r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\Search_Engine_1\data\covid19_07-13.snappy.parquet')
    global_method.create_association_matrix(search_engine._indexer.inverted_idx,
                                            search_engine._indexer.get_posting_dict())
    #
    # search_engine.build_index_from_parquet(r'C:\\Users\\Ophir Porat\\PycharmProjects\\search_engine_1\\data\covid19_07-19.snappy.parquet')
    # results =search_engine.search("covid is fun 2020 US new  wear", 40)
    # for res in results[1]:
    #     print(res)

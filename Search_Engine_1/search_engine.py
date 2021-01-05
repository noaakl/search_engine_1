import pandas as pd
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils
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
        # documents_list = self._reader.get_next_file()  # TODO: from old maybe delete
        # Iterate over every document in the file
        number_of_documents = 0
        # while (documents_list != None):  # TODO: from old maybe delete
        for idx, document in enumerate(documents_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document)
            if not parsed_document:  # TODO: from old check if necessary
                continue
            number_of_documents += 1
            # index the document data
            self._indexer.add_new_doc(parsed_document)
        # documents_list = self._reader.get_next_file()  # TODO: from old maybe delete

        self._indexer.check_pending_list()
        self._indexer.calculate_and_add_idf()

        # save inverted index
        with open("inverted_index.json", 'w') as json_file:
            json.dump(self._indexer.inverted_idx, json_file)

        # save posting dict
        with open("posting_file.json", 'w') as json_file:
            json.dump(self._indexer.postingDict, json_file)

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
    def load_precomputed_model(self):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and
        assign to self._model, which is passed on to the searcher at query time.
        """
        pass

    def search(self, query):
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
        searcher = Searcher(self._parser, self._indexer, model=self._model)
        return searcher.search(query)


# def main():
if __name__ == '__main__':
    # reader = ReadFile()
    search_engine = SearchEngine()
    search_engine.build_index_from_parquet("benchmark_data_train.snappy.parquet")
    # text = TextProcessing()
    # print(text.process_text(['New', 'Harvard', 'study', 'of', '32k', 'COVID19', 'cases', 'in', 'Wuhan', '87', 'of', 'infections', 'were', 'unascertainedpotentially', 'incl', 'asymptomatic', 'amp', 'mild symptomatic', 'R0', 'reproduction', 'number', '3.54', 'in', 'early', 'outbreak', 'close', 'to', 'my', 'first', '3.8', '', 'This', 'much', 'worse', 'than', 'old', 'SARS', 'amp', 'MERS']))


 # TODO: heyyyyy ophirrrrrrrushhhhh
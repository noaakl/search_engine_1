from ranker import Ranker


# DO NOT MODIFY CLASS NAME
class Searcher:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implmentation as you see fit. The model 
    # parameter allows you to pass in a precomputed model that is already in 
    # memory for the searcher to use such as LSI, LDA, Word2vec models. 
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, model=None):
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker()
        self._model = model

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implmentation as you see fit.
    def search(self, query, k=None):
        """ 
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """
        query_as_dict = self.get_query_by_inverted_index(query)
        relevant_docs = self._relevant_docs_from_posting(query_as_dict.keys())
        ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs, query_as_dict, k)
        n_relevant = len(ranked_doc_ids)
        return n_relevant, ranked_doc_ids

    def search_with_extension(self, query, extension, k=None):
        query_as_dict = self.get_query_by_inverted_index(query)
        query_as_dict = self.get_extended_and_query_by_inverted_index(extension, query_as_dict)
        relevant_docs = self._relevant_docs_from_posting(query_as_dict.keys())
        n_relevant = len(relevant_docs)
        ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs, query_as_dict, k)
        return n_relevant, ranked_doc_ids

    # feel free to change the signature and/or implmentation of this function 
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """
        index = self._indexer.get_index()
        relevant_docs = {}
        for term in query_as_list:
            posting_list = self._indexer.get_term_posting_list(term.lower())

            for doc_id, information in posting_list.items():  # information :[tf, df]
                doc_info = self._indexer.get_doc_information(doc_id)
                sigma_Wij_for_doc = doc_info[0]
                doc_date = doc_info[1]
                doc_len = doc_info[2]
                tf = information[0]
                idf = index[term][1]
                if doc_id not in relevant_docs.keys():
                    # id: [Wiq of document[0], {term: tf, idf}, date, doc_len]
                    relevant_docs[doc_id] = [sigma_Wij_for_doc, {term.lower(): (tf, idf)}, doc_date, doc_len]
                else:
                    relevant_docs[doc_id][1][term.lower()] = (tf, idf)
                # df = relevant_docs.get(doc_id, 0)
                # relevant_docs[doc_id] = df + 1
        return relevant_docs

    def get_query_by_inverted_index(self, query_as_list):
        query_as_dict = {}
        index = self._indexer.get_index()
        for word in query_as_list:
            if word.lower() in index:
                if word.lower() in query_as_dict:
                    query_as_dict[word.lower()] += 1
                else:
                    query_as_dict[word.lower()] = 1
            elif word.upper() in index:
                if word.lower() in query_as_dict:
                    query_as_dict[word.lower()] += 1
                else:
                    query_as_dict[word.upper()] = 1
        return query_as_dict

    def get_extended_and_query_by_inverted_index(self, query_as_list, query_as_dict):
        index = self._indexer.get_index()
        for word in query_as_list:
            if word not in query_as_dict:
                if word.lower() in index:
                    if word.lower() in query_as_dict:
                        query_as_dict[word.lower()] += 0.5
                    else:
                        query_as_dict[word.lower()] = 0.5
                elif word.upper() in index:
                    if word.lower() in query_as_dict:
                        query_as_dict[word.lower()] += 0.5
                    else:
                        query_as_dict[word.upper()] = 0.5
        return query_as_dict

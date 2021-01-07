# you can change whatever you want in this module, just make sure it doesn't 
# break the searcher module
import heapq
import math


class Ranker:
    def __init__(self):
        pass

    @staticmethod
    def rank_relevant_docs(relevant_docs, query_dict, k=None):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param k:
        :param query_dict:
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        ranked_docs = []
        query_wiq = 0
        for n in query_dict.values():
            query_wiq += math.pow(n, 2)
        for doc_id in relevant_docs.keys():
            # if doc_id =='1280935601450213377':
            #     print("")
            if len(query_dict) > 3 and len(relevant_docs[doc_id][1]) < 2:
                continue
            upper_part = 0
            document_wij = relevant_docs[doc_id][0]
            for term in relevant_docs[doc_id][1]:
                tf_idf = relevant_docs[doc_id][1][term][0] * relevant_docs[doc_id][1][term][1]
                upper_part += tf_idf * query_dict[term]

            score = Ranker.cos_similarity(upper_part, query_wiq, document_wij)
            heapq.heappush(ranked_docs, [-1 * score, doc_id])

        return Ranker.retrieve_top_k(ranked_docs,k)
        # ranked_results = sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True)
        # if k is not None:
        #     ranked_results = ranked_results[:k]
        # return [d[0] for d in ranked_results]
    @staticmethod
    def retrieve_top_k(sorted_relevant_doc, k):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        if not k: k = len(sorted_relevant_doc)
        n_largest =[]
        for i in range(k):
            try:
                curr_doc=heapq.heappop(sorted_relevant_doc)
                curr_doc[0]=curr_doc[0]*-1
                n_largest.append(curr_doc[1])
            except:
                break
        return n_largest

    @staticmethod
    def cos_similarity(upper_part, query_wiq, document_wiq):
        return upper_part / math.sqrt(query_wiq * document_wiq)


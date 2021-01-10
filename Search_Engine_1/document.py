class Document:

    avg_doc_len = [0, 0]

    def __init__(self, tweet_id, tweet_date=None, full_text=None, url=None, retweet_text=None, retweet_url=None,
                 quote_text=None, quote_url=None, term_doc_dictionary=None, doc_length=0, entity_dict=None, max_f=0):
        """
        :param tweet_id: tweet id
        :param tweet_date: tweet date
        :param full_text: full text as string from tweet
        :param url: url
        :param retweet_text: retweet text
        :param retweet_url: retweet url
        :param quote_text: quote text
        :param quote_url: quote url
        :param term_doc_dictionary: dictionary of term and documents.
        :param doc_length: doc length
        :param entity_dict: dictionary of entities and documents
        :param max_f: the largest frequency of a word
        """
        self.tweet_id = tweet_id
        self.tweet_date = tweet_date
        self.full_text = full_text
        self.url = url
        self.retweet_text = retweet_text
        self.retweet_url = retweet_url
        self.quote_text = quote_text
        self.quote_url = quote_url
        self.term_doc_dictionary = term_doc_dictionary
        self.entity_dict = entity_dict
        self.doc_length = doc_length
        self.max_f = max_f

    # the info needed for every doc in doc file
    def get_doc_info(self):
        return [0, self.tweet_date, self.doc_length]

    # all the words in the doc
    def get_num_of_uniq_words(self):
        return len(self.term_doc_dictionary) + len(self.entity_dict)

    @classmethod
    def get_avg_doc_len(cls):
        return Document.avg_doc_len[0] / Document.avg_doc_len[1]


import re
import string
from nltk.corpus import stopwords

import configuration
from document import Document
import stemmer
from text_processing import TextProcessing


class Parse:

    def __init__(self):
        self.stemmer = stemmer.Stemmer()
        self.text_processing = TextProcessing()
        # self.config = config
        # ************************
        self.punctuation = {}
        for item in string.punctuation + '’' + ' ' + "\n":
            self.punctuation[item] = 0
        self.punctuation.pop('#')
        self.punctuation.pop('@')
        self.punctuation.pop('%')
        self.stop_words = stopwords.words('english')
        # self.stop_words.extend(
            # ['_','``', "''", "'", " ", ":", "?", '.', 'https', '!', ',', '"', '^', '*', '&', ';', '~', 'etc', '-', '+', "=","/",")","("])

    def parse_sentence(self, text):
        """
        This function tokenize the text and split it to terms (lower case) and entities (upper case)
        :param text: string of the full text of a document
        :return: processed_text: list of terms, entities: list of entities
        """
        # print(text)
        text_tokens = self.tokenize_text(text)
        # print("after tokenize: " ,text_tokens)
        if not text_tokens: return [], []
        processed_text, entities = self.text_processing.process_text(text_tokens)
        return processed_text, entities

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields, parses the text,
        stems if needed, creates term dictionary and entities dictionary, calculates max f
        :param to_steam:
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        needs_to_stem = False
            #self.config.toStem

        # create doc info
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        retweet_text = doc_as_list[4]
        retweet_url = doc_as_list[5]
        quote_text = doc_as_list[6]
        quote_url = doc_as_list[7]
        term_dict = {}
        entity_dict = {}
        max_f = 0

        if tweet_id =='1284603170296143872':
            print("")
        # parse
        tokenized_text, entities = self.parse_sentence(full_text)
        if tokenized_text == [] and entities == []: return
        doc_length = len(tokenized_text) + len(entities)  # after text operations, with stopwords.

        # create term dict for the doc
        for term in tokenized_text + self.parse_url(url):
            # if not term or term.lower() in self.stop_words:
            #     continue
            # if term.isalpha() and len(term) < 2:
            #     continue
            if needs_to_stem: term = self.stemmer.stem_term(term)
            if term.lower() not in term_dict:
                term_dict[term.lower()] = 1
            else:
                term_dict[term.lower()] += 1

            # update max_f
            if term_dict[term.lower()] > max_f:
                max_f = term_dict[term.lower()]

        # create entity dict for the doc
        for entity in entities:

            # elif entity.isalpha() and len(entity) < 2:
            #     continue
            if needs_to_stem: entity = self.stemmer.stem_term(entity)

            # if the entity is term- add to term dict
            if entity.lower() in term_dict:
                term_dict[entity.lower()] += 1
                # update max_f
                if term_dict[entity.lower()] > max_f:
                    max_f = term_dict[entity.lower()]
                continue

            # if the entity is entity- add to entity dict
            # if entity.lower() in self.stop_words:
            #     continue
            if entity.upper() not in entity_dict:
                entity_dict[entity.upper()] = 1
            else:
                entity_dict[entity.upper()] += 1
            # update max_f
            if entity_dict[entity.upper()] > max_f:
                max_f = entity_dict[entity.upper()]

        # create doc
        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length, entity_dict, max_f)
        # print("document Id : " +tweet_id)
        # print("entities : " + str(entity_dict))
        # print("terms : " + str(term_dict))
        # print("*********************************************************")

        return document

    def parse_url(self, url):
        delimiters = '[/=+:?><.-}{]'
        url = url.replace('[', '')
        url = url.replace(']', '')
        url_tokens = [w.lower() for w in re.split(delimiters, url) if w and w != '{}' and len(w) > 1]
        return url_tokens

    def tokenize_text(self, text):
        tokens = []
        # first_tokens = []
        first_tokens = text.split()
        # print(first_tokens)
        if first_tokens[0].lower() == 'rt' : first_tokens.pop(0)
        for token in first_tokens:

            if 'http' in token:
                continue
            token_checker = ''
            token = ''.join([i if ord(i) < 128 else '' for i in token])
            for char in token:

                if char in self.punctuation.keys():
                    if token.endswith(char) or token.startswith(char):
                        # tokens.append(token_checker)
                        continue


                    elif len(token_checker) > 0:
                        # if token_checker[len(token_checker) - 1] == '-':
                        #     token_checker = token_checker[0:len(token_checker) - 1]
                        #     tokens.append(token_checker)
                        #     token_checker = ''
                        #     tokens.append('-')
                        #     tokens.append(char)
                        #     continue
                        if char == ',' and token_checker[len(token_checker)-1].isdigit() :
                            continue
                        if char == '-':
                            if token_checker[len(token_checker) - 1] != '-':
                                tokens.append(token_checker)
                                token_checker = ''
                                continue
                        elif char =="." and token_checker[len(token_checker)-1].isdigit():
                            token_checker += char
                            continue
                        elif char in "\/" :
                            if not token_checker.isdigit():
                                token_checker += ' '
                                continue
                        elif char == "'" or char == '’':
                            break
                        elif char == '_' :
                            if token.startswith('@') or token.startswith('#'):
                               token_checker += char
                               continue
                        # token_checker += char
                        tokens.append(token_checker)
                        token_checker = ''
                    # tokens.append(char)

                else:
                    token_checker += char

            if len(token_checker) > 1:
                tokens.append(token_checker)
        # tokens = [ for t in tokens]
        return tokens

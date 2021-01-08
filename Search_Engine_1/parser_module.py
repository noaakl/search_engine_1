import re
import string
from nltk.corpus import stopwords
import configuration
from document import Document
import stemmer
from text_processing import TextProcessing
from _datetime import datetime

shortcuts = {"aint": 'is not', "arent": 'are not', "cant": 'cannot', "cantve": 'cannot have', 'cause': 'because',
             "couldve": 'could have', "couldnt": 'could not',
             "couldntve": 'could not have', "didnt": 'did not', "doesnt": 'does not', "dont": 'do not',
             "hadnt": 'had not', "hadntve": 'had not have', "hasnt": 'has not',
             "havent": 'have not', "hed": 'he had', "hes": 'he is', "howll": 'how will', "hows": 'how is',
             "Id": 'I would', "Ill": 'I will', "Im": 'I am', "Ive": 'I have', "isnt": 'is not',
             "itd": 'it had', "itll": 'it will', "its": 'it is', "lets": 'let us', "maam": 'madam', "maynt": 'may not',
             "mightve": 'might have', "mightnt": 'might not', "mustve": 'must have',
             "mustnt": 'must not', "mustntve": 'must not have', "neednt": 'need not', "needntve": 'need not have',
             "oclock": 'of the clock', "shant": 'shall not', "shed": 'she had',
             "shes": 'she is', "shouldve": 'should have', "shouldnt": 'should not', "sove": 'so have',
             "thatd": 'that would', "thats": 'that is', "thered": 'there would',
             "theres": 'there is', "theyd": 'they would', "theyll": 'they will', "theyre": 'they are',
             "theyve": 'they have', "wasnt": 'was not', "well": 'we will',
             "we've": 'we have', "weren't": 'were not', "whatll": 'what will', "whatre": 'what are', "whats": 'what is',
             "whatve": 'what have',
             "whens": 'when is', "wheres": 'where is', "who'll": 'who will', "whos": 'who is', "willve": 'will have',
             "wont": 'will not',
             "wouldve": 'would have', "wouldnt": 'would not', "yall": 'you all',
             "youd": 'you would', "youll": 'you all', "youre": 'you are', "youve": 'you have'}

corona = {"covid": "covid", "virus": "corona", "corona": "covid", "coronavirus": "covid", "covid19": "covid",
          "covid 19": "covid", "cov": "covid"}

trump = {"trump": "donald trump", "donald trump": "donald trump", "president": "donald trump"}


def parse_url(url):
    delimiters = '[/=+:?><.-}{]'
    url = url.replace('[', '')
    url = url.replace(']', '')
    url_tokens = [w.lower() for w in re.split(delimiters, url) if w and w != '{}' and len(w) > 1]
    return url_tokens


class Parse:

    def __init__(self, spell_check=False):
        self.stemmer = stemmer.Stemmer()
        self.text_processing = TextProcessing(spell_check)
        # self.config = config
        # ************************
        self.punctuation = {}
        for item in string.punctuation + '’' + ' ' + "\n":
            self.punctuation[item] = 0
        self.punctuation.pop('#')
        self.punctuation.pop('@')
        self.punctuation.pop('%')
        self.stop_words = stopwords.words('english')
        # self.stop_words.extend( ['_','``', "''", "'", " ", ":", "?", '.', 'https', '!', ',', '"', '^', '*', '&',
        # ';', '~', 'etc', '-', '+', "=","/",")","("])

    def parse_sentence(self, text):
        """
        This function tokenize the text and split it to terms (lower case) and entities (upper case)
        :param text: string of the full text of a document
        :return: processed_text: list of terms, entities: list of entities
        """
        print(text)
        text_tokens = self.tokenize_text(text)
        print("after tokenize: ", text_tokens)
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
        # self.config.toStem

        # create doc info
        tweet_id = doc_as_list[0]
        date_distance = datetime.strptime("Sun Jan 10 05:03:50 +0000 2021", "%a %b %d %H:%M:%S %z %Y") - datetime.strptime(doc_as_list[1], "%a %b %d %H:%M:%S %z %Y")
        formatted_date_distance = str(date_distance).split(',')[1].replace(':', '')
        tweet_date = -int(formatted_date_distance)/999999
        # print(tweet_date)
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        retweet_text = doc_as_list[4]
        retweet_url = doc_as_list[5]
        quote_text = doc_as_list[6]
        quote_url = doc_as_list[7]
        term_dict = {}
        entity_dict = {}
        max_f = 0

        # parse
        tokenized_text, entities = self.parse_sentence(full_text)
        if tokenized_text == [] and entities == []: return
        doc_length = len(tokenized_text) + len(entities)  # after text operations, with stopwords.

        # create term dict for the doc
        for term in tokenized_text + parse_url(url):
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
            if needs_to_stem: entity = self.stemmer.stem_term(entity)

            # if the entity is term- add to term dict
            if entity.lower() in term_dict:
                term_dict[entity.lower()] += 1
                # update max_f
                if term_dict[entity.lower()] > max_f:
                    max_f = term_dict[entity.lower()]
                continue

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
        print("document Id : " + tweet_id)
        print("entities : " + str(entity_dict))
        print("terms : " + str(term_dict))
        print("*********************************************************")

        return document

    def tokenize_text(self, text):
        tokens = []
        # first_tokens = []
        first_tokens = text.split()
        # print(first_tokens)
        if first_tokens[0].lower() == 'rt': first_tokens.pop(0)
        for token in first_tokens:
            flag = 0
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
                        if char == ',' and token_checker[len(token_checker) - 1].isdigit():
                            continue
                        if char == '-':
                            if token_checker[len(token_checker) - 1] != '-':
                                # if  token_checker[0].isupper() or token[len(token_checker) - 1].isdigit():
                                token_checker += ' '
                                continue
                                # else:
                                #     tokens.append(token_checker)
                                #     token_checker = ''
                                #     continue

                        elif char == "." and token_checker[len(token_checker) - 1].isdigit():
                            token_checker += char
                            continue
                        elif char in "\/":
                            if not token_checker.isdigit():
                                token_checker += ' '
                                continue
                        elif char == "'" or char == '’':
                            break
                        elif char == '_':
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
                if token_checker.lower() in shortcuts:
                    tokens += shortcuts[token_checker.lower()].split()
                elif token_checker.lower() in corona:
                    tokens.append(corona[token_checker.lower()])
                # elif token_checker.lower() in corona:
                #     tokens += corona
                elif token_checker.lower() in trump:
                    tokens += trump[token_checker.lower()]
                else:
                    tokens.append(token_checker)

        return tokens

parser = Parse()
print(parser.parse_sentence("hey Covid covid19 covid-19 coronavirus Coronavirus US Us "))

from numbers_processor import NumbersProcessor
from entity import Entity
from nltk.corpus import stopwords
from spellchecker import SpellChecker


class TextProcessing:
    names_and_entities_dict = {}  # name : (how many docs, how many times in corpus, )

    def __init__(self):
        self.stop_words = {}
        my_stopwords = stopwords.words('english')
        my_stopwords.extend(
            ['^', '*', '&', ';', '~', 'etc', "=", "/", ")", "(", '_', '``', "''", "'", " ", ":", "?", '.', 'https', '!',
             ',', '"', '-', '+', 'web', 'status'])
        # more stop word - probably not nesecery
        for w in my_stopwords:
            self.stop_words[w] = 0
        self.numbers = NumbersProcessor()
        self.entity = Entity()


    def process_text(self, text_tokens):
        """
        :param text_tokens: list of strings
        :return: new list of strings according to the ruls
        """
        final_tokens = []
        final_entities = []
        text_tokens_len = len(text_tokens)
        skip_one = False

        for i in range(text_tokens_len):
            token = text_tokens[i]

            # token =self.spell_checker.correction(token)
            # check if needs to skip one token
            if skip_one:
                skip_one = False
                continue

            # stopWord
            elif token.lower() in self.stop_words:
                continue

            # names and entities
            if token[0].isupper():
                final_entities += self.entity.add_to_my_entities(token, i)

            elif token == 'united':
                if i + 1 < text_tokens_len:
                    if text_tokens[i+1] =='states':
                        final_tokens.append("united states")
                        skip_one = True

            # hashtag
            elif token.startswith("#"):
                tokens, entities = self.split_hashtag(text_tokens[i])
                final_tokens += tokens
                final_entities += entities
                skip_one = False

            # numbers
            elif self.numbers.is_number(token):
                if i + 1 < text_tokens_len:
                    processed_token, skip_one = self.numbers.process_numbers(token, text_tokens[i + 1])
                else:
                    processed_token, skip_one = self.numbers.process_numbers(token)
                final_tokens += processed_token

            # word
            else:
                final_tokens.append(token)
                skip_one = False

        self.entity.clear_entities()
        final_entities = [entity for entity in final_entities if len(entity.split()) < 4]
        return final_tokens, final_entities

    def split_hashtag(self, hashtag):
        """
        :param hashtag: stirng starts with #
        :return: list of separated words
        """
        splited_terms = []
        splited_entities = []
        curr_word = ""
        splited_terms.append(hashtag)
        hashtag = hashtag.replace('#', '')
        for i in range(len(hashtag)):
            curr_letter = hashtag[i]
            # number
            if curr_letter.isdigit():
                if not curr_word:
                    curr_word = curr_letter
                elif curr_word and curr_word.isdigit():
                    curr_word += curr_letter
                elif curr_word and curr_word.isupper():
                    splited_entities.append(curr_word)
                    curr_word = curr_letter
                else:
                    splited_terms.append(curr_word.lower())
                    curr_word = curr_letter
            # _
            elif curr_letter == "_":
                if curr_word:
                    if curr_word.isupper():
                        splited_entities.append(curr_word)
                    else:
                        splited_terms.append(curr_word.lower())
                curr_word = ""
                continue
            # upper
            elif curr_letter.isupper():
                if not curr_word:
                    curr_word = curr_letter
                elif curr_word and curr_word.isupper():
                    curr_word += curr_letter
                else:  # curr word not upper - add curr word and stard new one
                    splited_terms.append(curr_word.lower())
                    curr_word = ""
                    curr_word += curr_letter
            # lower
            elif curr_letter.islower():
                if curr_word.isdigit():
                    splited_terms.append(curr_word)
                    curr_word = ""
                elif len(curr_word) > 1 and curr_word.isupper():
                    splited_entities.append(curr_word)
                    curr_word = ""
                curr_word += curr_letter
            # last letter
            if i == len(hashtag) - 1:
                if curr_word:
                    if curr_word.isupper():
                        splited_entities.append(curr_word)
                    else:
                        splited_terms.append(curr_word.lower())

        return splited_terms, splited_entities

    def upper_lower_case(self, token):
        if token[0].isupper():
            return token.upperCase()
        return token

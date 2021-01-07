from decimal import Decimal
import re


class NumbersProcessor:
    number_dict = {"hundred": 100, "hundreds": 100, "thousand": 1000, "thousands": 1000, "million": 1000000,
                   "millions": 1000000, "billion": 1000000000, "billions": 1000000000, 'K': 1000, 'M': 1000000,
                   'B': 1000000000}
    number_form_dict = {1000: 'K', 1000000: 'M', 1000000000: 'B'}
    percent_dict = {"percent": "%", "percentage": "%", "percentages": "%"}
    price_dict = {"dollar": "$", "dollars": "$", "bucks": "$", "buck": "$", "$": "$"}

    def __init__(self):
        self

    def process_numbers(self, token1, token2=None):
        """
        :param token1: string
        :param token2: string
        :return: new list of strings according to the ruls
        """
        final_tokens = []
        skip_one = False
        # percent
        percent_token, token_is_percent = self.percent(token1, token2)
        if token2 is not None and token_is_percent:
            final_tokens.append(percent_token)
            skip_one = True
            return final_tokens, skip_one
        # just numbers
        just_number_token, skip_one = self.just_numbers(token1, token2)
        if just_number_token != token1:
            final_tokens.append(just_number_token)
            # skip_one = True
            return final_tokens, skip_one
        # dollar
        elif token2 is not None and token2.lower() in self.price_dict.keys():
            final_tokens.append(token1 + self.price_dict[token2.lower()])
            skip_one = True
            return final_tokens, skip_one
        # word
        else:
            if token1 is not None:
                final_tokens.append(token1)
                return final_tokens, skip_one

    def percent(self, token1, token2=None):
        """
        :param token2: string
        :param token1: string
        :return: string
        """
        # %
        if token2 == "%":
            return token1 + token2, True
        # percent
        elif token2 is not None and token2.lower() in self.percent_dict:
            return token1 + self.percent_dict[token2.lower()], True
        # not relevant
        else:
            return token1, False

    def just_numbers(self, num, token2=None):
        """
        :param token2: next token
        :param num: string
        :return:
        """
        # num_list = num.split('.')
        # if len(num_list)>2:
            # friction or something else
            # return num,False
        if num.__contains__('/'):
            return num , False
        else:
            # remove_comma = num.replace(',', '')
            multiply = 1
            if token2 is not None:
                # if self.is_fraction(token2[0]):
                #     return remove_comma + " " + token2, True
                if token2.lower() in self.number_dict:
                    multiply=self.number_dict[token2.lower()]
            new_number = float(float(num) * multiply)
            if new_number < 1000:
                return num, False

            divide = 1000000000.0
            while new_number < divide:
                # print(num,new_number,token2 , divide)
                divide = divide / 1000.0
            formed_number = num
            if divide != 1:
                formed_number= float(float(new_number) / divide)
                list_to_format = str(formed_number).split('.')
                if int(list_to_format[1]) >0 :
                    list_to_format[1] = list_to_format[1][0:3]
                    formed_number =list_to_format[0] + '.' +list_to_format[1]
                else:
                    formed_number  =list_to_format[0]
                formed_number = str(formed_number) + self.number_form_dict[divide]
            return formed_number, multiply != 1

    def is_float(self, num):  # float, date, number with comma, num
        try:
            float(num)
            return True
        except ValueError:
            return False

    def is_fraction(self, token):
        """
        :param token:
        :return:
        """
        if not token.__contains__('/'):
            return False
        split_by_slash = token.split('/')
        remove_slash = split_by_slash[0].replace('/', '')
        return self.is_float(remove_slash)

    def is_num_with_comma(self, num):
        remove_comma = num.replace(',', '')
        return self.is_float(remove_comma)

    def is_num_without_letters(self, num):
        return not re.search('[a-zA-Z]', num)

    def is_int(self, num):
        try:
            int(num)
            return True
        except ValueError:
            return False

    def is_number(self, num):
        boolean =  (self.is_float(num) or self.is_fraction(num) or self.is_int(num)) and self.is_num_without_letters(num)
        return boolean

# num_processor =NumbersProcessor()
# print(num_processor.just_numbers("42300" , "hundred"))
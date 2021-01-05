
class Entity:

    def __init__(self):
        self.last_token = -2
        self.current_entity = ''

    # adds a new entity to the my_entities list
    def add_to_my_entities(self, token, index):
        """
        :param token: entity to parse
        :param index: the index which token in full text document
        """
        # if token[0] == '@':
        #     token = token.replace('@', '')

        # cases of / between two entities
        # if token.__contains__("/"):
        #     for w in token.split("/"):
        #         if w:
        #             self.my_entities.append(w.upper())
        #             self.current_entity = w
        #             self.num_of_words = 0
        #     return
        #
        # if token.__contains__('-'):
        #     for w in token.split("-"):
        #         if w:
        #             self.my_entities.append(w.upper())
        #             self.current_entity = w
        #             self.num_of_words = 0
        #     self.my_entities.append(token.replace('-', ' '))
        #     return
        entities_to_return = []
        # case of entity compound of more then one word
        if self.last_token == index - 1:
            self.current_entity += ' ' + token.upper()
            self.last_token = index
            entities_to_return.append(self.current_entity)

        else:
            # create new entity
            self.current_entity = token
            self.last_token = index
        entities_to_return.append(token.upper())
        return entities_to_return
        # if len(token) > 1: self.my_entities.append(token)
    def clear_entities(self):
        self.current_entity = ''
        self.last_token = -2


    # def get_entities(self):
    #     # return all document entities and change all fields
    #     if self.current_entity and self.num_of_words > 1:
    #         self.my_entities.append(self.current_entity)
    #     self.current_entity = ''
    #     self.num_of_words = 0
    #     self.last_token = -2
    #     temp_list = self.my_entities
    #     self.my_entities = []
    #     return temp_list
    #
    # def get_last_entity(self):
    #     return self.current_entity


us_state_abbrev = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado',
    'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana',
    'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Los Angles', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
    'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota',
    'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
    'US': 'United States', 'AMERICA': 'UNITED STATES', 'USA': "United States", "THE STATES": "United States"
}


class Entity:

    def __init__(self):
        self.last_token = -2
        self.current_entity = ''
        self.num_of_words = 0

    # adds a new entity to the my_entities list
    def add_to_my_entities(self, token, index):
        """
        :param token: entity to parse
        :param index: the index which token in full text document
        """
        entities_to_return = []

        # case of entity compound of more then one word
        if self.last_token == index - 1:
            # and self.num_of_words < 3
            self.current_entity += ' ' + token.upper()
            self.last_token = index
            self.num_of_words += 1
            entities_to_return.append(self.current_entity)
        else:
            # create new entity
            self.num_of_words = 1
            self.current_entity = token.upper()
            self.last_token = index

        if token.upper() in us_state_abbrev:
            token = us_state_abbrev[token.upper()].upper()
            self.current_entity = token
            self.last_token = -2
            # entities_to_return += token
        entities_to_return.append(token.upper())

        return entities_to_return
        # if len(token) > 1: self.my_entities.append(token)

    def clear_entities(self):
        self.current_entity = ''
        self.last_token = -2

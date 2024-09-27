import re
import collections
from services.normalize import *
from services.infer import *

# TODO: reconfigure patterns to be an array or just a re object instead of a dict
# TODO: likely move the re.compile out of the normalize patterns method and into the patterns array
# TODO: investigate dataclasses - https://docs.python.org/3/library/dataclasses.html

class Parser:
    parser_type = ''
    pattern = r''
    match_keys = []
    match_dict = {}
    matches = []
    def __init__(self):
        self.pattern = self.normalize_pattern()
        self.match_dict = dict.fromkeys(self.match_keys)

    def get_parser_type(self):
        return self.parser_type

    def get_pattern(self):
        return self.pattern

    def get_match_keys(self):
        return self.match_keys

    def get_match_dict(self):
        return self.match_dict
    
    def get_readable(self, match):
        return ''

    def generate_match(self, match_fields):
        for k, v in match_fields.items():
            if k not in self.match_dict:
                raise ValueError(k + ' is not a valid match key for the ' + self.parser_type + ' parser')
        match_dict = dict(self.match_dict)
        match_dict.update(match_fields)
        return match_dict

    def normalize_pattern(self):
        return re.compile(self.pattern, flags = re.I)

    def normalize_match(self, match):
        return match

    def parse(self, sig):
        matches = []
        for match in re.finditer(self.pattern, sig):
            normalized_match = self.normalize_match(match)
            if normalized_match:
                matches.append(normalized_match)
        self.matches = matches
        return matches
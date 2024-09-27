from classes.parser import *

class MethodParser(Parser):
    parser_type = 'method'
    match_keys = ['method', 'method_text_start', 'method_text_end', 'method_text', 'method_readable']
    def normalize_pattern(self):
        method_patterns = []
        for n, p in METHODS.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the method_patterns array
            method_patterns.append(r'|'.join(p))
        pattern = re.compile(r'(?<!do not crush or )(?P<method>' + r'|'.join(method_patterns) + r')', flags = re.I)
        return pattern
    def normalize_match(self, match):
        method = get_normalized(METHODS, match.group('method'))
        method_text_start, method_text_end = match.span()
        method_text = match[0]
        method_readable = self.get_readable(method)
        return self.generate_match({'method': method, 'method_text_start': method_text_start, 'method_text_end': method_text_end, 'method_text': method_text, 'method_readable': method_readable})
    def get_readable(self, method):
        readable = method
        return readable

parsers = [
    MethodParser()
]

#print(MethodParser().parse('take ond tab daily'))
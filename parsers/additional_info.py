from classes.parser import *

class AdditionalInfoParser(Parser):
    parser_type = 'additional_info'
    match_keys = ['additional_info', 'additional_info_text_start', 'additional_info_text_end', 'additional_info_text', 'additional_info_readable']
    def normalize_pattern(self):
        additional_info_patterns = []
        for n, p in ADDITIONAL_INFO.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the route_patterns array
            additional_info_patterns.append(r'|'.join(p))
        pattern = re.compile(r'(?P<additional_info>' + r'|'.join(additional_info_patterns) + r')', flags = re.I)
        return pattern
    def normalize_match(self, match):
        additional_info = get_normalized(ADDITIONAL_INFO, match.group('additional_info'))
        additional_info_text_start, additional_info_text_end = match.span()
        additional_info_text = match[0]
        additional_info_readable = self.get_readable(additional_info=additional_info)
        return self.generate_match({'additional_info': additional_info, 'additional_info_text_start': additional_info_text_start, 'additional_info_text_end': additional_info_text_end, 'additional_info_text': additional_info_text, 'additional_info_readable': additional_info_readable})
    def get_readable(self, additional_info=None):
        readable = additional_info if additional_info else ''
        return readable
    def normalize_multiple_matches(self, matches=[], sig=None):
        # get the min/max start/end locations from list of matches
        additional_info_text_start = min(matches, key=lambda x:x['additional_info_text_start'])['additional_info_text_start']
        additional_info_text_end = max(matches, key=lambda x:x['additional_info_text_end'])['additional_info_text_end']
        # get substring of sig text based on these min/max locations
        additional_info_text = sig[additional_info_text_start:additional_info_text_end]
        # get list of route text from list of matches
        additional_info_list = [m['additional_info'] for m in matches]
        additional_info = ''
        additional_info_readable = ''
        if additional_info_list:
            # remove duplicates
            additional_info_list = list(dict.fromkeys(additional_info_list))
            # separate list into 'take-containing' info and 'non-take-containing' info
            # remove 'take ' from all (see below)
            additional_info_take = [a.replace('take ', '') for a in additional_info_list if 'take ' in a.lower()]
            additional_info_no_take = [a for a in additional_info_list if 'take ' not in a.lower()]
            # store additional_info as just a ' / ' joined version of the original list
            additional_info = ' / '.join(additional_info_list)
            # additional_info_readable should be the 'take-containing' info, with the 'takes' removed, ' ' joined,
            additional_info_readable += ' '.join(additional_info_take)
            #       followed by a ' - ' and any 'non-take-containing' info, ' / ' joined
            if additional_info_no_take:
                additional_info_readable += ' - '
                additional_info_readable += ' / '.join(additional_info_no_take)
            #       EXAMPLE: as directed with food one hour prior to sexual activity - do not crush or chew / for suspected overdose call 911
            # remove white space
            additional_info_readable = additional_info_readable.strip()
        return self.generate_match({'additional_info': additional_info, 'additional_info_text_start': additional_info_text_start, 'additional_info_text_end': additional_info_text_end, 'additional_info_text': additional_info_text, 'additional_info_readable': additional_info_readable})
    def parse(self, sig):
        matches = []
        for match in re.finditer(self.pattern, sig):
            normalized_match = self.normalize_match(match)
            if normalized_match:
                matches.append(normalized_match)
        # once we have matched on all the possible patterns,
        # we take the list of matches and pass it to a special normalize_multiple_matches method
        # which then overwrites the list of matches with one final match that combines all the matches
        if matches:
            normalized_match = self.normalize_multiple_matches(matches, sig)
            if normalized_match:
                matches = [(normalized_match)]
        self.matches = matches
        return matches

parsers = [
    AdditionalInfoParser(),
]
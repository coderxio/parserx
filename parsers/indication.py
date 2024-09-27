from .classes.parser import *

# as needed for heartburn | prn for heartburn | p.r.n. heartburn | prn heartburn
# asNeededBoolean = true
# TODO: replace wildcard indication search with INDICATIONS list from normalize.py
class IndicationParser(Parser):
    parser_type = 'indication'
    pattern = r'(?P<as_needed>as needed for|if needed for|as needed|to prevent|if needed|prn for|prnf|prf|prn|at (?:the )?(?:first|1st) sign of)(?:\s?(?P<indication>.{,250}))?'
    match_keys = ['as_needed', 'indication', 'indication_text_start', 'indication_text_end', 'indication_text', 'indication_readable']
    def normalize_match(self, match):
        as_needed = 1
        indication_text = match.group('indication')
        indication = (get_indication(indication_text) if indication_text != None else indication_text)
        indication_text_start, indication_text_end = match.span()
        indication_text = match.group(0)
        indication_readable = self.get_readable(as_needed=as_needed, indication=indication)
        return self.generate_match({'as_needed': as_needed, 'indication': indication, 'indication_text_start': indication_text_start, 'indication_text_end': indication_text_end, 'indication_text': indication_text, 'indication_readable': indication_readable})
    def get_readable(self, as_needed=None, indication=None):
        as_needed = 'as needed' if as_needed else ''
        if indication:
            indication = indication.split(',')
            # remove duplicate indications (i.e. pain / pain)
            indication = list(dict.fromkeys(indication))
            indication = ' / '.join(indication)
        else:
            indication = ''

        readable = as_needed + (' for ' + indication if indication != '' else '')
        readable = readable.strip()
        return readable

class ChronicIndicationParser(IndicationParser):
    pattern = r'(?!as needed |if needed |prn |prf |prnf )(?:for|indications) (?P<indication>.{,250})(?!' + RE_RANGE + r')'
    def normalize_match(self, match):
        indication_text = match.group('indication')
        indication = (get_indication(indication_text) if indication_text != None else indication_text)
        indication_text_start, indication_text_end = match.span()
        indication_text = match.group(0)
        indication_readable = self.get_readable(indication=indication)
        return self.generate_match({'indication': indication, 'indication_text_start': indication_text_start, 'indication_text_end': indication_text_end, 'indication_text': indication_text, 'indication_readable': indication_readable})

parsers = [
    IndicationParser(),
    ChronicIndicationParser()
]
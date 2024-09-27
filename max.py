from classes.parser import *

class MaxParser(Parser):
    parser_type = 'max'
    match_keys = ['max_numerator_value', 'max_numerator_unit', 'max_denominator_value', 'max_denominator_unit', 'max_text_start', 'max_text_end', 'max_text', 'max_readable']
    def normalize_pattern(self):
        dose_patterns = []
        for n, p in DOSE_UNITS.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the dose_patterns array
            dose_patterns.append(r'|'.join(p))
        strength_patterns = []
        for n, p in STRENGTH_UNITS.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the strength_patterns array
            strength_patterns.append(r'|'.join(p))        
        pattern = re.compile(r'(?:max(?: dose)?|do not take more than|no more than|nmt|do not exceed)\s?(?P<dose>' + RE_RANGE + r')\s?(?P<dose_unit>' + r'|'.join(dose_patterns) + '|' + r'|'.join(strength_patterns) + r')?\s?(?:per|\/|in(?: a)?)\s?(?P<period>' + RE_RANGE + r')?\s?(?P<period_unit>day|hours|hour|hrs|hr|\bh\b|week|month|year|d\b|w\b|mon|m\b|yr)', flags = re.I)
        return pattern
    def normalize_match(self, match):
        dose_range = split_range(match.group('dose'))
        max_numerator_value = dose_range[1] or dose_range[0]
        # need to check for normalizaion for both dose units and strength units
        # will return text of match if no normalization found
        max_numerator_unit = get_normalized(STRENGTH_UNITS, get_normalized(DOSE_UNITS, match.group('dose_unit'))) if match.group('dose_unit') else None
        max_denominator_value = None
        if match.group('period'):
            period_range = split_range(match.group('period')) 
            max_denominator_value = period_range[1] or period_range[0]
        max_denominator_unit = get_normalized(PERIOD_UNIT, match.group('period_unit')) if match.group('period_unit') else None
        # set denominator value to 1 in the example of "max 3 tablets per day" -> "max 3 tablets per 1 day"
        if max_denominator_unit and not max_denominator_value:
            max_denominator_value = 1
        max_text_start, max_text_end = match.span()
        max_text = match[0]
        max_readable = self.get_readable(
            max_numerator_value=max_numerator_value, 
            max_numerator_unit=max_numerator_unit, 
            max_denominator_value=max_denominator_value,
            max_denominator_unit=max_denominator_unit)
        return self.generate_match({'max_numerator_value': max_numerator_value, 'max_numerator_unit': max_numerator_unit, 'max_denominator_value': max_denominator_value, 'max_denominator_unit': max_denominator_unit, 'max_text_start': max_text_start, 'max_text_end': max_text_end, 'max_text': max_text, 'max_readable': max_readable})
    def get_readable(self, max_numerator_value=None, max_numerator_unit=None, max_denominator_value=None, max_denominator_unit=None):
        if 1 == 2:
            return ''
        
        readable = ' - max'
        readable += ' ' + str(max_numerator_value) if max_numerator_value else ''
        plural_dose_unit = max_numerator_value and max_numerator_value > 1
        if max_numerator_unit:
            if plural_dose_unit:
                max_numerator_unit += 'e' if max_numerator_unit[-1:] == 'h' else ''
                max_numerator_unit += 's' if max_numerator_unit not in ['oz','mL','L','cm', 'mg','mcg','g','mEq'] else ''
            readable += ' ' + max_numerator_unit

        readable += ' per' if max_denominator_value or max_denominator_unit else ''
        readable += ' ' + str(max_denominator_value) if max_denominator_value and max_denominator_value != 1 else ''
        plural_duration = max_denominator_value and max_denominator_value > 1
        if max_denominator_unit:
            max_denominator_unit += 's' if plural_duration else ''
        readable += ' ' + max_denominator_unit
        return readable


class MaxDailyParser(MaxParser):
    def normalize_pattern(self):
        dose_patterns = []
        for n, p in DOSE_UNITS.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the dose_patterns array
            dose_patterns.append(r'|'.join(p))
        strength_patterns = []
        for n, p in STRENGTH_UNITS.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the strength_patterns array
            strength_patterns.append(r'|'.join(p))        
        pattern = re.compile(r'(?:max(?:imum)? daily (?:dose|amount)|mdd)\s?(?:=|is)?\s?(?P<dose>' + RE_RANGE + r')\s?(?P<dose_unit>' + r'|'.join(dose_patterns) + '|' + r'|'.join(strength_patterns) + r')?', flags = re.I)
        return pattern
    def normalize_match(self, match):
        dose_range = split_range(match.group('dose'))
        max_numerator_value = dose_range[1] or dose_range[0]
        # need to check for normalizaion for both dose units and strength units
        # will return text of match if no normalization found
        max_numerator_unit = get_normalized(STRENGTH_UNITS, get_normalized(DOSE_UNITS, match.group('dose_unit'))) if match.group('dose_unit') else None
        max_denominator_value = 1
        max_denominator_unit = get_normalized(PERIOD_UNIT, 'day')
        max_text_start, max_text_end = match.span()
        max_text = match[0]
        max_readable = self.get_readable(
            max_numerator_value=max_numerator_value, 
            max_numerator_unit=max_numerator_unit, 
            max_denominator_value=max_denominator_value,
            max_denominator_unit=max_denominator_unit)
        return self.generate_match({'max_numerator_value': max_numerator_value, 'max_numerator_unit': max_numerator_unit, 'max_denominator_value': max_denominator_value, 'max_denominator_unit': max_denominator_unit, 'max_text_start': max_text_start, 'max_text_end': max_text_end, 'max_text': max_text, 'max_readable': max_readable})

parsers = [
    MaxParser(),
    MaxDailyParser(),
]

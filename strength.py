from classes.parser import *

# TODO: figure out what to do with multiple ingredient strengths
# NOTE: added \b border at end because was matching on ZONEGRAN (ONE G), 1 GELCAP (1 G), 1 GTT (1 G), and WEIGHT GAIN (EIGHT G)
class StrengthParser(Parser):
    parser_type = 'strength'
    match_keys = ['strength', 'strength_max', 'strength_unit', 'strength_text_start', 'strength_text_end', 'strength_text', 'strength_readable']
    def normalize_pattern(self):
        strength_patterns = []
        for n, p in STRENGTH_UNITS.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the strength_patterns array
            strength_patterns.append(r'|'.join(p))        
        pattern = re.compile(r'(?:(?P<strength_negation>' + RE_DOSE_STRENGTH_NEGATION + r')\s?)?(?P<strength>' + RE_RANGE + r')\s?(?P<strength_unit>' + r'|'.join(strength_patterns) + r')\b', flags = re.I)
        return pattern
    def normalize_match(self, match):
        # the standard RE_RANGE pattern will mach 1/2 which is fine for dose, but 5/325 is to complicated for strength, so disgard it for now
        # alternatively, if negation text is found before the strength, don't generate a match
        if match.group('strength').find('/') >= 0 or match.group('strength_negation'):
            return None

        strength_range = split_range(match.group('strength'))
        strength, strength_max = strength_range
        strength_unit = get_normalized(STRENGTH_UNITS, match.group('strength_unit'))
        strength_text_start, strength_text_end = match.span()
        strength_text = match[0]
        strength_readable = self.get_readable(strength, strength_max, strength_unit)
        return self.generate_match({'strength': strength, 'strength_max': strength_max, 'strength_unit': strength_unit, 'strength_text_start': strength_text_start, 'strength_text_end': strength_text_end, 'strength_text': strength_text, 'strength_readable': strength_readable})
    def get_readable(self, strength=None, strength_max=None, strength_unit=None):
        plural = (strength and strength > 1) or (strength_max and strength_max > 1)
        if strength_unit:
            if plural:
                strength_unit += 's' if strength_unit not in ['mg','mcg','g','mEq'] else ''
        else:
            strength_unit = ''
        
        strength = str(strength) if strength else ''
        if strength_max:
            strength += '-' + str(strength_max)

        readable = strength + ' ' + strength_unit
        readable = readable.strip()
        return readable

parsers = [
    StrengthParser()
]

#print(StrengthParser().parse('take one capsule (30 mg) prn nausea for 5 days'))
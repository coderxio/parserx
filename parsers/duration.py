from classes.parser import *

class DurationParser(Parser):
    parser_type = 'duration'
    match_keys = ['duration', 'duration_max', 'duration_unit', 'duration_text_start', 'duration_text_end', 'duration_text', 'duration_readable']
    def get_readable(self, duration=None, duration_max=None, duration_unit=None):
        plural = (duration and duration > 1) or (duration_max and duration_max > 1)
        if duration_unit:
            duration_unit += 's' if plural else ''
        else:
            duration_unit = ''

        duration = str(duration) if duration else ''
        if duration_max:
            duration += '-' + str(duration_max)
        
        readable = 'for ' + duration + ' ' + duration_unit
        readable = readable.strip()
        return readable

# for x [more] days
class DurationParserForXDays(DurationParser):
    pattern = r'(?:for|\bf|x)\s*(?P<duration>' + RE_RANGE + r')\s*(?:more)?\s?(?P<duration_unit>year(?:s)|month(?:s)|week(?:s)|day(?:s)|yr(?:s)\b|mon(?:s)\b|wk(?:s)?|d\b|w\b)'
    def normalize_match(self, match):
        duration_range = split_range(match.group('duration'))
        duration_text_start, duration_text_end = match.span()
        # NOTE: PERIOD_UNIT has the same content that duration_unit needs for normalization
        duration_unit = get_normalized(PERIOD_UNIT, match.group('duration_unit'))
        duration, duration_max = duration_range
        duration_text = ' '.join(match.groups())
        duration_readable = self.get_readable(duration, duration_max, duration_unit)
        return self.generate_match({'duration': duration, 'duration_max': duration_max, 'duration_unit': duration_unit, 'duration_text_start': duration_text_start, 'duration_text_end': duration_text_end, 'duration_text': duration_text, 'duration_readable': duration_readable})

# up to x days
class DurationParserUpToXDays(DurationParser):
    pattern = r'(?:for )?up to (?P<duration>' + RE_RANGE + r')\s?(?P<duration_unit>year(?:s)|month(?:s)|week(?:s)|day(?:s)|yr(?:s)\b|mon(?:s)\b|wk(?:s)|d\b)'
    def normalize_match(self, match):
        duration_range = split_range(match.group('duration'))
        duration_text_start, duration_text_end = match.span()
        # NOTE: PERIOD_UNIT has the same content that duration_unit needs for normalization
        duration_unit = get_normalized(PERIOD_UNIT, match.group('duration_unit'))
        duration, duration_max = duration_range
        duration_text = ' '.join(match.groups())
        duration_readable = self.get_readable(duration, duration_max, duration_unit)
        return self.generate_match({'duration': duration, 'duration_max': duration_max, 'duration_unit': duration_unit, 'duration_text_start': duration_text_start, 'duration_text_end': duration_text_end, 'duration_text': duration_text, 'duration_readable': duration_readable})
    def get_readable(self, duration=None, duration_max=None, duration_unit=None):
        plural = (duration and duration > 1) or (duration_max and duration_max > 1)
        if duration_unit:
            duration_unit += 's' if plural else ''
        else:
            duration_unit = ''

        duration = str(duration) if duration else ''
        if duration_max:
            duration += '-' + str(duration_max)
        
        readable = 'for up to ' + duration + ' ' + duration_unit
        readable = readable.strip()
        return readable

# on day x
class DurationParserOnDayX(DurationParser):
    pattern = r'on day(?:s)?\s?(?P<duration>' + RE_RANGE + r')'
    def normalize_match(self, match):
        duration_range = split_range(match.group('duration'))
        duration_text_start, duration_text_end = match.span()
        duration = 1 if duration_range[0] == duration_range[1] or duration_range[1] == None else int(duration_range[1]) - int(duration_range[0]) + 1
        duration_unit = 'day'
        duration, duration_max = [duration, duration]
        duration_text = ' '.join(match.groups())
        duration_readable = self.get_readable(duration, duration_max, duration_unit)
        return self.generate_match({'duration': duration, 'duration_max': duration_max, 'duration_unit': duration_unit, 'duration_text_start': duration_text_start, 'duration_text_end': duration_text_end, 'duration_text': duration_text, 'duration_readable': duration_readable})

parsers = [
    DurationParserForXDays(),
    DurationParserUpToXDays(),
    DurationParserOnDayX()
]

#print(DurationParserForXDays().parse('take one prn nausea for 5 days'))
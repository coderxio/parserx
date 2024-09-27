from .classes.parser import *

class FrequencyParser(Parser):
	parser_type = 'frequency'
	match_keys = ['frequency', 'frequency_max', 'period', 'period_max', 'period_unit', 'time_duration', 'time_duration_unit', 'day_of_week', 'time_of_day', 'offset', 'bounds', 'count', 'frequency_text_start', 'frequency_text_end', 'frequency_text', 'frequency_readable']
	def get_readable(self,frequency=None,frequency_max=None,period=None,period_max=None,period_unit=None,time_duration=None,time_duration_unit=None,day_of_week=None,count=None):
		readable = ''
		frequency_range = str(frequency) + ('-' + str(frequency_max) if frequency_max else '') if frequency != None else ''
		# period - don't show period if period = 1 (i.e. don't show every 1 day, just show every day -- or better yet, daily)
		period_range = ('' if period == 1 and period_max == None else str(period) + ('-' + str(period_max) if period_max else '')) if period != None else ''

		readable += 'once' if count == 1 else ''

		if frequency != None and period_unit != None and (frequency > 1 or (frequency_max != None and frequency_max > 1)):
			if frequency_range == '2' and period_unit == 'day':
				readable += 'twice daily'
			else:
				readable += frequency_range + ' times a ' + str(period_unit)
		elif frequency != None and period_unit != None and frequency == 1:
			if period_range == '' and period_unit == 'day':
				readable += 'daily'
			elif period_range == '2' and period_unit == 'day':
				readable += 'every other day'
			else:				
				readable += 'every ' + period_range + (' ' if period_range != '' else '') + period_unit + ('s' if period_range != '' else '')

		readable += '' if time_duration == None and time_duration_unit == None else ' for ' + str(time_duration) + ' ' + time_duration_unit
		readable += ' on ' + ', '.join(day_of_week.split('|')) if day_of_week != None else ''
		return readable

# bid | tid | qid
# bid-tid, bid or tid
# TODO: account for bid-tid being min 2 and max 3 times per day - currently it only finds the max of 3
# frequency = a (2 if b, 3 if t, 4 if q), period = 1, periodUnit = d
class FrequencyXID(FrequencyParser):
	pattern = r'(?:\b(?:\s?(?:to|-|or)\s?)?(?P<frequency>b|t|q)id)+'
	def normalize_match(self, match):
		frequency_dict = { 'b': 2, 't': 3, 'q': 4 }
		frequency = frequency_dict.get(match.group('frequency').lower(), None)
		period = 1
		period_unit = 'day'
		frequency_text_start, frequency_text_end = match.span()
		frequency_text = match.group(0)
		frequency_readable = self.get_readable(frequency=frequency,period=period,period_unit=period_unit)
		return self.generate_match({'frequency': frequency, 'period': period, 'period_unit': period_unit, 'frequency_text_start': frequency_text_start, 'frequency_text_end': frequency_text_end, 'frequency_text': frequency_text, 'frequency_readable': frequency_readable})

# q | every | each
# 4 | 4-6 | 4 to 6 | four | four-six | four to six
# hours | days | weeks | months | h | hrs | hr | min | mins | mon
# (a: normalize 'to' to '-', and explode)
# NOTE: optional duplicate RE_RANGE accounts for sigs like every 12 (twelve) hours
# frequency = 1, period = a[0], periodUnit = b (normalize to h, d, wk, min), [periodMax = a[1]]
class FrequencyEveryXDay(FrequencyParser):
	pattern = r'(?:q|every|each)\s?(?P<period>' + RE_RANGE + r')(?:\s' + RE_RANGE + r'\s)?\s?(?P<period_unit>month|mon|hour|day|d|week|wks|wk|h|hrs|hr|min)'
	def normalize_match(self, match):
		frequency = 1
		period, period_max = split_range(match.group('period'))
		period_unit = get_normalized(PERIOD_UNIT, match.group('period_unit'))
		frequency_text_start, frequency_text_end = match.span()
		frequency_text = match.group(0)
		frequency_readable = self.get_readable(frequency=frequency,period=period,period_max=period_max,period_unit=period_unit)
		# TODO: normalize text numbers to integer numbers - maybe make separate normalize_period_unit function that also hits the text_to_int function?
		return self.generate_match({'frequency': frequency, 'period': period, 'period_max': period_max, 'period_unit': period_unit, 'frequency_text_start': frequency_text_start, 'frequency_text_end': frequency_text_end, 'frequency_text': frequency_text, 'frequency_readable': frequency_readable})

# 4 | four | 4-6 | 4 to 6 | 4 or 6 | four-six | four to six | four or six
# time(s) | x
# [per | a | each | /]
# day | daily | week | weekly | month | monthly
# 2-3 times daily
# (a: remove 'times' or 'x', normalize 'to' to '-', and explode)
# frequency = a[0], frequencyMax = a[1], period = 1, periodUnit = b (normalize to d, wk, mo, yr)
# frequency = a (1 if once, 2 if twice), period = 1, periodUnit = b (normalize to d, wk, mo, yr)
# NOTE: 'daily' won't match this pattern because it requires specific times *per* day
class FrequencyXTimesPerDay(FrequencyParser):
	pattern = r'(?P<frequency>' + RE_RANGE + r'\s?(?:time(?:s)?|x|nights|days)|once|twice)\s?(?:per|a|each|every|\/)\s?(?P<period_unit>day|week|wk\b|month|year|d\b|w\b|mon|m\b|yr)'
	def normalize_match(self, match):
		frequency = frequency_max = match.group('frequency')
		if (frequency):
			frequency, frequency_max = split_frequency_range(frequency)
		else:
			frequency = 1
		period = 1
		period_unit = get_normalized(PERIOD_UNIT, match.group('period_unit'))
		frequency_text_start, frequency_text_end = match.span()
		frequency_text = match.group(0)
		frequency_readable = self.get_readable(frequency=frequency,frequency_max=frequency_max,period=period,period_unit=period_unit)
		# TODO: normalize text numbers to integer numbers - maybe make separate normalize_period_unit function that also hits the text_to_int function?
		return self.generate_match({'frequency': frequency, 'frequency_max': frequency_max, 'period': period, 'period_unit': period_unit, 'frequency_text_start': frequency_text_start, 'frequency_text_end': frequency_text_end, 'frequency_text': frequency_text, 'frequency_readable': frequency_readable})


# once | twice | 3-4 times
# daily | nightly | weekly | monthly | yearly
# once daily, twice monthly, daily
# (a: remove 'times' or 'x')
# frequency = a[0], frequencyMax = a[1], period = 1, periodUnit = b (normalize to d, wk, mo, yr)
# frequency = a (1 if once, 2 if twice, 1 if null), period = 1, periodUnit = b (normalize to d, wk, mo, yr)
class FrequencyXTimesDaily(FrequencyParser):
	pattern = r'(?:(?P<frequency>' + RE_RANGE + r'\s?(?:time(?:s)?|x)|once|twice)(?: \ba\b| per)?\s?)(?P<period_unit>day|d\b|daily|dialy|weekly|monthly|yearly|\bhs\b)'
	def normalize_match(self, match):
		frequency = frequency_max = match.group('frequency')
		if (frequency):
			frequency, frequency_max = split_frequency_range(frequency)
		else:
			frequency = 1
		period = 1
		period_unit = get_normalized(PERIOD_UNIT, match.group('period_unit'))
		frequency_text_start, frequency_text_end = match.span()
		frequency_text = match.group(0)
		frequency_readable = self.get_readable(frequency=frequency,frequency_max=frequency_max,period=period,period_unit=period_unit)
		# TODO: normalize text numbers to integer numbers - maybe make separate normalize_period_unit function that also hits the text_to_int function?
		return self.generate_match({'frequency': frequency, 'frequency_max': frequency_max, 'period': period, 'period_unit': period_unit, 'frequency_text_start': frequency_text_start, 'frequency_text_end': frequency_text_end, 'frequency_text': frequency_text, 'frequency_readable': frequency_readable})


# daily | nightly | weekly | monthly | yearly
# NOTE: this is where 'daily' matches 
# frequency = a[0], frequencyMax = a[1], period = 1, periodUnit = b (normalize to d, wk, mo, yr)
# frequency = a (1 if once, 2 if twice, 1 if null), period = 1, periodUnit = b (normalize to d, wk, mo, yr)
class FrequencyDaily(FrequencyParser):
	pattern = r'(?P<period_unit>\bd\b|daily|dialy|weekly|monthly|yearly|\bhs\b)'
	def normalize_match(self, match):
		frequency = 1
		period = 1
		period_unit = get_normalized(PERIOD_UNIT, match.group('period_unit'))
		frequency_text_start, frequency_text_end = match.span()
		frequency_text = match.group(0)
		frequency_readable = self.get_readable(frequency=frequency,period=period,period_unit=period_unit)
		# TODO: normalize text numbers to integer numbers - maybe make separate normalize_period_unit function that also hits the text_to_int function?
		return self.generate_match({'frequency': frequency, 'period': period, 'period_unit': period_unit, 'frequency_text_start': frequency_text_start, 'frequency_text_end': frequency_text_end, 'frequency_text': frequency_text, 'frequency_readable': frequency_readable})


# every | each | per | q
# [other] 
# day | week | month | morning | afternoon | evening | night | hs
# TODO: combine with the qpm/qhs/qday/qdaily group above (not sure if this still applies)
# frequency = 1, period = 1 (or 2 if a is not null), periodUnit = b (normalize to d, wk, mo), [when = b (normalize to MORN, AFT, EVE, etc]
# NOTE: moved below FrequencyDaily because "per day" was taking precedence in max daily dose text
class FrequencyEveryDay(FrequencyParser):
	pattern = r'(?:every|each|q|per|\ba)\s?(?P<period>other\b|o)?\s?(?:day (?:in the|at)\s?)?(?P<period_unit>hour|day|week|wk\b|month|morning(?! and)|afternoon|evening at bedtime|bedtime|evening|night|hs|pm|am|d\b)'
	def normalize_match(self, match):
		frequency = 1
		period = 2 if match.group('period') else 1
		period_unit = get_normalized(PERIOD_UNIT, match.group('period_unit'))
		frequency_text_start, frequency_text_end = match.span()
		frequency_text = match.group(0)
		frequency_readable = self.get_readable(frequency=frequency,period=period,period_unit=period_unit)
		return self.generate_match({'frequency': frequency, 'period': period, 'period_unit': period_unit, 'frequency_text_start': frequency_text_start, 'frequency_text_end': frequency_text_end, 'frequency_text': frequency_text, 'frequency_readable': frequency_readable})


# every | on
# Thursday
# Monday, Tuesday, Wednesday, and Friday
# dayOfWeek = a
class FrequencySpecificDayOfWeek(FrequencyParser):
	pattern = r'(?:every|on|q)\s?(?P<day_of_week>(?:(?:\s?(?:and|&|\+|,|\s)\s?)?(?:' + RE_DAYS_OF_WEEK + '))+)'
	def normalize_match(self, match):
		# TODO: normalize days of week to be comma or pipe delimited - tuesday and thursday -> tuesday|thursday or tuesday,thursday
		day_of_week = match.group('day_of_week')
		frequency_text_start, frequency_text_end = match.span()
		frequency_text = match.group(0)
		frequency_readable = self.get_readable(day_of_week=day_of_week)
		# TODO: normalize text numbers to integer numbers - maybe make separate normalize_period_unit function that also hits the text_to_int function?
		return self.generate_match({'day_of_week': day_of_week, 'frequency_text_start': frequency_text_start, 'frequency_text_end': frequency_text_end, 'frequency_text': frequency_text, 'frequency_readable': frequency_readable})


# in the
# morning | evening | afternoon
# frequency = 1, when = a
class FrequencyInTheX(FrequencyParser):
	pattern = r'in the\s?(morning|evening|afternoon)'
	def normalize_match(self, match):
		frequency = 1
		period = 1
		period_unit = 'day'
		frequency_text_start, frequency_text_end = match.span()
		frequency_text = match.group(0)
		frequency_readable = self.get_readable(frequency=frequency,period=period,period_unit=period_unit)
		return self.generate_match({'frequency': frequency, 'period': period, 'period_unit': period_unit, 'frequency_text_start': frequency_text_start, 'frequency_text_end': frequency_text_end, 'frequency_text': frequency_text, 'frequency_readable': frequency_readable})


# at
# bedtime | night | nightly
# frequency = 1, when = a (normalize to HS)
class FrequencyAtBedtime(FrequencyParser):
	pattern = r'((?:at )?bedtime|(?:at )night|nightly)'
	def normalize_match(self, match):
		frequency = 1
		period = 1
		period_unit = 'day'
		frequency_text_start, frequency_text_end = match.span()
		frequency_text = match.group(0)
		frequency_readable = self.get_readable(frequency=frequency,period=period,period_unit=period_unit)
		return self.generate_match({'frequency': frequency, 'period': period, 'period_unit': period_unit, 'frequency_text_start': frequency_text_start, 'frequency_text_end': frequency_text_end, 'frequency_text': frequency_text, 'frequency_readable': frequency_readable})


# x1 | x 1
# exclude if followed by: day | week | month
# one time only
# count = 1
class FrequencyOneTime(FrequencyParser):
	pattern = r'(?:x\s?1\b(?!day| day|d\b| d\b|week| week|w\b| w\b|month| month|mon|m\b| m\b| mon\b)|(?:1|one) time(?: only)?(?! daily| per)|for (?:1|one) dose|once|once in imaging|before transfusion|(?:one|1) hour prior to (?:dental )?appointment|at (?:the )?(?:first|1st) (?:onset:sign) of symptoms)'
	def normalize_match(self, match):
		count = 1
		frequency_text_start, frequency_text_end = match.span()
		frequency_text = match.group(0)
		frequency_readable = self.get_readable(count=count)
		# TODO: normalize text numbers to integer numbers - maybe make separate normalize_period_unit function that also hits the text_to_int function?
		return self.generate_match({'count': count, 'frequency_text_start': frequency_text_start, 'frequency_text_end': frequency_text_end, 'frequency_text': frequency_text, 'frequency_readable': frequency_readable})


class FrequencyAsDirected(FrequencyParser):
	pattern = r'as directed(?: on package)?|ad lib|as dir\b|as instructed|see admin instructions|follow package directions|see notes|sliding scale|per package instructions'
	def normalize_match(self, match):
		frequency_text_start, frequency_text_end = match.span()
		# frequency_text = match.group(0)
		frequency_text = 'as directed'
		frequency_readable = frequency_text
		# TODO: normalize text numbers to integer numbers - maybe make separate normalize_period_unit function that also hits the text_to_int function?
		return self.generate_match({'frequency_text_start': frequency_text_start, 'frequency_text_end': frequency_text_end, 'frequency_text': frequency_text, 'frequency_readable': frequency_readable})

"""
TODO: improvements:
What about "at 8am" timings of meds?
Maybe check for "with meals" and infer three times daily?
"""

parsers = [
	FrequencyXID(),
	FrequencyEveryXDay(),
	FrequencyXTimesPerDay(),
	FrequencyXTimesDaily(),
	FrequencyDaily(),
	FrequencyEveryDay(),
	FrequencySpecificDayOfWeek(),
	FrequencyInTheX(),
	FrequencyAtBedtime(),
	FrequencyOneTime(),
	# FrequencyAsDirected(), # NOTE: removing this parser for DRX implementation - may consider adding back
]
from .classes.parser import *

# in the
# morning | evening | afternoon
# NOTE: nightly is weird, but matches here too
# NOTE: attempting to exclude UMS by excluding "morning and" and " and 1 tablet in the evening"
class WhenParser(Parser):
	parser_type = 'when'
	match_keys = ['when', 'when_text_start', 'when_text_end', 'when_text', 'when_readable']
	pattern = r'(?P<ums_sig> and .{0,30})?(?P<when_relation>with|\bw|\bc|before|\ba|after|\bp|on an empty stomach in the|in the|at|every|each|\bq|night)(?: each| every)?(?P<when_time>\s?(?:c\b|meal(?:s)? and (?:at )?bed(?:\s)?time|meal(?:s)?|food|cm\b|breakfast and lunch|breakfast and dinner|breakfast|morning meal|the first food beverage or medicine of the day|cd\b|lunch|cv\b|dinner|(?:the )?eve(?:ning)? meal|morning before breakfast|(?:morning|first meal of the day) on an empty stomach|morning with breakfast|morning(?! and)|morn\b|am\b(?! and)|evening at bed(?:\s)?time|bed(?:\s)?time|evening|eve\b|afternoon|aft\b|pm\s?hs|pm\b|night at bed(?:\s)?time|night|hs\b|ly|(?<!a)f\b))'
	def normalize_match(self, match):
		ums_sig = match.group('ums_sig')
		if (ums_sig):
			when = when_text_start = when_text_end = when_text = when_readable = None
		else:
			# TODO: normalize before to 'a' and after to 'p', etc
			# TODO: normalize meals to 'm', etc
			when_relation = match.group('when_relation')
			when_time = match.group('when_time')
			when = get_normalized(WHEN, when_relation + when_time)
			when_text_start, when_text_end = match.span()
			when_text = match.group(0)
			when_readable = self.get_readable(when=when)
		return self.generate_match({'when': when, 'when_text_start': when_text_start, 'when_text_end': when_text_end, 'when_text': when_text, 'when_readable': when_readable})
	def get_readable(self, when=None):
		readable = when if when else ''
		return readable

# Things that don't match the more common patterns above
class OtherWhenParser(WhenParser):
	pattern = r'(?P<when>bedtime|\bam\b|\bhs\b|before transfusion|while awake)'
	def normalize_match(self, match):
		when = match.group('when')
		when = get_normalized(WHEN, when)
		when_text_start, when_text_end = match.span()
		when_text = match.group(0)
		when_readable = self.get_readable(when=when)
		return self.generate_match({'when': when, 'when_text_start': when_text_start, 'when_text_end': when_text_end, 'when_text': when_text, 'when_readable': when_readable})


"""
PC	http://hl7.org/fhir/v3/TimingEvent	PC	after meal (from lat. post cibus)
PCM	http://hl7.org/fhir/v3/TimingEvent	PCM	after breakfast (from lat. post cibus matutinus)
PCD	http://hl7.org/fhir/v3/TimingEvent	PCD	after lunch (from lat. post cibus diurnus)
PCV	http://hl7.org/fhir/v3/TimingEvent	PCV	after dinner (from lat. post cibus vespertinus)
"""

parsers = [
	WhenParser(),
	OtherWhenParser(),
]
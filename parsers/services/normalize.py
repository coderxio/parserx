import collections
import re
from fractions import Fraction

RE_WRITTEN_NUMBERS = r'one(?:\s|-)?(?:quarter|half)|quarter|half|one point (?:one|two|three|four|five|six|seven|eight|nine)|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty(?:\s|-)?(?:one|two|three|four|five|six|seven|eight|nine)|twenty|thirty(?:\s|-)?five|thirty|forty|fifty'
#one (?:and |& )one(?:-|\s)half| 

# NOTE: keep the x-y at the beginning and x at the end so that it finds the x-y first without stopping
# (
#   (
#     (WRITTEN_NUMBER OR 1.5 OR 1/2)
#     TO
#     (WRITTEN_NUMBER OR 1.5 OR 1/2) 
#   )
#   OR (1.5 OR 1/2)
#   OR WRITTEN_NUMBER
# )
RE_RANGE = r'(?:(?:' + RE_WRITTEN_NUMBERS + r'|(?:\d*(?:\.|/))?\d+)(?:\s*(?:to|-|or|/|&|and)\s*)(?:' + RE_WRITTEN_NUMBERS + r'|(?:\d*(?:\.|/))?\d+)|(?:\d*(?:\.|/))?\d+|(?:' + RE_WRITTEN_NUMBERS + r'))'

RE_DAYS_OF_WEEK = r'monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon\b|tue\b|tues\b|wed\b|thu\b|thur\b|thurs\b|fri\b|sat\b|sun\b|m\b|tu\b|w\b|th\b|t\b|f\b|sa\b|su\b|mwf'
 
"""
  TODO: make all of the ac / pc / hs / etc
	https://www.hl7.org/fhir/valueset-event-timing.html
	Code	System	Display	Definition
	MORN	http://hl7.org/fhir/event-timing	Morning	event occurs during the morning
	AFT	http://hl7.org/fhir/event-timing	Afternoon	event occurs during the afternoon
	EVE	http://hl7.org/fhir/event-timing	Evening	event occurs during the evening
	NIGHT	http://hl7.org/fhir/event-timing	Night	event occurs during the night
	
	PHS	http://hl7.org/fhir/event-timing	After Sleep	event occurs [offset] after subject goes to sleep
	HS	http://hl7.org/fhir/v3/TimingEvent	HS	Description: Prior to beginning a regular period of extended sleep (this would exclude naps). Note that this might occur at different times of day depending on a person's regular sleep schedule.
	WAKE	http://hl7.org/fhir/v3/TimingEvent	WAKE	Description: Upon waking up from a regular period of sleep, in order to start regular activities (this would exclude waking up from a nap or temporarily waking up during a period of sleep) Usage Notes: e.g. Take pulse rate on waking in management of thyrotoxicosis. Take BP on waking in management of hypertension Take basal body temperature on waking in establishing date of ovulation
	
	C	http://hl7.org/fhir/v3/TimingEvent	C	Description: meal (from lat. ante cibus)
	CM	http://hl7.org/fhir/v3/TimingEvent	CM	Description: breakfast (from lat. cibus matutinus)
	CD	http://hl7.org/fhir/v3/TimingEvent	CD	Description: lunch (from lat. cibus diurnus)
	CV	http://hl7.org/fhir/v3/TimingEvent	CV	Description: dinner (from lat. cibus vespertinus)
	
	AC	http://hl7.org/fhir/v3/TimingEvent	AC	before meal (from lat. ante cibus)
	ACM	http://hl7.org/fhir/v3/TimingEvent	ACM	before breakfast (from lat. ante cibus matutinus)
	ACD	http://hl7.org/fhir/v3/TimingEvent	ACD	before lunch (from lat. ante cibus diurnus)
	ACV	http://hl7.org/fhir/v3/TimingEvent	ACV	before dinner (from lat. ante cibus vespertinus)
	
	PC	http://hl7.org/fhir/v3/TimingEvent	PC	after meal (from lat. post cibus)
	PCM	http://hl7.org/fhir/v3/TimingEvent	PCM	after breakfast (from lat. post cibus matutinus)
	PCD	http://hl7.org/fhir/v3/TimingEvent	PCD	after lunch (from lat. post cibus diurnus)
	PCV	http://hl7.org/fhir/v3/TimingEvent	PCV	after dinner (from lat. post cibus vespertinus)
"""
"""
	TODO: associate these common codings with each structured frequency
	https://www.hl7.org/fhir/valueset-timing-abbreviation.html
	Code	Display	Definition
	BID	BID	Two times a day at institution specified time
	TID	TID	Three times a day at institution specified time
	QID	QID	Four times a day at institution specified time
	AM	AM	Every morning at institution specified times
	PM	PM	Every afternoon at institution specified times
	QD	QD	Every Day at institution specified times
	QOD	QOD	Every Other Day at institution specified times
	Q4H	Q4H	Every 4 hours at institution specified times
	Q6H	Q6H	Every 6 Hours at institution specified times
"""
# pattern: new RegExp('(with|before|after)\s*(breakfast|lunch|dinner|meals|each meal)', 'ig'),	

# NOTE: periodUnit 'day' should include pretty much all of 'when' array
# for FHIR conversion: https://www.hl7.org/fhir/valueset-units-of-time.html
PERIOD_UNIT = {
  'day': [ 'daily', 'dialy', 'nightly', 'days', 'day', r'\bd\b', 'morning', 'morn', 'am', 'afternoon', 'aft', 'pm', r'evening at bed(?:\s)?time', r'bed(?:\s)?time', 'evening', 'eve', 'night', 'hs' ],
  'week': [ 'weekly', 'weeks', 'week', 'wks', 'wk', r'\bw\b' ],
  'month': [ 'monthly', 'months', 'month', 'mon', 'mo' ],
  'hour': [ 'hourly', 'hours', 'hour', 'hrs', 'hr', r'\bh\b' ],
  'minute': [ 'minutes', 'minute', 'mins', 'min', r'\bm\b' ],
  'second': [ 'seconds', 'second', 'secs', 'sec', r'\bs\b' ],
  'year': [ 'yearly', 'years', 'year', 'yrs', 'yr', r'\by\b' ],
}

# for FHIR conversion: https://www.hl7.org/fhir/valueset-days-of-week.html
DAY_OF_WEEK = {
  'monday': [ r'monday(?:s)?', 'mon', 'mo', 'm' ],
  'tuesday': [ r'tuesday(?:s)?', 'tues', 'tue', 'tu' ],
  'wednesday': [ r'wednesday(?:s)?', 'weds', 'wed', 'wd', 'w' ],
  'thursday': [ r'thursday(?:s)?', 'thurs', 'thu', 'th' ],
  'friday': [ r'friday(?:s)?', 'fri', 'fr', 'f' ],
  'saturday': [ r'saturday(?:s)?', 'sat', 'sa' ],
  'sunday': [ r'sunday(?:s)?', 'sun', 'su' ],
}
 
#(?:with|\bc\.|before|\ba|\ba\.|after|\bp|\bp\.|in the|at|every)
WHEN = {
  'in the morning': [ r'(?:in the|every|each)\s?(?:morning|morn(?!ing)|a m\b|am)', r'a m\b', r'\bam\b', r'\bqam\b', r'q am\b' ],
  'in the morning with breakfast': [],
  'in the afternoon': [ r'(?:in the|every|each|at)\s?(?:aft(?:ernoon)?|p m\b|pm)', r'\bqpm\b', 'q afternoon' ],
  'in the evening at bedtime': [r'(?:in the|every)\s?evening at bed(?:\s)?time'],
  'in the evening': [ r'(?:in the|every|each)\s?eve(?:ning)?(?! at bed(?:\s)?time)' ],
  'at night': [ r'(?:in the|at|every|each)\s?night(?! at bed(?:\s)?time)', r'nightly(?! at bed(?:\s)?time)' ],
  'at bedtime': [ r'(?!eve(?:ning) )(?:in the|at|every|before|every night at|nightly at|each)\s?bed(?:\s)?time', r'\bqhs\b', r'q hs\b', r'bed(?:\s)?time', r'\bhs\b', r'qpm\s?hs' ],
  'with meal': [ r'(?:with|each|every|at)?\s?meal(?:s)?', r'c c\b', r'\bcc\b', 'with food', 'wf' ],
  'with breakfast and lunch': [],
  'with breakfast and dinner': [],
  'with breakfast': [ r'(?:with|each|every|at)? breakfast(?! and lunch| and dinner)' ],
  'with lunch': [ r'(?:with|each|every|at)?\s?lunch', r'\bcd\b', r'c d\b' ],
  'with dinner': [ r'(?:with|each|every|at)?\s?dinner', r'\bcv\b', r'c v\b', r'with (?:the )?eve(?:ning)? meal' ],		
  'before meal': [ r'before(?: a)? meal(?:s)?', r'\bac\b', r'a c\b' ],
  'before breakfast': [ r'before (?:breakfast|morning meal|the first food beverage or medicine of the day)', r'(?:in the|every|each) morning before breakfast', r'\bacm\b', r'a c m\b', 'on an empty stomach in the morning', 'in the morning on an empty stomach', r'before the first meal of the day(?: on an empty stomach)?' ],
  'before lunch': [ 'before lunch', r'\bacd\b', r'a c d\b' ],
  'before dinner': [ 'before dinner', r'\bacv\b', r'a c v\b' ],
  'after meal': [ r'after meal(?:s)?', r'\bpc\b', r'p c\b' ],
  'after breakfast and dinner': [],
  'after breakfast': [ r'after breakfast(?! and dinner)', r'\bpcm\b', r'p c m\b' ],
  'after lunch': [ 'after lunch', r'\bpcd\b', r'p c d\b' ],
  'after dinner': [ 'after dinner', r'\bpcv\b', r'p c v\b' ],
  'before transfusion': [],
  'while awake': [],
  'before each meal and at bedtime': [r'before (?:each )?meal(?:s)? and (?:at )?bed(?:\s)?time'],
}

METHODS = {
  'swish and swallow': [],
  'dilute': [],
  'inject': [r'\binj\b'],
  'wash': [],
  'sprinkle': [],
  'apply': [r'^app\b', 'aaa'],
  'administer': [],
  'dissolve': [],
  'shampoo': [],
  'inhale': [r'inh\b', r'neb\b', r'nebuliz(?:ation|ed|er|e)', r'\binl\b'],
  'insert': [],
  'use': [],
  'push': [],
  'give': [],
  'take': [r'\btk(?:\b|\d)', r'^t(?:\b|\d)', 'taking'],
  'swallow': [],
  'instill': [],
  'chew': [],
  'swish': [],
  'suck': [],
  'sniff': [],
  'place': [],
  'spray': [],
  'implant': [],
  'rinse': [],
  'test': [],
}
"""
# other "methods" from FHIR
'subtract - dosing instruction fragment': [],
'as': [],
'or': [],
'finish': [],
'until gone': [],
'upon': [],
'per': [],
'sparingly': [],
'call': [],
'when': [],
'to': [],
'then': [],
'multiply': [],
'discontinue': [],
'with': [],
'then discontinue': [],
'until': [],
'every': [],
'before': [],
'now': [],
'follow directions': [],
'if': [],
'and': [],
'twice': [],
'follow': [],
'until finished': [],
'during': [],
'at': [],
'dosing instruction imperative': [],
'only': [],
'hold': [],
'constant': [],
'divide': [],
'add': [],
'once': [],
'then stop': [],
"""

# NOTE: topical routes are handled separately (below)
# NOTE: affected ears == ear(s) because the ( and ) get stripped
ROUTES = {
	'by mouth': ['by oral route', 'oral', r'orally(?! disintegrating)', r'(?:\b|\d)po\b', r'(?:\b|\d)p o\b', r'oral\b', 'chew', r'(?:with food|with (?:a )?meal(?:s)?|empty stomach|\bwf\b)'],
  'in left ear': [r'(?:in to |into |in |to |per )?(?:the )?left ear'],
  'in right ear': [r'(?:in to |into |in |to |per )?(?:the )?right ear'],
  'in each ear': [r'(?:in to |into |in |to |per )?(?:bilateral ears|both ears|each ear|(?<!affected )ears)', r'\bau\b'],
  'in affected ear': [r'(?:in to |into |in |to |per )?(?:the )?affected ear\b'],
  'in ear(s)': ['by ear', 'otically', 'otic', r'(?:in to |into |in |to |per )?(?:the )?(?<!affected )ear\b', 'affected ears'],
  'in left nostril': [r'(?:in to |into |in |to |per )?(?:the )?left (?:nose|nostril|nare)'],
  'in right nostril': [r'(?:in to |into |in |to |per )?(?:the )?right (?:nose|nostril|nare)'],
  'in each nostril': [r'(?:in to |into |in |to |per )?(?:both nostrils|each nostril|(?<!affected )nostrils|each nare|ea nare)', r'\bien\b'],
  'in nostril(s)': [r'\bvn\b', 'by nose', 'nasally', r'nasal(?!.{0,100}nostril)', 'intranasal', r'(?:in to |into |in |to |per )?(?:the )?(?!each|left|right|both)(?:affected)?(?:nose|nostrils|nostril|nare)\b', 'affected nostrils'],
  'in left eye': [r'(?:in to |into |in |to |per )?(?:the )?left eye', r'\bos\b'],
  'in right eye': [r'(?:in to |into |in |to |per )?(?:the )?right eye', r'\bod\b'],
  'in each eye': [r'(?:in to |into |in |to |per )?(?:both eyes|each eye|(?<!affected )eyes)', r'\bou\b'],
  'in affected eye': [r'(?:in to |into |in |to |per )?(?:the )?affected eye\b'],
  'in eye(s)': ['by eye', 'ophthalmically', 'ophthalmic', 'ophth', r'(?:in to |into |in |to |per )?(?:the )?(?<!affected )eye(?!\s?lid)\b', 'affected eyes'],
  'vaginally': ['vaginal', r'(?:in to|into|in|per|to)(?: the)? vagina', r'(?:\b|\d)pv\b'],
  'into the uterus': ['intrauterine', 'uterus'],
  'under the tongue': ['sublingually', 'sublingual', r'under (?:the )?tongue', r'sub(?: |-)?lingual(?:ly)?', r'(?:\b|\d)sl\b'],
  'under the skin': ['subcutaneously', 'subcutaneous', r'(?<!massage )(?:into|in|under) (?:the )?skin', r'sub(?: |-)*cutaneous(?:ly)?', r'(?:\b|\d)subq\b', r'(?:\b|\d)sc\b', r'(?:\b|\d)subcu\b', r'(?:\b|\d)sq\b', r'(?:\b|\d)s/q\b'],
  'rectally': ['rectal', r'(?:\b|\d)pr\b', r'in(?:to)* (?:the )?(?:butt|anus|rectum)'],
  'into the muscle': ['intramuscularly', r'\bim\b', 'intramuscular', r'in(?:to)?(?: the)? muscle', 'intramuscularrly'],
  'intravenously': [r'(?<!schedule )\biv\b', 'intravenous'],
  'cutaneously': [r'\bcutaneous'],
  'to the skin': ['transdermally', 'transdermal', 'patch', 'patches'],
  'enterally': ['enteral'],
  'via g-tube': [r'(?:via|per) g(?:-| )?tube', 'gastrostomy'],
  'via j-tube': [r'(?:via|per) j(?:-| )?tube', 'jejunostomy'],
  'via ng-tube': [r'(?:via|per) (?:ng|n\.g\.)(?:-| )?tube', 'nasogastrically', 'nasogastricly', 'nasogastric'],
  'to the teeth': ['dentally', r'dental(?! procedure)', r'to(?: the)? teeth'],
  'intra-articularly': [r'(?:in to|into|in|per) (?:the|one|both|two|all) joint', 'intra-articular'],
  'via nebulizer': ['via nebulization', r'(?:via |per|using a |from the |by )?nebuliz(?:ation|ed|er|e)', r'(?:\b|\d)neb\b'],
  'in urethra': [r'(?:into|via|within the|within) urethra', 'urethrally', 'urethral'],
  'on the tongue': ['translingual', 'translingually'],
  'between the cheek and gums': ['buccally', r'between (?:the )?cheek and (?:the )?gums', 'buccal', 'inside the cheek'],
  'to the gum': [],
  'to mucous membrane': [r'(?:to|on) (?:the )?mucous membrane(?:s)?', r'mucous membrane(?:s)?'],
  'via injection': ['by injection route', r'(?:via |per )injection', r'(?<!with )injection(?:s)?(?! intramuscularly| intravenously| cuteneously| subcutaneously| intra-articularly)'],
  'swish and spit': [r'swish around (?:inside mouth )?and then expectorate', 'swish and expectorate'],
  'swish and swallow': [],
  'subdermal': [],
  'to the mouth or throat': [],
  'scalp': ['scalp area'],
}

MISCELLANEOUS_ROUTES = {
  'miscellaneous': ['misc', 'device', 'meter', 'needle', 'pen needle', 'strip', r'(?:test )?strip(?:s)', r'test(?:ing)?', r'check(?:ing|s)?', 'monitor'],
}

"""
NOTE: other "routes" from FHIR
  'endocervical': [],
  'endosinusial': [],
  'endotracheopulmonary': [],
  'extra-amniotic': [],
  'gastroenteral': [],
  'gingival': [],
  'intraamniotic': [],
  'intrabursal': [],
  'intracardiac': [],
  'intracavernous': [],
  'intracoronary': [],
  'intradermal': [],
  'intradiscal': [],
  'intralesional': [],
  'intralymphatic': [],
  'intraocular': [],
  'intrapleural': [],
  'intrasternal': [],
  'intravesical': [],
  'oromucosal': [],
  'periarticular': [],
  'perineural': [],
  'subconjunctival': [],
  'intraluminal': [],
  'intraperitoneal': [],
  'transmucosal': [],
  'intrabiliary': [],
  'epidural': [],
  'suborbital': [],
  'caudal': [],
  'intraosseous': [],
  'intrathoracic': [],
  'intraductal': [],
  'intratympanic': [],
  'intravenous central': [],
  'intramyometrial': [],
  'gastro-intestinal stoma': [],
  'colostomy': [],
  'periurethral': [],
  'intracoronal': [],
  'retrobulbar': [],
  'intracartilaginous': [],
  'intravitreal': [],
  'intraspinal': [],
  'orogastric': [],
  'transurethral': [],
  'intratendinous': [],
  'intracorneal': [],
  'oropharyngeal': [],
  'peribulbar': [],
  'nasojejunal': [],
  'fistula': [],
  'surgical drain': [],
  'intracameral': [],
  'paracervical': [],
  'intrasynovial': [],
  'intraduodenal': [],
  'intracisternal': [],
  'intratesticular': [],
  'intracranial': [],
  'tumor cavity': [],
  'paravertebral': [],
  'intrasinal': [],
  'transcervical': [],
  'subtendinous': [],
  'intraabdominal': [],
  'subgingival': [],
  'intraovarian': [],
  'ureteral': [],
  'peritendinous': [],
  'intrabronchial': [],
  'intraprostatic': [],
  'submucosal': [],
  'surgical cavity': [],
  'ileostomy': [],
  'intravenous peripheral': [],
  'periosteal': [],
  'esophagostomy': [],
  'urostomy': [],
  'laryngeal': [],
  'intrapulmonary': [],
  'mucous fistula': [],
  'nasoduodenal': [],
  'body cavity': [],
  'intraventricular route - cardiac': [],
  'intracerebroventricular': [],
  'percutaneous': [],
  'interstitial': [],
  'arteriovenous graft': [],
  'intraesophageal': [],
  'intragingival': [],
  'intravascular': [],
  'intradural': [],
  'intrameningeal': [],
  'intragastric': [],
  'intracorpus cavernosum': [],
  'intrapericardial': [],
  'intralingual': [],
  'intrahepatic': [],
  'conjunctival': [],
  'intraepicardial': [],
  'transendocardial': [],
  'transplacental': [],
  'intracerebral': [],
  'intraileal': [],
  'periodontal': [],
  'peridural': [],
  'lower respiratory tract': [],
  'intramammary': [],
  'intratumor': [],
  'transtympanic': [],
  'transtracheal': [],
  'digestive tract': [],
  'intraepidermal': [],
  'intrajejunal': [],
  'intracolonic': [],
  'intra-arterial': [],
  'intramedullary': [],
  'intrauterine': [],
  'arteriovenous fistula': [],
  'intrathecal': [],
"""

TOPICAL_ROUTES = {
  'topically': [r'topical\b', r'\btop\b', 'application', 'apply', 'patch'],
  'affected areas': [r'(?:involved|affected|effected) (?:areas|sites)'],
  'affected area': [r'\baa\b', r'(?:involved|affected|effected) (?:area|site)\b'],
  'affected and surrounding areas': [],
  # TODO: exclude back pain
  'back': [],
  'scalp': [],
  'torso': [],
  'arms': [],
  'legs': [],
  'abdomen': [],
  'arm': [],
  'eyelids': ['eye lids'],
  'eyelid': [r'eye lid\b'],
  'left big toe': ['left great toe'],
  'right big toe': ['right great toe'],
  'clean dry skin': [r'clean(?:ed)? dry skin'],
  'skin': [r'(?<!clean )(?<!cleaned )(?<!dry )skin'],
  'vagina': [],
  'blood blister': [],
  'buttocks': [r'butt\b'],
  'blood blister': [],
  'face': [],
  'chest': [],
  'shoulders': [],
}

INHALATION_ROUTES = {
  'into the lungs': ['via inhalation', 'respiratory tract', r'(?:via |per |using a |from the )?(?<!with )(?<!with albuterol )inhal(?:ation|ed|er|e)(?!.{0,30}(?:spray|nebuliz))', r'inh\b', r'inhalation(?:s)?', r'puff(?:s)? by mouth'],
}

# TODO: add a lot more here (mL, mcg, g, etc)
# NOTE: moved unit here - need to do more testing
STRENGTH_UNITS = {
  'mg': [r'(?:milligram(?:s)?|mgs)\b'],
  'mcg': [r'(?:microgram(?:s)?|mcgs)\b'],
  'g': [r'(?:gm|gms|gram(?:s)?)\b'],
  'international unit': [r'i\.u\.\b', r'iu\b', 'international units', r'int\'l unit(?:s)?',  r'intl unit(?:s)?'],
  # NOTE: don't want u at beginning of sig d/t 'u to test blood sugar' which should be 'use'
  'unit': [r'units', r'un\b', r'(?<!^)u\b'],
  'mEq': [r'milliequivalent(?:s)?'],
}

DOSE_STRENGTH_NEGATION = [
  'no more than',
  r'do not (?:exceed|take more than)',
  'not to exceed',
  r'\bnmt',
  r'\bnte',
  # NOTE: negating o and a prevents things like fosamax / topamax / zithromax
  r'(?<!o|a)max(?:imum)? (?:daily )?(?:dose|amount)?\s?(?:=|is)?',
  r'mdd(?:\s?=)?',
  r'take with(?: a)?',
  r'combined dos(?:e|age) of',
  'in addition to',
  'total of',
  'increasing daily dose to',
  'finish current supply of',
]
RE_DOSE_STRENGTH_NEGATION = r'|'.join(DOSE_STRENGTH_NEGATION)

EXCLUDED_MDD_DOSE_UNITS = [
  'mg',
  'mcg',
  # 'g',
  # 'mL',
  'L',
  'international unit',
  'unit',
  'mEq',
  'teaspoon',
  'tablespoon',
  'puff',
  'application',
  'spray',
  'drop',
  'syringe',
  'vial',
  'packet',
  'pen',
  'oz',
  'injection',
  'cm',
]

DOSE_UNITS = {
  # to match ahead of one-letter dose form (L)
  'lozenge': [r'\bloz\b'],
  'liniment': [],
  'lotion': [],
  'liquid dose form': [],
  # volume
  'mL': ['milliliter', r'mls\b', r'cc\b', 'mililiter'],
  'L': [r'(?:\bliter)'],
  'oz': ['ounce'],
  'cm': ['centimeter', r'cm\b', r'cms\b'],
  'inch': [],
  'teaspoon': [r'tsp\b', 'teaspoons', 'teaspoonsful', 'teaspoonful', 'teaspoonfuls'],
  'tablespoon': [r'tbsp\b', 'tablespoon', 'tablespoonsful', 'tablespoonful', 'tablespoonfuls'],
  # tablet
  # TODO: add all synonyms to exclusion for tablet
  # ERROR: make sure "tablespoon" does not match on "tab" -- use a negative lookahead
  'tablet': [r'(?<!film-coated)(?<!effervescentgastro-resistant)(?<!orodispersible)(?<!prolonged-release)(?<!vaginal)(?<!effervescent vaginal)(?<!modified-release)(?<!chewable)(?<!sublingual)(?<!buccalmuco-adhesive buccal)(?<!soluble)(?<!dispersible)(?<!delayed-release particles)(?<!oral)(?<!inhalation vapor)(?<!implantation)(?<!extended-release film coated)(?<!ultramicronized)(?<!extended-release)(?<!extended-release enteric coated)(?<!delayed-release)(?<!coated particles)(?<!sustained-release buccal)(?<!multilayer)\s*tab(?:let)?(?:s)?', r'tb\b', r't\b', r'ts\b', r'a tab(?:let)?', r'whole tab(?:let)?'],
  'film-coated tablet': [r'(?:film-coated|film coated) tab(?:let)?(?:s)?'],
  'effervescent tablet': [r'effervescent tab(?:let)?(?:s)?'],
  'gastro-resistant tablet': [r'(?:gastro-resistant|gastro resistant) tab(?:let)?(?:s)?'],
  'orodispersible tablet': [r'(?:orodispersible|oral disintegrating|orally disintegrating) tab(?:let)?(?:s)?', r'\bodt\b', r'o.d.t.'],
  'prolonged-release tablet': [r'(?:prolonged-release|prolonged release) tab(?:let)?(?:s)?'],
  'vaginal tablet': [r'vaginal tab(?:let)?(?:s)?'],
  'effervescent vaginal tablet': [r'effervescent vaginal tab(?:let)?(?:s)?'],
  'modified-release tablet': [r'(?:modified-release|modified release) tab(?:let)?(?:s)?'],
  'chewable tablet': [r'chewable tab(?:let)?(?:s)?', r'chewable'],
  'sublingual tablet': [r'(?:sublingual|s.l.|sl) tab(?:let)?(?:s)?'],
  'buccal tablet': [r'buccal tab(?:let)?(?:s)?'],
  'muco-adhesive buccal tablet': [r'(?:muco-adhesive|muco adhesive) buccal tab(?:let)?(?:s)?'],
  'soluble tablet': [r'soluble tab(?:let)?(?:s)?'],
  'dispersible tablet': [r'dispersible tab(?:let)?(?:s)?'],
  'delayed-release particles tablet': [r'(?:delayed-release|delayed release|d.r.|dr) particles tab(?:let)?(?:s)?'],
  'oral tablet': [r'oral tab(?:let)?(?:s)?'],
  'inhalation vapor tablet': [r'inhalation vapor tab(?:let)?(?:s)?'],
  'implantation tablet': [r'implantation tab(?:let)?(?:s)?'],
  'extended-release film coated tablet': [r'(?:extended-release|extended release|e.r.|er) (?:film coated|film-coated) tab(?:let)?(?:s)?'],
  'ultramicronized tablet': [r'(?:ultramicronized|ultra-micronized) tab(?:let)?(?:s)?'],
  'extended-release tablet': [r'(?:extended release|er|e.r.) tablet'],
  'extended-release enteric coated tablet': [r'(?:extended release|extended release|er|e.r.) (?:enteric coated|enteric-coated|e.c.|ec) tablet'],
  'delayed-release tablet': [r'(?:delayed release|d.r.|dr) tablet'],
  'coated particles tablet': [r'coated particles tab(?:let)?(?:s)?'],
  'sustained-release buccal tablet': [r'(?:sustained-release|sustained release|s.r.|sr) buccal tab(?:let)?(?:s)?'],
  'multilayer tablet': [r'(?:multilayer|multi-layer) tab(?:let)?(?:s)?'],		
  # capsule
  'capsule': [r'cap(?:sule)?(?:s)?\b', r'c\b', r'cs\b', 'gelcap'],
  'hard capsule': [r'hard cap(?:sule)?(?:s)?\b'],
  'soft capsule': [r'soft cap(?:sule)?(?:s)?\b'],
  'vaginal capsule': [r'vaginal cap(?:sule)?(?:s)?\b'],
  'hard capsule inhalation powder': [r'hard cap(?:sule)?(?:s)?\b inhalation powder'],
  'hard vaginal capsule': [r'hard vaginal cap(?:sule)?(?:s)?\b'],
  'soft vaginal capsule': [r'soft vaginal cap(?:sule)?(?:s)?\b'],
  'rectal capsule': [r'rectal cap(?:sule)?(?:s)?\b'],
  'inhalation vapor capsule': [r'inhalation vapor cap(?:sule)?(?:s)?\b'],
  'gastro-resistant capsule': [r'(?:gastro-resistant|gastro resistant) cap(?:sule)?(?:s)?\b'],
  'prolonged-release capsule': [r'(?:prolonged-release|prolonged release) cap(?:sule)?(?:s)?\b'],
  'coated pellets capsule': [r'coated pellets cap(?:sule)?(?:s)?\b'],
  'delayed-release capsule': [r'(?:delayed-release|delayed release|d.r.|dr) cap(?:sule)?(?:s)?\b'],
  'extended-release film coated capsule': [r'(?:extended-release|extended release|e.r.|er) (?:film coated|film-coated) cap(?:sule)?(?:s)?\b'],
  'extended-release coated capsule': [r'(?:extended-release|extended release|e.r.|er) coated cap(?:sule)?(?:s)?\b'],
  'extended-release capsule': [r'(?:extended-release|extended release|e.r.|er) cap(?:sule)?(?:s)?\b'],
  'coated capsule': [r'coated cap(?:sule)?(?:s)?\b'],
  'extended-release enteric coated capsule': [r'(?:extended-release|extended release|e.r.|er) (?:enteric coated|enteric-coated|e.c.|ec) cap(?:sule)?(?:s)?\b'],
  'delayed-release pellets capsule': [r'(?:delayed-release|delayed release|d.r.|dr) pellets cap(?:sule)?(?:s)?\b'],
  'modified-release capsule': [r'(?:modified-release|modified release) cap(?:sule)?(?:s)?\b'],
  'oromucosal capsule': [r'oromucosal cap(?:sule)?(?:s)?\b'],
  # patch
  'drug patch': [r'(?<!transdermal ) patch'],
  'transdermal patch': [r'patch'],
  # drops
  'drop': ['drops', 'gtt', 'drp'],
  'oral drop': ['oral drops'],
  'eye/ear drop': ['eye/ear drops'],
  'eye drop': ['eye drops', 'ophthalmic drop'],
  'prolonged-release eye drop': [r'(?:prolonged-release|prolonged release) eye drops'],
  'nasal drop': ['nasal drops', 'nose drop'],
  'eye/ear/nose drop': ['eye/ear/nose drops'],
  'ear drop': ['ear drops', 'otic drop'],
  'modified release drop': ['modified release drops', 'modified-release drop'],
  # spray
  'spray': [r'spr\b'],
  'oromucosal spray': [],
  'sublingual spray': [],
  'cutaneous spray': [],
  'cutaneous powder spray': [],
  'aerosol spray': [],
  'powder spray': [],
  'ear spray': [r'otic spray'],
  'vaginal spray': [],
  'rectal spray': [],
  'metered spray': [],
  'pressurized spray': [],
  'nasal spray': [],
  'cutaneous suspension spray': [],
  'cutaneous solution spray': [],
  # inhalation
  'puff': [r'inhalation', r'puff', r'\bpuf\b', r'pressurized inhalation(?:s)?', r'\bpfs\b'],
  'pressurised inhalation solution': [],
  'pressurised inhalation suspension': [],
  'pressurised inhalation emulsion': [],
  'inhalation powder': [],
  'inhalation vapor': [],
  'inhalation vapor powder': [],
  'inhalation vapor solution': [],
  'inhalation vapor ointment': [],
  'inhalation vapor liquid': [],
  'inhalation gas': [],
  # aerosol
  'aerosol generator': [],
  'metered dose aerosol inhaler': [],
  'nasal aerosol': [r'nasal spray'],
  'aerosol powder': [],
  'cutaneous aerosol': [],
  'metered dose aerosol': [],
  # gum
  'gummie': ['gummy'],
  'gum': [],
  'oral gum': [],
  'medicated chewing-gum': [r'medicated chewing gum'],
  # film
  'film': [],
  'extended-release film': [r'(?:extended-release|extended release|e.r.|er) film'],
  # cone
  'cone': [],
  'dental cone': [],
  # sponge
  'sponge': [],
  'vaginal sponge': [],
  'cutaneous sponge': [],
  # pellet
  'implantable pellet': [],
  'pellet': [],
  # inhaler
  #'inhaler': [],
  #'metered dose powder inhaler': [],
  #'metered dose inhaler': [r'MDI', r'M.D.I.'],
  #'breath activated powder inhaler': [],
  #'breath activated inhaler': [],
  # stick
  'ear stick': [],
  'nasal stick': [],
  'drug stick': [],
  'dental stick': [],
  'cutaneous stick': [],
  'urethral stick': [],
  'wound stick': [],
  # tampon
  'tampon': [r'tampon dose form'],
  'ear tampon': [],
  'medicated vaginal tampon': [],
  'rectal tampon': [],
  # paste
  'oral paste': [],
  'drug paste': [r'(?<!oral )paste'],
  'oromucosal paste': [],
  'gingival paste': [],
  # pill
  'pill': [],
  'pillule': [],
  'caplet': [],
  'drug aerosol': [],
  'drug aerosol foam': [r'foam'],
  'cachet': [],
  'drug pledget': [],
  'oral lyophilisate': [],
  'oromucosal gel': [],
  'gingival gel': [],
  'dental gel': [],
  'dental insert': [],
  'dental powder': [],
  'shampoo': [],
  'collodion': [],
  'medicated nail laquer': [],
  'poultice': [],
  'ophthalmic insert': [],
  'ear powder': [],
  'nasal powder': [],
  'eye/ear/nose ointment': [],
  'pessary': [],
  'enema': [],
  'suppository': [],
  'implantation chain': [],
  'implant dosage form': [],
  'extended-release insert': [],
  'vaginal insert': [],
  'urethral suppository': [],
  'metered powder': [],
  'rectal suppository': [],
  'extended-release suppository': [],
  'pastille': [],
  'gaseous dose form': [],
  'vaginal suppository': [],
  'extended-release bead implant': [],
  'solid dose form': [],
  'eye/ear ointment': [],
  'transdermal drug delivery system': [],
  'medicated toothpaste': [],
  'tincture': [],
  'spirit': [],
  'modified-release pessary': [],
  'bar': [],
  'buccal film': [],
  'orodispersible film': [],
  'pen': [],
  'applicatorful': ['applicatorsful', 'applicator'],
  # NOTE: have a separate parser for generic application keywords (i.e. 'apply')
  'application': [ r'applic\b', r'appl\b', r'app\b'],
  'capful': [],
  'injection': [],
  'packet': ['pkt'],
  'strip': ['test strip'],
  'syringe': [],
  'vial': [],
  'kit': ['meter kit'],
  # NOTE: have a separate parser for generic each keywords (i.e. 'strips', 'meter')
  # TODO: after standardized terminology re-architecture, prevent 'each' from triggering on 'into each nostril' type sigs
  'each': ['eaches', 'pen needle', 'test strip'],
  'vaginal ring': ['ring'],
  'dose': [],
  'swab': [],
  'squirt': [],
  'pump': [],
  'troche': [],
  'cartridge': ['cartridges'],
  'device': [],
  'pea-sized amount': ['pea-sized'],
  'to the affected area': ['aaa'],
}

PAIN_SEVERITIES = {
  'acute': [],
  'chronic': [],
  'any level of': [],
  'breakthrough': [],
  'mild to moderate': [r'mild-moderate'],
  'moderate to severe': [r'moderate-severe'],
  'mild to severe': [r'mild-severe'],
  'mild': [],
  'moderate': [],
  'severe': [],
  'intense': [],
  'intolerable': [],
}

PAIN_LOCATIONS = {
  'abdominal': [],
  'arthritis': [],
  'ear': [],
  'eye': [],
  'muscle/joint': [],
  'muscle': [],
  'nerve': [],
  'neuropathic': [],
  'joint': [],
  'throat': [],
  'back': [],
  'knee': [],
  'leg': [],
  'stent': [],
  'lower back': [],
  'upper back': [],
  'back': [],
  'post-operative': [r'post(?:-|\s)?op(?:erative)?'],
}

PAIN_TRIGGERS = {
  'unrelieved by PO medications': [],
  'with swallowing': ['w/ swallowing', 'on swallowing'],
  'with urination': ['w/ urination', 'on urination'],
}

RE_BASIC_PAIN = re.compile(r'\bpain', flags = re.I)
RE_PAIN_SEVERITY = []
RE_PAIN_LOCATION = []
RE_PAIN_TRIGGER = []
for n, p in PAIN_SEVERITIES.items():
  p.append(n)
  RE_PAIN_SEVERITY.append(r'|'.join(p))
for n, p in PAIN_LOCATIONS.items():
  p.append(n)
  RE_PAIN_LOCATION.append(r'|'.join(p))
for n, p in PAIN_TRIGGERS.items():
  p.append(n)
  RE_PAIN_TRIGGER.append(r'|'.join(p))
PAIN_PATTERN = re.compile(r'(?P<pain_severity>' + r'|'.join(RE_PAIN_SEVERITY) + r')?\s*(?P<pain_location>' + r'|'.join(RE_PAIN_LOCATION) + r')?\s*\bpain\s*(?P<pain_trigger>' + r'|'.join(RE_PAIN_TRIGGER) + r')?\s*(?:score|scale|rated)?\s*(?:(?:(?P<pain_logical_expression>greater than or equal to|>=|greater than|>|\bgte\b|\bg\.t\.e\.\b|\bgt\b|\bg\.t\.\b)\s*)?(?P<pain_score>' + RE_RANGE + r'))?', flags = re.I)

# NOTE: pain is intentionally missing from here because it has its own PainIndicationParser
INDICATIONS = {
  'acne': [],
  'acute migraine': [],
  'agitation': [],
  'allergic reaction': [],
  'allergies': [],
  'allergy': [],
  'anaphylaxis': [],
  'anxiety': [],
  'arthritis': [],
  'asthma': [],
  'bedwetting': [],
  'bee sting': [],
  'bladder irritation': [],
  'bladder spasm': [],
  'bleeding': [],
  'blood glucose monitoring': [],
  'blood sugar less than': [],
  'blood pressure': [],
  'bradycardia': [],
  'burning with urination': [],
  'cholesterol': ['choleserol'],
  'chest pain': [],
  'cold sore': ['cold sores'],
  'cold': [],
  'congestion': [],
  'constipation': [],
  'cough': [],
  'cramping': [],
  'cravings': [],
  'dandruff': [],
  'delirium': [],
  'demand feeding': [],
  'depression': [],
  'diarrhea': [],
  'diabetes': ['type 2 diabetes'],
  'difficulty breathing': [],
  'discomfort': [],
  'dizziness': [],
  'drainage': [],
  'dressing change': [],
  'dry eyes': [],
  'dry mouth': [],
  'dry skin': [],
  'dysmenorrhea': [],
  'dyspnea': [],
  'dysuria': [],
  'ear drainage': [],
  'ear fullness': [],
  'eczema': [],
  'edema': [],
  'erectile dysfunction': [r'e\.d\.', r'\bed\b'],
  'fever': [],
  'fever blisters': [],
  'fever greater than or equal to': [],
  'flares': [],
  'food allergy': [],
  'flatulence': [],
  'gas': [],
  'glaucoma': [],
  'gout': [],
  'hallucination': [],
  'headache': [],
  'heartburn': [],
  'heart rate': ['heart rates', r'\bhr\b'],
  'hiccups': [],
  'heart failure': [],
  'heart': [],
  'hemorrhoids': [],
  'hair': [],
  'high blood pressure': [],
  'high blood sugar': [],
  'high cholesterol': ['hyperlipidemia'],
  'hives': [],
  'hypoglycemia': [],
  'hypothyroidism': ['underactive thyroid'],
  'incontinence': [],
  'indigestion': [],
  'infection': [],
  'inflammation': [],
  'inflammatory bowel disease': [r'\bibd\b'],
  'insomnia': [],
  'intercourse': [],
  'irritation': [],
  'itchiness': [],
  'itching': [],
  'line care': [],
  'low blood sugar': [],
  'low heart rate': [],
  'migraine': [],
  'mood': [],
  'mucositis': [],
  'movement disorder': [],
  'muscle spasm': [],
  'nasal congestion': [],
  'nasal dryness': [],
  'nausea': [],
  'numbness': [],
  'opioid dependence': [],
  'opioid reversal': [],
  'outbreak': [],
  'overdose': [],
  'palpitations': [],
  'panic attack': [],
  'perianal irritation': [],
  'pharyngitis': [],
  'prostate': [],
  'rash': [],
  'reflux': [],
  'respiratory distress': [],
  'respiratory depression': [],
  'restlessness': [],
  'rhinitis': [],
  'rigors': [],
  'seasonal allergies': [],
  'sedation': [],
  'seizure clusters': [],
  'seizures lasting longer than': [],
  'seizures lasting more than': [],
  'severe allergic reaction': [],
  'severe food allergies': [],
  'severe headache': [],
  'severe hypoglycemia': [],
  'severe low blood sugar': [],
  'sexual activity': [],
  'sex': [],
  'shivering': [],
  'shortness of breath': [r'\bsob\b', r's\.o\.b\.'],
  'sinus pressure': [],
  'sleep': [],
  'smoking cessation': [],
  'social situations': [],
  'sore throat': [],
  'soreness': [],
  'spasm': [],
  'stomatitis': [],
  'stroke': [],
  'swelling': [],
  'teething': [],
  'thrush': [],
  'thyroid': [],
  'tick bite': [],
  'tremor': ['tremors'],
  'ulcerative colitis': [],
  'unable to take po': [],
  'urge to smoke': [],
  'urinary burning': [],
  'urinary tract infection': [r'\buti'],
  'urinary tract irritation': [],
  'urinary tract symptoms': [],
  'vertigo': [],
  'vomiting': [],
  'weight gain': [],
  'withdrawal': ['withdrawl'],
  'wheeze': [],
  'wheezing': [],
  'wound care': [],
  'yeast infection': [],
  # less specific
  'blood pressure': [],
}

RE_INDICATION = []
for n, p in INDICATIONS.items():
  p.append(n)
  RE_INDICATION.append(r'|'.join(p))        
INDICATION_PATTERN = re.compile(r'(?P<indication>' + r'|'.join(RE_INDICATION) + r')', flags = re.I)

ADDITIONAL_INFO = {
  # take
  'take as directed': ['as directed', r'\bud\b', r'\btud\b', r'as dir\b'],
  'take on an empty stomach': [r'on(?: an)? empty stomach'],
  'take 1 hour before sexual activity': [r'(?:one|1) hour (?:before|prior to) sex(?:ual activity)?'],
  'take with food': ['with food'],
  'take with fluids': ['with fluids'],
  'take with plenty of water': [],
  'take at onset of migraine': [],
  'take after brushing teeth': ['after brushing teeth'],
  'take per package instructions': ['per package instructions'],
  'take at same time each day': [],
  'take until finished': [r'until finish(?:ed)?'],
  'take on full stomach': ['take on a full stomach'],
  'take with an antacid': [r'with(?: an)? antacid'],
  # other
  'for suspected overdose call 911': [],
  'repeat if no response in 3 minutes': [r'if no response in 3 min(?:utes) repeat'],
  'allow to dissolve': ['allow to disintegrate'],
  'do not crush, break, or chew': [],
  'do not crush or chew': ['no crushing or chewing', 'no chewing or crushing', 'do not chew or crush', 'without chewing or crushing', 'without crushing or chewing'],
  'do not crush': [],
  'do not chew': [],
  'retain in mouth as long as possible before swallowing': [],
  'gargle after each use': [],
  'rotate sites': ['rotate injection sites'],
  'may sprinkle contents of capsule on food': [],
  'shake well before each use': [],
  'shake well before use': ['shake well before using'],
  'may cause drowsiness': [],
}

LOGICAL_EXPRESSIONS = {
  'greater than or equal to': [r'\bgte\b', r'>=', r'g\.t\.e\.', r'> ='],
  'less than or equal to': [r'\blte\b', r'<=', r'l\.t\.e\.', r'< ='],
  'greater than': [r'>'],
  'less than': [r'<'],
}

# splits '1 to 2' or '1-2' or '1 or 2' into [1,2] and returns '1' as [1,None] because FHIR doesn't capture frequencyMax when frequency is q8h
def split_range(text):
  split = text.lower()
  split = re.sub(r'  ', ' ', split)
  split = re.sub(r'(?:,|mg)', '', split)
  split = re.sub(r'(?:to|or)', '-', split, flags = re.I)
  split = re.sub(r'(?<!(?:\d|\s))-(?!(?:\d|\s))', '', split) # don't split one-half, but do split on 1/2-1 and 1/2 - 1 --> convert one-half to onehalf
  split = split.split('-') 
  split = [number_text_to_int(s) for s in split]
  return [split[0], split[1]] if len(split) > 1 else [split[0], None]

# similar to split_range, but specific to frequencies
# once -> [1,None], 3-4 times -> [3,4]
def split_frequency_range(text):
  split = text
  split = re.sub(r'(?:times(?: a| per)?|time|(?<=\d|\s)x(?: a| per)?|nights|days)', '', split, flags = re.I)
  split = re.sub(r'once(?: a| per)?|a|per', '1', split, flags = re.I)
  split = re.sub(r'twice(?: a| per)?', '2', split, flags = re.I)
  split = split_range(split)
  return split

# once IndicationParser returns a string of text following "as needed for", this tries to parse a specific indication
# it first tries to find a pain-related indication, and then looks for more general indications
# TODO: expand the pain-type search to blood glucose levels (i.e. prn BG > 120) and other specific types of indications
def get_indication(indication_text):
  indication = []
  if re.search(RE_BASIC_PAIN, indication_text) != None:
    for match in re.finditer(PAIN_PATTERN, indication_text):
      pain_severity = match.group('pain_severity')
      pain_location = match.group('pain_location')
      pain_trigger = match.group('pain_trigger')
      pain_logical_expression = match.group('pain_logical_expression')
      pain_score = match.group('pain_score')
      indication.append((get_normalized(PAIN_SEVERITIES, pain_severity) + ' ' if pain_severity else '') + (get_normalized(PAIN_LOCATIONS, pain_location) + ' ' if pain_location else '') + 'pain' + (' ' + get_normalized(PAIN_TRIGGERS, pain_trigger) if pain_trigger else '') + (' score' if pain_score else '') + (' ' + get_normalized(LOGICAL_EXPRESSIONS, pain_logical_expression) if pain_logical_expression else '') + (' ' + pain_score if pain_score else ''))
  
  for match in re.finditer(INDICATION_PATTERN, indication_text):
    indication.append(get_normalized(INDICATIONS, match.group('indication')))
  
  indication = ','.join(indication)
  indication = None if indication == '' else indication
  return indication

# converts one to 1, thirty to 30, etc
def number_text_to_int(textnum):
  # convert 1 and 1/2 to 1 1/2
  # convert one and one half to one one half
  textnum = re.sub(r'(?:&\s|\band\s)', '', textnum)
  try:
    # try integer (i.e. 1)
    return int(textnum)
  except:
    try:
      # try float (i.e. 1.5)
      return float(textnum)
    except:
      try:
        # try fraction (i.e. 1 1/2 -> 1.5)
        return float(sum(Fraction(s) for s in textnum.split()))
      except:
        try:
          # not sure what would match here...
          return eval(textnum)
        except:
          try:
            # otherwise, we have text-based numbers and need to figure it out
            # TODO: make this better - re-write the core numwords function to make more sense for sigs
            #       we are never going to see the word trillion in a sig, but could definitey see "one quarter tablet"
            #       and this algorithm doesn't account for that, which is why the below is hard coded
            # NOTE: we remove & and from textnum
            # NOTE: we also convert one-half to onehalf in split_range method
            numwords = []
            fractions = [ 'half', 'third', 'quarter', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth' ]
            decimals = [ 'point one', 'point two', 'point three', 'point four', 'point five', 'point six', 'point seven', 'point eight', 'point nine' ]
            units = [ 'zero', 'one', 'two', 'three', r'four(?!teen)', 'five', r'six(?!teen|ty)', r'seven(?!teen|ty)', r'eight(?!een|y)', r'nine(?!teen|ty)', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', ]
            tens = [ 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety' ]
            
            for idx, pattern in enumerate(fractions):   numwords.append((re.compile(r'(P<multiplier>' + r'|'.join(units) + r')?' + pattern, re.I), 1 / (idx + 2)))
            for idx, pattern in enumerate(decimals):    numwords.append((re.compile(pattern, re.I), (idx + 1) / 10))
            for idx, pattern in enumerate(units):       numwords.append((re.compile('(?<!point )' + pattern + r'(?!\s*(?:' + r'|'.join(fractions) + r'))', re.I), idx))
            for idx, pattern in enumerate(tens):        numwords.append((re.compile(pattern, re.I), (idx + 2) * 10))

            number = 0
            for pattern, increment in numwords:
              if re.search(pattern, textnum):
                number += increment
            return number
          except:
            return None

# normalizes text using constant pattern groups
# pattern groups are tuples with the following format:
# (name, [pattern,...])
def get_normalized(patterns, text):
  # trim whitespace from beginning and end of string
  normalized = text.strip()
  for n, p in patterns.items():
    # normalized = re.sub(r'(?:\b' + r'|'.join(p) + r'\b)', n, text, flags=re.I)
    normalized = re.sub(r'^(?:' + r'|'.join(p) + r')$', n, text, flags=re.I)
    if normalized != text:
        break
  return normalized

#print(split_range('2.5-fifty'))
#print(get_frequency_readable(frequency=1,frequency_max=2,period=3,period_unit='day'))
#print(get_indication_(frequency=1,frequency_max=2,period=3,period_unit='day'))
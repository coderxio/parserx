from .classes.parser import *

class DoseParser(Parser):
    parser_type = 'dose'
    match_keys = ['dose', 'dose_max', 'dose_unit', 'dose_text_start', 'dose_text_end', 'dose_text', 'dose_readable']
    def normalize_pattern(self):
        dose_patterns = []
        for n, p in DOSE_UNITS.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the dose_patterns array
            dose_patterns.append(r'|'.join(p))        
        pattern = re.compile(r'(?:(?P<dose_negation>' + RE_DOSE_STRENGTH_NEGATION + r')\s?)?(?P<dose>' + RE_RANGE + r')\s?(?P<dose_unit>' + r'|'.join(dose_patterns) + r')(?!\s?\/\s?act)', flags = re.I)
        return pattern
    def normalize_match(self, match):
        # alternatively, if negation text is found before the dose, don't generate a match
        if match.group('dose_negation'):
            return None

        dose_range = split_range(match.group('dose'))
        dose, dose_max = dose_range
        dose_unit = get_normalized(DOSE_UNITS, match.group('dose_unit'))
        # convert teaspoon and tablespoon to mL
        if (dose_unit in ['teaspoon', 'tablespoon']):
            multipliers = {
                'teaspoon': 5,
                'tablespoon': 15
            }
            multiplier = multipliers[dose_unit]
            dose = dose * multiplier if dose else dose
            dose_max = dose_max * multiplier if dose_max else dose_max
            dose_unit = 'mL'
        dose_text_start, dose_text_end = match.span()
        dose_text = match[0]
        dose_readable = self.get_readable(dose=dose, dose_max=dose_max, dose_unit=dose_unit)
        return self.generate_match({'dose': dose, 'dose_max': dose_max, 'dose_unit': dose_unit, 'dose_text_start': dose_text_start, 'dose_text_end': dose_text_end, 'dose_text': dose_text, 'dose_readable': dose_readable})
    def get_readable(self, dose=None, dose_max=None, dose_unit=None):
        plural = (dose and dose > 1) or (dose_max and dose_max > 1)
        if dose_unit:
            if plural:
                dose_unit += 'e' if dose_unit[-1:] == 'h' else ''
                dose_unit += 's' if dose_unit not in ['oz','mL','L','cm'] else ''
        else:
            dose_unit = ''
        
        dose = str(dose) if dose else ''
        if dose_max:
            dose += '-' + str(dose_max)

        readable = dose + ' ' + dose_unit
        readable = readable.strip()
        return readable

class DoseOnlyParser(DoseParser):
    def normalize_pattern(self):
        method_patterns = []
        strength_unit_patterns = []
        for n, p in METHODS.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the dose_patterns array
            method_patterns.append(r'|'.join(p))        
        for n, p in STRENGTH_UNITS.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the dose_patterns array
            strength_unit_patterns.append(r'|'.join(p))        
        pattern = re.compile(r'^(?:' + r'|'.join(method_patterns) + r')?\s?(?P<dose>' + RE_RANGE + r')(?!(?:\s)?\d)(?!(?:\s)?(?:times|x))(?!\s?(?:' + r'|'.join(strength_unit_patterns) + r'))', flags = re.I)
        return pattern
    def normalize_match(self, match):
        dose_range = split_range(match.group('dose'))
        dose, dose_max = dose_range
        dose_text_start, dose_text_end = match.span()
        dose_text = match[0]
        dose_readable = self.get_readable(dose=dose, dose_max=dose_max)
        return self.generate_match({'dose': dose, 'dose_max': dose_max, 'dose_text_start': dose_text_start, 'dose_text_end': dose_text_end, 'dose_text': dose_text, 'dose_readable': dose_readable})

# NOTE: moved dose unit only BELOW dose only because prefer "2" over "tablets" from "2 po qid max dose 6 tabs"
class DoseUnitOnlyParser(DoseParser):
    def normalize_pattern(self):
        dose_patterns = []
        for n, p in DOSE_UNITS.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the dose_patterns array
            dose_patterns.append(r'|'.join(p))        
        pattern = re.compile(r'\b(?P<dose_unit>' + r'|'.join(dose_patterns) + r')\b', flags = re.I)
        return pattern
    def normalize_match(self, match):
        dose_unit = get_normalized(DOSE_UNITS, match.group('dose_unit'))
        dose_text_start, dose_text_end = match.span()
        dose_text = match[0]
        dose_readable = self.get_readable(dose_unit=dose_unit)
        return self.generate_match({'dose_unit': dose_unit, 'dose_text_start': dose_text_start, 'dose_text_end': dose_text_end, 'dose_text': dose_text, 'dose_readable': dose_readable})

class ApplyDoseUnitParser(DoseParser):
    def normalize_pattern(self):
        pattern = re.compile(r'apply', flags = re.I)
        return pattern
    def normalize_match(self, match):
        dose = 1
        dose_unit = 'application'
        dose_text_start, dose_text_end = match.span()
        dose_text = match[0]
        dose_readable = self.get_readable(dose_unit=dose_unit)
        return self.generate_match({'dose': dose, 'dose_unit': dose_unit, 'dose_text_start': dose_text_start, 'dose_text_end': dose_text_end, 'dose_text': dose_text, 'dose_readable': dose_readable})

class EachDoseUnitParser(DoseParser):
    def normalize_pattern(self):
        dose_patterns = []
        for n, p in MISCELLANEOUS_ROUTES.items():
            # add the name of the pattern to the list of matched patterns
            p.append(n)
            # and join them with a | character
            # and add them to the dose_patterns array
            dose_patterns.append(r'|'.join(p))
        pattern = re.compile(r'(' + r'|'.join(dose_patterns) + r')', flags = re.I)
        return pattern
    def normalize_match(self, match):
        dose = 1
        dose_unit = 'each'
        dose_text_start, dose_text_end = match.span()
        dose_text = match[0]
        dose_readable = self.get_readable(dose_unit=dose_unit)
        return self.generate_match({'dose': dose, 'dose_unit': dose_unit, 'dose_text_start': dose_text_start, 'dose_text_end': dose_text_end, 'dose_text': dose_text, 'dose_readable': dose_readable})


parsers = [
    DoseParser(),
    DoseOnlyParser(),
    DoseUnitOnlyParser(),
    ApplyDoseUnitParser(),
    EachDoseUnitParser(),
]

#print(DoseParser().parse('take one capsule prn nausea for 5 days'))

"""
// handle sigs like 1 qd or 1 po qd or one by mouth daily or one daily
// in these cases, we know the 'value' (i.e. 1 or one) but not the 'dose.unit' (i.e. tablet, mL, etc)
parseLoneNumericDose(sig: string): void {
    var regexRange = this.normalize.getRegexRange();
    var frequency = this.frequency.getFrequency();
    var route = this.route.getRoute();
    var index: number[] = [];
    
    frequency.map(f => index.push(f.match.index));
    route.map(r => index.push(r.match.index));
    
    // this pattern is similar to others, but doesn't list a 'unit' in the standardize function
    var p: any = {
        pattern: new RegExp('(?<!(?:no more than|do not exceed|not to exceed|\\bnmt|\\bnte)\\s*)\\**(' + regexRange + ')\\**\\s*', 'ig'),
        standardize: (match: any[]) => {
            var value = match[1].replace(/(?:to|or)/ig, '-').replace(/\s/g, '').split('-');
            var dose = value.length > 1 ? { doseRange: { low: { value: value[0] }, high: { value: value[1] } } } : { doseQuantity: { value: value[0] } }; 
            return dose;
        }
    };

    var match: any;
    while (match = p.pattern.exec(sig)) {
        // if the last character of the match is just before the start of a route or frequency
        // then add it to the list of doses
        if (index.indexOf(match.index + match[0].length) > -1) {
            this.dose.push({
                match: match,
                standardized: p.standardize(match)
            });
        }
    }
}
"""






"""
'(?:extended release|delayed release|buccal|sustained release buccal|chewable|disintegrating|enteric coated|extended release enteric coated|sublingual|vaginal)?\s*(?:oral)?\s*tablet': [],
'spray': [],
'actuation': [],
'puff': [],
'drop': [],
'bar': [],
'capsule': [],
'pad\b': [],
'patch': [],
'tape': [],
'gum': [],
'gel': [],
'lozenge': [],
'strip': [],
'film': [],
'tab(?:s)?\b': [],
'cap\b': [],
'stick'
"""
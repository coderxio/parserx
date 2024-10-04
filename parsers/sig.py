from parsers.classes.parser import *
from parsers import method, dose, strength, route, frequency, when, duration, indication, max, additional_info
import csv

# TODO: need to move all this to the main app and re-purpose the sig.py parser

# a work in progress...
# read csv: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
# general dataframe: https://pandas.pydata.org/pandas-docs/stable/reference/frame.html
# dataframe to csv: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_csv.html
# csv to sql: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_sql.html
class SigParser(Parser):
    parsers = {
        'method': method.parsers,
        'dose': dose.parsers,
        'strength': strength.parsers,
        'route': route.parsers,
        'frequency': frequency.parsers,
        'when': when.parsers,
        'duration': duration.parsers,
        'indication': indication.parsers,
        'max': max.parsers,
        'additional_info': additional_info.parsers,
    }
    # TODO: make this match_keys assignment more elegant
    #match_keys = ['original_sig_text'] + ['sig_text', 'sig_readable', 'max_dose_per_day'] + method.parsers[0].match_keys + dose.parsers[0].match_keys + strength.parsers[0].match_keys + route.parsers[0].match_keys + frequency.parsers[0].match_keys + when.parsers[0].match_keys + duration.parsers[0].match_keys + indication.parsers[0].match_keys + max.parsers[0].match_keys + additional_info.parsers[0].match_keys
    match_keys = ['sig_text', 'sig_readable', 'max_dose_per_day'] + method.parsers[0].match_keys + dose.parsers[0].match_keys + strength.parsers[0].match_keys + route.parsers[0].match_keys + frequency.parsers[0].match_keys + when.parsers[0].match_keys + duration.parsers[0].match_keys + indication.parsers[0].match_keys + max.parsers[0].match_keys + additional_info.parsers[0].match_keys
    parser_type = 'sig'

    def get_normalized_sig_text(self, sig_text):
        # standardize to lower case
        sig_text = sig_text.lower()
        # remove:
        # . if not bordered by a number (i.e. don't want to convert 2.5 to 25 or 0.5 to 05)
        # : if not bordered by a number (i.e. not 5:00 or 1:10000)
        # , ; # * " ' ( ) \t [ ] :
        sig_text = re.sub(r'(?:(?<![0-9])\.(?![0-9])|,|;|#|\*|\"|\'|\(|\)|\t|\[|\]|(?<![0-9]):(?![0-9]))', '', sig_text)
        # remove duplicate spaces, and in doing so, also trim whitespaces from around sig
        sig_text = ' '.join(sig_text.split())
        return sig_text

    def get_readable(self, match_dict, inferred_method=None, inferred_route=None, inferred_form=None):
        method = match_dict['method_readable'] or inferred_method or ''
        dose = match_dict['dose_readable'] or ''
        if match_dict['dose_unit']:
            form = ''
        else:
            form = inferred_form or ''
        strength = match_dict['strength_readable'] or ''
        route = match_dict['route_readable'] or inferred_route or ''
        frequency = match_dict['frequency_readable'] or ''
        when = match_dict['when_readable'] or ''
        duration = match_dict['duration_readable'] or ''
        indication = match_dict['indication_readable'] or ''
        max = match_dict['max_readable'] or ''
        additional_info = match_dict['additional_info_readable'] or ''

        if dose != '' and strength != '':
            strength = '(' + strength + ')'
        sig_elements = [method, dose, form, strength, route, frequency, when, duration, indication, max, additional_info]
        # join sig elements with spaces
        readable = ' '.join(sig_elements)
        # remove duplicate spaces, and in doing so, also trim whitespaces from around sig
        # this accounts for empty sig elements
        readable = ' '.join(readable.split())
        return readable

    def get_period_per_day(self, period, period_unit):
        if not period:
            return None

        if period_unit == 'hour':
            return 24 / period
        elif period_unit == 'day':
            return 1 / period
        elif period_unit == 'week':
            return 1 / (7 * period)
        elif period_unit == 'month':
            return 1 / (30 * period)
        else:
            return None
        
    def get_max_dose_per_day(self, match_dict):
        # calculate max per day from sig instructions
        frequency = match_dict['frequency_max'] or match_dict['frequency']
        period = match_dict['period']
        period_unit = get_normalized(PERIOD_UNIT, match_dict['period_unit']) if match_dict['period_unit'] else match_dict['period_unit']
        # period_per_day can be null if period_unit doesn't match hour / day / week / month
        period_per_day = self.get_period_per_day(period, period_unit)

        dose = match_dict['dose_max'] or match_dict['dose']
        dose_unit = match_dict['dose_unit'] # NOTE: moved units to strength unit instead of dose unit - eventually need to update this part to include units

        max_dose_per_day_sig = None
        if frequency and period_per_day and dose:
            max_dose_per_day_sig = frequency * period_per_day * dose

        # calculate max per day from max dose (i.e. "max daily dose = 3" or "no more than 2 per week")
        frequency_max = 1
        period_max = match_dict['max_denominator_value']
        period_unit_max = match_dict['max_denominator_unit']
        # can be null if period_unit doesn't match
        period_per_day_max = self.get_period_per_day(period_max, period_unit_max)
        
        dose_max = match_dict['max_numerator_value']
        dose_unit_max = match_dict['max_numerator_unit']

        max_dose_per_day_max = None
        if frequency_max and period_per_day_max and dose_max:
            max_dose_per_day_max = frequency_max * period_per_day_max * dose_max
        
        max_dose_per_day = None
        # if we are dealing with a complex dose unit, don't return a max_dose_per_day
        if dose_unit in EXCLUDED_MDD_DOSE_UNITS or dose_unit_max in EXCLUDED_MDD_DOSE_UNITS:
            return max_dose_per_day
        # if (at least one max dose is not null) and (the dose units match or one of the dose units is null)
        if (max_dose_per_day_sig or max_dose_per_day_max) and (dose_unit == dose_unit_max or not dose_unit or not dose_unit_max):
            # originally wrote this to choose the lowest dose per day
            # max_dose_per_day = min(d for d in [max_dose_per_day_sig, max_dose_per_day_max] if d is not None)
            # however, requirements changed to always prefer max over sig
            max_dose_per_day = max_dose_per_day_max or max_dose_per_day_sig

        return max_dose_per_day

    def parse(self, sig_text):
        match_dict = dict(self.match_dict)
        #match_dict['original_sig_text'] = sig_text
        sig_text = self.get_normalized_sig_text(sig_text)
        match_dict['sig_text'] = sig_text
        for parser_type, parsers in self.parsers.items():
            matches = []
            
            for parser in parsers:
                match = parser.parse(sig_text)
                if match:
                    matches += match
            
            if len(matches) > 1:
                # TODO: this is where we can put logic to determine the best dose / frequency / etc
                match = matches[0]
                for k, v in match.items():
                    match_dict[k] = v
            elif len(matches) == 1:
                match = matches[0]
                for k, v in match.items():
                    match_dict[k] = v
            #elif len(matches) == 0:
        match_dict['sig_readable'] = self.get_readable(match_dict)
        match_dict ['max_dose_per_day'] = self.get_max_dose_per_day(match_dict)

        # calculate admin instructions based on leftover pieces of sig
        # would need to calculate overlap in each of the match_dicts
        # in doing so, maybe also return a map of the parsed parts of the sig for use in frontend highlighting
        # i.e. 0,4|5,12|18,24
        return match_dict

    # infer method, dose_unit, and route from NDC or RXCUI
    def infer(self, match_dict, ndc=None, rxcui=None):
        sig_elements = ['method', 'dose_unit', 'route']
        #sig_elements = ['method', 'route']
        inferred = dict.fromkeys(sig_elements)
        for sig_element in sig_elements:
            inferred[sig_element] = infer_sig_element(sig_element, ndc, rxcui)
        inferred['sig_readable'] = self.get_readable(match_dict, inferred_method=inferred['method'], inferred_route=inferred['route'], inferred_form=inferred['dose_unit'])
        return inferred

    # parse a csv
    def parse_sig_csv(self, input_file='input.csv', output_file='output.csv'):
        input_folder = 'csv/'
        output_folder = input_folder + 'output/'
        csv_columns = self.match_keys
        # create an empty list to collect the data
        parsed_sigs = []
        # open the file and read through it line by line
        try:
            input_file_path = input_folder + input_file
            with open(input_file_path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                # calculate total number of rows for progress bar
                row_total = sum(1 for row in csv_reader)
                row_count = 0
                # reset csv file to beginning
                csv_file.seek(0)
                for row in csv_reader:
                    row_count += 1
                    print_progress_bar(row_count, row_total)
                    sig = row[0]
                    parsed_sig = self.parse(sig)
                    parsed_sigs.append(parsed_sig.copy())
        except IOError:
            print("I/O error")

        try:
            output_file_path = output_folder + output_file
            with open(output_file_path, 'w') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
                writer.writeheader()
                for parsed_sig in parsed_sigs:
                    writer.writerow(parsed_sig)
        except IOError:
            print("I/O error")

        return parsed_sigs

def print_progress_bar (iteration, total, prefix = 'Progress:', suffix = 'complete', decimals = 1, length = 50, fill = '█', print_end = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s (n = %s)' % (prefix, bar, percent, suffix, iteration), end = print_end)
    if iteration == total: 
        print()

#print(SigParser().infer(ndc='68788640709'))
#parsed_sigs = SigParser().parse_sig_csv()
#parsed_sig = SigParser().parse('take 1-2 tabs by mouth qid x7d prn nausea')
#print(parsed_sig)
#parsed_sigs = SigParser().parse_validate_sig_csv()
#print(parsed_sigs)

# NOTE: if no dose found, check for numbers immediately following method (i.e. take 1-2 po qid)
# NOTE: if indication overlaps something else, then end indication just before the next thing starts
# NOTE: don't forget about the actual sig text and the sequence
# NOTE: split sig by "then" occurrences for sequence
# NOTE: Github has pieces that could make a FHIR converter

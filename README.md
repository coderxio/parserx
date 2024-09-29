# 🧠 ParseRx

Modern, lightweight medication sig parser.

## Getting started

### Installation

Clone repo.

```
git clone https://github.com/coderxio/parserx.git
```

Create virtual environment within the `parserx/` directory.

```
cd parserx
python3 -m venv venv
```

### Running ParseRx

Activate virtual environment.

```
source venv/bin/activate
```

Initialize script.

```
python main.py
```

### Parse single sig

Example:

```
Enter 1 for a single sig. Enter 2 for bulk sigs via .csv file: 1
Enter sig: take 1-2 tab po qid x7d prn pain
{'sig_text': 'take 1-2 tab po qid x7d prn pain', 'sig_readable': 'take 1-2 tablets by mouth 4 times a day for 7 days as needed for pain', 'max_dose_per_day': 8.0, 'method': 'take', 'method_text_start': 0, 'method_text_end': 4, 'method_text': 'take', 'method_readable': 'take', 'dose': 1, 'dose_max': 2, 'dose_unit': 'tablet', 'dose_text_start': 5, 'dose_text_end': 12, 'dose_text': '1-2 tab', 'dose_readable': '1-2 tablets', 'strength': None, 'strength_max': None, 'strength_unit': None, 'strength_text_start': None, 'strength_text_end': None, 'strength_text': None, 'strength_readable': None, 'route': 'by mouth', 'route_text_start': 13, 'route_text_end': 15, 'route_text': 'po', 'route_readable': 'by mouth', 'frequency': 4, 'frequency_max': None, 'period': 1, 'period_max': None, 'period_unit': 'day', 'time_duration': None, 'time_duration_unit': None, 'day_of_week': None, 'time_of_day': None, 'offset': None, 'bounds': None, 'count': None, 'frequency_text_start': 16, 'frequency_text_end': 19, 'frequency_text': 'qid', 'frequency_readable': '4 times a day', 'when': None, 'when_text_start': None, 'when_text_end': None, 'when_text': None, 'when_readable': None, 'duration': 7, 'duration_max': None, 'duration_unit': 'day', 'duration_text_start': 20, 'duration_text_end': 23, 'duration_text': '7 d', 'duration_readable': 'for 7 days', 'as_needed': 1, 'indication': 'pain', 'indication_text_start': 24, 'indication_text_end': 32, 'indication_text': 'prn pain', 'indication_readable': 'as needed for pain', 'max_numerator_value': None, 'max_numerator_unit': None, 'max_denominator_value': None, 'max_denominator_unit': None, 'max_text_start': None, 'max_text_end': None, 'max_text': None, 'max_readable': None, 'additional_info': None, 'additional_info_text_start': None, 'additional_info_text_end': None, 'additional_info_text': None, 'additional_info_readable': None}
```

### Parse CSV of sigs

Example:

```
Enter 1 for a single sig. Enter 2 for bulk sigs via .csv file: 2


**********************************
Place your input file in the /csv directory.
**********************************
 > Input files are read from the /csv directory.
 > Output files are written to the /csv/output directory.

**********************************
Enter the input file name (input.csv as default) and output file name (output.csv as default), separated by a space.
input.csv output.csv
progress: |██████████████████████████████████████████████████| 100.0% complete (n = 250)
Output written to output.csv
```

## Result object components

These are the main components returned from a parsed sig.

`sig_text`

A string containing the modified sig_text from the request, converted to lower case, extraneous characters removed, and duplicate spaces converted to single spaces.

`sig_parsed`

A JSON object containing all the parsed components of the free text sig. See details of each component below.

`sig_inferred`

A JSON object containing all the inferred sig components if the request included an ndc or rxcui parameter. See details of each component below.

This entire object will only appear if a valid ndc or rxcui are included as a request parameter. If both are included, ndc will take precedence over rxcui.

`original_sig_text`

A string containing the original, un-modified sig_text from the request.

## Parsed sig components

These components are contained within `sig_parsed`.

`method`

How the medication is administered (i.e. take, inject, inhale).

`dose`

`dose_max`

`dose_unit`

How much medication patient is instructed to take based on dosage (i.e. 2 tablets, 30 units, 1-2 puffs).

Numbers represented as words in the sig will be converted to integers (i.e. “one” will be converted to 1).

`strength`

`strength_max`

`strength_unit`

How much medication the patient is instructed to take based on strength (i.e. 500 mg, 15 mL, 17 g).

NOTE: ParseRx intentionally does not parse multiple ingredient strengths (i.e. if 5/325 mg is in a sig, it will return null for strength).

`route`

Route of administration of the medication (i.e. by mouth, via inhalation, in left eye).

`frequency`

`frequency_max`

`period`

`period_max`

`period_unit`

`time_duration`

`time_duration_unit`

`day_of_week`

`time_of_day`

`when`

`offset`

`bounds`

`count`

`frequency_readable`

How often medication should be administered (i.e. every 4-6 hours, three times daily, once daily in the morning with meal).

Due to the complexity and variety of medication instructions, these elements are based off of an existing standard - FHIR Timing.

For convenience, a frequency_readable is generated to represent a human-readable representation of the sig frequency.

`duration`

`duration_max`

`duration_unit`

How long the patient is instructed to take the medication (i.e. for 7 days, for 7-10 days, for 28 days).

NOTE: this is different from days’ supply, which represents how long a given supply of medication should last.

`as_needed`

`indication`

Whether the medication should be taken “as needed” (i.e. PRN), and the specific reason the patient is taking the medication (i.e. for pain, for wheezing and shortness of breath, for insomnia).

NOTE: indication may be populated even if as_needed is false. There are chronic indications represented in sigs as well (i.e. for cholesterol, for high blood pressure, for diabetes).

`sig_reviewed_status`

This is an indicator that a pharmacist / pharmacy resident has reviewed the sig.

Depending on the review status of the sig, it will return either unreviewed, correct, incorrect, or unknown.

`sig_reviewed`

If sig_reviewed_status is unreviewed or unknown, this will be null.
Otherwise, this will return an object containing the reviewed components of the parsed sig. See details of each component below.

NOTE: ParseRx will be constantly improving, and as such, there may be multiple different versions of parsing a given sig. Each of these parsing versions will be reviewed by a pharmacist or pharmacy resident in time. If there exists a version that has a sig_reviewed_status of correct, this is the version that will be returned. Otherwise, the most recently parsed version of the sig will be returned.

IMPORTANT: Pay close attention to the sig_reviewed_status and sig_reviewed object. It is your responsibility to use this information safely.

### Inferred sig components

These components are contained within `sig_inferred`.

`method`

`dose_unit`

`route`

This entire object will only appear if a valid ndc or rxcui are included as a request parameter. If both are included, ndc will take precedence over rxcui.

Any or all of the inferred sig components may be null if it is not possible to infer them.

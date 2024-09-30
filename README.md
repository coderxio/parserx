# 🧠 ParseRx

> A modern, lightweight medication sig parser.

## Getting started

Input free text medication sigs, output discrete sig elements.
* Extract method, dose, strength, frequency, route, duration, indication, and additional info
* Calculate maximum daily dose (preferring explicit MDD in sig over maximum possible dose per day)

Medication "sigs" are the instructions you see on your prescription label - i.e. "take 1-2 tablets by mouth daily". 

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

### Parse single sig

Individual sig usage: 

```
python -m parserx take 1 tab by mouth daily
```

* Replace `take 1 tab by mouth daily` with your own sig.

Example:

```
$ python -m parserx take 1-2 tab po qid x7d prn pain
{'sig_text': 'take 1-2 tab po qid x7d prn pain', 'sig_readable': 'take 1-2 tablets by mouth 4 times a day for 7 days as needed for pain', 'max_dose_per_day': 8.0, 'method': 'take', 'method_text_start': 0, 'method_text_end': 4, 'method_text': 'take', 'method_readable': 'take', 'dose': 1, 'dose_max': 2, 'dose_unit': 'tablet', 'dose_text_start': 5, 'dose_text_end': 12, 'dose_text': '1-2 tab', 'dose_readable': '1-2 tablets', 'strength': None, 'strength_max': None, 'strength_unit': None, 'strength_text_start': None, 'strength_text_end': None, 'strength_text': None, 'strength_readable': None, 'route': 'by mouth', 'route_text_start': 13, 'route_text_end': 15, 'route_text': 'po', 'route_readable': 'by mouth', 'frequency': 4, 'frequency_max': None, 'period': 1, 'period_max': None, 'period_unit': 'day', 'time_duration': None, 'time_duration_unit': None, 'day_of_week': None, 'time_of_day': None, 'offset': None, 'bounds': None, 'count': None, 'frequency_text_start': 16, 'frequency_text_end': 19, 'frequency_text': 'qid', 'frequency_readable': '4 times a day', 'when': None, 'when_text_start': None, 'when_text_end': None, 'when_text': None, 'when_readable': None, 'duration': 7, 'duration_max': None, 'duration_unit': 'day', 'duration_text_start': 20, 'duration_text_end': 23, 'duration_text': '7 d', 'duration_readable': 'for 7 days', 'as_needed': 1, 'indication': 'pain', 'indication_text_start': 24, 'indication_text_end': 32, 'indication_text': 'prn pain', 'indication_readable': 'as needed for pain', 'max_numerator_value': None, 'max_numerator_unit': None, 'max_denominator_value': None, 'max_denominator_unit': None, 'max_text_start': None, 'max_text_end': None, 'max_text': None, 'max_readable': None, 'additional_info': None, 'additional_info_text_start': None, 'additional_info_text_end': None, 'additional_info_text': None, 'additional_info_readable': None}
```

In this example, "take 1-2 tab po qid x7d prn pain" is interepreted by ParseRx as "take 1-2 tablets by mouth 4 times a day for 7 days as needed for pain".

* You can see each individual component that comprises that sig, as well as the start and end characters within the original sig.

### Parse CSV of sigs

Bulk sig usage:  

```
python -m parserx --b input.csv output.csv
```

* Use the `--b` flag for bulk parsing of sigs in CSV files.
* Replace input.csv with the name of your input file (needs to be in the /csv directory).
* Replace output.csv with the desired name of your output file (will be in the /csv/output directory).
* Separate input and output file names with a space.

Example:

```
$ python -m parserx --b input.csv output.csv
Progress: |██████████████████████████████████████████████████| 100.0% complete (n = 250)
Output written to output.csv.
```

![image](https://github.com/user-attachments/assets/fc5e5e21-0f80-4688-9e55-f631e1caf3cc)

## Parsed sig components

### Text

`sig_text`

A string containing the modified sig_text from the request, converted to lower case, extraneous characters removed, and duplicate spaces converted to single spaces.

`sig_readable`

A human-readable version of the parsed sig for quick and easy validation.

### Method

`method`

How the medication is administered (i.e. take, inject, inhale).

### Dose

`dose`

`dose_max`

`dose_unit`

How much medication patient is instructed to take based on dosage (i.e. 2 tablets, 30 units, 1-2 puffs).

Numbers represented as words in the sig will be converted to integers (i.e. “one” will be converted to 1).

### Strength

`strength`

`strength_max`

`strength_unit`

How much medication the patient is instructed to take based on strength (i.e. 500 mg, 15 mL, 17 g).

NOTE: ParseRx intentionally does not parse multiple ingredient strengths (i.e. if 5/325 mg is in a sig, it will return null for strength).

### Route

`route`

Route of administration of the medication (i.e. by mouth, via inhalation, in left eye).

### Frequency

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

### Duration

`duration`

`duration_max`

`duration_unit`

How long the patient is instructed to take the medication (i.e. for 7 days, for 7-10 days, for 28 days).

NOTE: this is different from days’ supply, which represents how long a given supply of medication should last.

### Indication / PRN

`as_needed`

`indication`

Whether the medication should be taken “as needed” (i.e. PRN), and the specific reason the patient is taking the medication (i.e. for pain, for wheezing and shortness of breath, for insomnia).

NOTE: indication may be populated even if as_needed is false. There are chronic indications represented in sigs as well (i.e. for cholesterol, for high blood pressure, for diabetes).

### Maximum daily dose

`max_dose_per_day`

`max_numerator_value`

`max_numerator_unit`

`max_denominator_value`

`max_deniminator_unit`

Max numerator and denominator elements are extracted from text explicitly stated in the sig (i.e. if a prescriber writes mdd or nte). 

Max dose per day looks to both the maximum dose possible per the sig instructions and any explicit mdd or or nte directions, preferring the mdd or nte directions if present.

Examples:

* take 1 tab every 6 hours mdd 3/d -> max_dose_per_day should be 3, max numerator/denominator should have values
* take 1 tab every 6 hours -> max_dose_per_day should be 4, max numerator/denominator should not have values

### Additional info

`additional_info`

Extra instructions such as "take with food" - things that might be on auxillary labels on a prescription bottle.

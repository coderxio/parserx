# 🧠 ParseRx

Modern, lightweight medication sig parser.

## Getting started

### Installation

Clone repo and cd into `parserx` directory.

```
git clone https://github.com/coderxio/parserx.git
cd parserx
```

Create virtual environment.

```
python3 -m venv venv
```

Activate virtual environment.

```
source venv/bin/activate
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

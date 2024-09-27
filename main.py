from parsers.sig import *

parsed_sig = SigParser().parse('take 1-2 tabs by mouth qid x7d prn nausea')
print(parsed_sig)
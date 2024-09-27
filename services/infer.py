import csv

# converts a csv file to a list of dicts
def csv_to_dict_list(file_name):
    file_path='services/'
    csv_dict_list = []
    with open(file_path + file_name + '.csv', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            csv_dict_list.append(row)
    return csv_dict_list

PACKAGE_NDC_TO_DOSE_FORM_RXCUI = csv_to_dict_list('package_ndc_to_dose_form_rxcui')
PRODUCT_RXCUI_TO_DOSE_FORM_RXCUI = csv_to_dict_list('product_rxcui_to_dose_form_rxcui')
DOSE_FORM_RXCUI_TO_METHOD_DOSE_UNIT_AND_ROUTE = csv_to_dict_list('dose_form_rxcui_to_method_dose_unit_and_route')

def product_id_to_dose_form_rxcui(ndc=None, rxcui=None):
    if ndc:
        result = [df for df in PACKAGE_NDC_TO_DOSE_FORM_RXCUI if df['ndc'] == ndc]
        if len(result) > 0:
            return result[0]['dose_form_rxcui']
    elif rxcui:
        result = [r for r in PRODUCT_RXCUI_TO_DOSE_FORM_RXCUI if r['clinical_product_rxcui'] == rxcui]
        if len(result) > 0:
            return result[0]['dose_form_rxcui']

def dose_form_rxcui_to_sig_element(dose_form_rxcui, sig_element):
    if sig_element in ('method', 'dose_unit', 'route'):
        result = [r for r in DOSE_FORM_RXCUI_TO_METHOD_DOSE_UNIT_AND_ROUTE if r['dose_form_rxcui'] == dose_form_rxcui]
        if len(result) > 0 and result[0][sig_element] != '':
            return result[0][sig_element]

def infer_sig_element(sig_element, ndc=None, rxcui=None):
    dose_form_rxcui = product_id_to_dose_form_rxcui(ndc, rxcui)
    if dose_form_rxcui:
        return dose_form_rxcui_to_sig_element(dose_form_rxcui, sig_element)

#print(product_id_to_dose_form_rxcui())
#print(dose_form_rxcui_to_sig_element('316964', 'method'))
#print(infer_sig_element('method', rxcui='104894'))
#print(PACKAGE_NDC_TO_DOSE_FORM_RXCUI[0])
#print(PRODUCT_RXCUI_TO_DOSE_FORM_RXCUI[0])
#print(DOSE_FORM_RXCUI_TO_METHOD_DOSE_UNIT_AND_ROUTE[0])
import pandas as pd
from datetime import date 
from currency_converter import CurrencyConverter


def _clean_value(input) -> tuple[str, str]:
    
    input = str(input).lower().replace("eur ii.2.", "eur").replace("including vat . vat rate (%) 20,00", "").replace("including vat . vat rate (%) 20", "")\
        .replace("excluding vat : ", "").replace("excluding vat", "").strip()
    currencies = ["EUR", "USD", "CHF", "RMB", "HUF", "RON", "HRK", "PLN", "RSD"]

    if input == "nan":
        return (0, "EUR")
    elif _check_currencies(input, currencies):
        return _get_currency(input, currencies)
    else:
        return (input, "unknown")
    
def _check_currencies(input, currencies):
    return any([input.endswith(c.lower()) for c in currencies])

def _get_currency(input, currencies):
    
    c = CurrencyConverter() #moved from outside function

    for curr in currencies:
        if input.endswith(curr.lower()):
            currency = curr
            val = input[:-3].strip()
            val = float(str(val).replace(" ", "").replace(",", "."))
            if curr != "EUR":
                eur_value = c.convert(val, curr, 'EUR')
                return (eur_value, "EUR")
            else:
                return (val, currency)

def _check_for_errors(cleaned_contract_values):
    
    still = cleaned_contract_values.apply(lambda x: x[1] != "EUR")
    fails = cleaned_contract_values.loc[still[still == True].index]
    msg = "Errors found: {}".format(len(fails))
    print(msg)
    return msg

def _augment_keywords(keywords):

    keywords = list(map(lambda x: x.lower(), keywords))
    
    additional_keywords = []
    separators = [",", ";", ".", "\n", "\t"]
    for w in keywords:
        if w.startswith(" "):
            for sep in separators:
                additional_keywords.append(sep + w[1:])
    keywords = keywords + additional_keywords

    return keywords

def _find_category(keywords : list, input : str) -> bool:

    keywords = _augment_keywords(keywords)
    input = input.lower()

    for w in keywords:
        if w in input:
            return True
        else:
            pass
    return False

def _check_all_cols(keywords, row, cols):
    col_res = []
    for col in cols:
        col_res.append(_find_category(keywords, str(row.loc[col])))
    return any(col_res)

def _find_approx_value(combined_df : pd.DataFrame) -> pd.DataFrame:

    #### ugly fix for 100 broken ones in Romania
    complex_value = combined_df["Lot_Value"].apply(lambda x: "approximate value" in str(x).lower())
    problems = complex_value[complex_value == True].index
    combined_df.loc[problems, "Lot_Value"] = combined_df["Lot_Value"].loc[problems].apply(lambda x: str(x).lower().split("approximate value of the framework agreements :")[1])

    return combined_df

def prepare_for_segmentation(combined_df : pd.DataFrame) -> pd.DataFrame:

    cleaned_contract_values = combined_df.apply(lambda x: _clean_value(str(x.loc["Lot_Value"])), axis = 1)

    combined_df = _find_approx_value(combined_df) # imperfect debugging

    _check_for_errors(cleaned_contract_values)

    combined_df["Contract Value"] = cleaned_contract_values.apply(lambda x: x[0]) # not readable enough and this function is rly bad -> TODO: refactor
    combined_df["Contract Value Currency"] = cleaned_contract_values.apply(lambda x: x[1])

    return combined_df

def do_simple_segmentation(combined_df : pd.DataFrame, dq_info : bool = True) -> pd.DataFrame:
    microscopy_keywords = ["microscope", "mikroskop", "microscop", "mikroszkop"]
    em = ["Elektron", "Elektronen", "electron", "dualbeam", "dual-beam", "dual beam" "thermofisher", "bruker", "hitachi", "joel ", "tescan", " fei "]
    widefield_a = ["3d imaging", " 3d", "laser scan", "scan", "lightsheet", "lichtblatt", "zoom", "konfokal", "confocal", "light-sheet", "light sheet", "photon", " invers", "high-content-screen", "high content screen", "cLSM", "super resolution", "spinning disk", "spinning disc"]
    widefield_c = ["routine", "labormi", " invers", "stereo", "tirf", "olympus"]
    exclude = ["HNO", " ENT", "ORL", "otorhino", "laryngo", "op mi", "operationsmikro", "laborgerät", "atomic force", "rastertunnel", "raster tunnel", "transmission electron", "transmissionselektro", "rasterkraft"]
    categories = [microscopy_keywords, em, widefield_a, widefield_c, exclude]

    category_names = ["Microscopy", "Electron Microscopy", "Widefield A", "Widefield C", "Exclude"]
    for cat_index in range(len(categories)):
        cat = categories[cat_index]
        cat_name = category_names[cat_index]
        combined_df[cat_name] = combined_df.apply(lambda x: _check_all_cols(cat, x, combined_df.columns), axis = 1)

    if dq_info:
        print("Microscopy Tenders found: {}".format(combined_df[combined_df["Microscopy"] == True].shape[0]))
    
    return combined_df

def write_to_csv(combined_df : pd.DataFrame, project : str) -> None:
    d = date.today().strftime('%d_%m_%Y')
    combined_df.to_csv("Combined_df_{date}_{project}_segmented.csv".format(date = d, project = project), encoding = "utf-8")
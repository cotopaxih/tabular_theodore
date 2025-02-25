import pandas as pd
import os
from datetime import date
from ..utils import parse_buyer, parse_section, parse_nonroman_winner, get_proc_sections, get_lot_sections

def parse_non_roman_blocks(df_non_roman):
    """
    Empirically useful column names used in imported functions to get relevant parts from fields that likely contain them 
    """

    header_list = ["Official name", "Postal address", "Town", "NUTS code", "Postal code", "Country", "Contact person", "E-mail", "Telephone", "Internet address(es)", "Type of the contracting authority", "Main activity", "Email", "Legal type of the buyer", "Activity of the contracting authority", "Fax", "Internet address", "The contractor is an SME"]

    ##########################

    proc_fields = ["1.  Description", "1.1.  Type of procedure", "1.3.  Information about a framework agreement or a dynamic purchasing system", "1.8.  Information about the Government Procurement Agreement (GPA)", "2.  Administrative information", "2.1.  Previous publication concerning this procedure", "2.8.  Information about termination of dynamic purchasing system", "2.9.  Information about termination of call for competition"]
    # Not all fields were checked for this section, some new additions are included in the variable non_roman_proc_f below" 
    non_roman_proc_f = ["The procedure is accelerated", "Purpose", "Main nature of the contract", "Main classification \xa0 ( cpv )", "General information", "Legal basis", "Place of performance", "Country", "Procedure identifier", "Title", "Internal identifier", "Value", "Previous notice", "Additional classification \xa0 ( cpv )"]
    proc_fields_unnumbered = [" ".join(i.split()[1:]) for i in proc_fields] + non_roman_proc_f

    ##########################

    lot_field_list_unnumbered = ['Scope of the procurement', 'Title', 'Main CPV code', 'Type of contract', 'Short description', 'Information about lots', 'Total value of the procurement', 'Description', 'Title', 'Additional CPV code(s)', 'Place of performance', 'Description of the procurement', 'Award criteria', 'Information about options', 'Information about European Union funds', 'Additional information', 'Type of contract and place of performance or delivery', 'Information about a framework agreement', 'Information about framework agreement', 'CPV code(s)', 'Information about the Government Procurement Agreement (GPA)', 'Information about the dynamic purchasing system', 'Electronic auction', 'Further information, mediation and review', 'Date of the conclusion of the contract', 'Review organisation', 'TED eSender', 'Maximum renewals', 'Value', 'Estimated value excluding VAT', 'Organisation whose budget is used to pay for the contract', 'Organisation executing the payment', 'General information', 'The procurement is covered by the Government Procurement Agreement (GPA)', 'Terms of procurement', 'Information about review deadlines', 'Options', 'Renewal', 'Strategic procurement', 'Estimated duration', 'Information about previous notices', 'Identifier of the previous notice', 'Identifier of the part of the previous notice', 'The buyer reserves the right for additional purchases from the contractor, as described here', 'Total value of the contract/lot']
    # Description field may appear multiple times (not read anyway??)

    more_lot_fields= ["Internal identifier", "Purpose", "Main nature of the contract", "Main classification \xa0 ( cpv )", "Additional classification \xa0 ( cpv )", "Main classification ( cpv )", "Main classification( cpv )", "Main classification (cpv)", "Award Criteria", "Techniques", "Framework Agreement","Framework agreement", "Additional classification ( cpv )"]
    lot_fields = lot_field_list_unnumbered + more_lot_fields

    ##########################

    res_field_names = ["Value of all contracts awarded in this notice", "Result lot ldentifier", "Winner selection status"]
    key_sections612 = ["Information about winners", "Tender", "Contract information"]
    winner_fields = ["Official name"]
    tender_fields = ["Rank in the list of winners","The tender was ranked", "Value of the result", "Identifier of lot or group of lots", "Tender identifier", "Concession value", "The tender is a variant"]
    contract_info_fields = ["The contract is awarded within a framework agreement", "Date of the conclusion of the contract", "Date on which the winner was chosen", "Identifier of the contract", "Title"]
    all_fields = res_field_names + key_sections612 + winner_fields + tender_fields + contract_info_fields

    ##########################

    other_fields = ["Notice information", "Notice identifier/version", "Form type", "Notice type", "Notice subtype", "Notice dispatch date","Publication information", "Notice publication number", "OJ S issue number", "Publication date"]

    buyer_parsed = df_non_roman["Buyer"].apply(lambda x: parse_buyer(x, header_list) if "Official name :" in str(x) else "NOT FOUND")
    procedure_parsed = df_non_roman["Procedure"].apply(lambda s: parse_section(s, proc_fields_unnumbered, get_proc_sections(s)))
    res_parsed = df_non_roman["Results_long"].apply(lambda s: parse_nonroman_winner(s, all_fields))
    lot_parsed = df_non_roman["Lot"].apply(lambda s: parse_section(s, lot_fields, get_lot_sections(s)))
    other_parsed = df_non_roman["Other"].apply(lambda s: parse_section(s, other_fields, []))

    parsed_parts = [buyer_parsed, procedure_parsed, res_parsed, lot_parsed, other_parsed]
    prefixes = ["Buyer", "Procedure", "Results", "Lot", "Other"]
    named_parsed_parts = zip(prefixes, parsed_parts)

    return named_parsed_parts

def combine_non_roman(named_parsed_parts):
    """
    Creating a single usable dataset

    params:
    named_parsed_parts: parts zipped together with prefixes used to identify them in the dataset 
    """

    full_df = pd.DataFrame()
    for prefix, data in named_parsed_parts:
        data = data.apply(pd.Series)
        data.columns = [prefix + "_" + c for c in data.columns]
        full_df = pd.concat([full_df, data], axis = 1)
    return full_df

def persist_non_roman_df(full_df: pd.DataFrame, output_dir : str, project: str) -> None:
    """
    Save the dataset as a CSV

    output_dir : the folder where the parsed table should be saved
    """ 
    orig_dir = os.getcwd()
    os.chdir(output_dir)
    if "nr" not in os.listdir():
        os.mkdir("nr")
    d = date.today().strftime('%d_%m_%Y')
    full_df.to_csv("{dir}/nr/TED_non_romans_df_{date}_{project}.csv".format(dir = output_dir, date = d, project = project), encoding = "utf-8")

    os.chdir(orig_dir)

def full_non_roman_parser(df_non_roman : pd.DataFrame, output_dir : str, project : str, save_as_csv : bool = True) -> pd.DataFrame: # TODO improve this function by using piping!
    """
    Orchestrator for parsing non-roman-style blocks which already contain the notice from the raw page

    params:
    df: pandas df collecting the notices from raw html pages for non_romans
    output_dir : the folder where the parsed table should be saved
    project: the name of the project, such as ROU, to be used for naming the files
    save_as_csv: Do you need the file saved or just returned by the function

    returns:
    full_df: parsed dataframe for non_romans
    """
    named_parsed_parts = parse_non_roman_blocks(df_non_roman)
    full_df = combine_non_roman(named_parsed_parts)

    if save_as_csv:
        persist_non_roman_df(full_df, output_dir, project)
    
    return full_df
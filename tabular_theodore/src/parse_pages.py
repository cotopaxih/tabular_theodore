import pandas as pd
from bs4 import BeautifulSoup
import glob
import os

def extract_summary_block(soup):
    """
    Get the summary of TED notices
    """
    try:
        summary_ugly = soup.find("div", {"id" : "summary-content"}).getText(" ")
    except:
        try:
            summary_ugly = soup.find("div", {"id" : "summary-content"}).find_next_sibling("div").getText(" ")
        except:
            summary_ugly = "Not found"
    return summary_ugly

def extract_notice_block(soup):
    """
    Get the entire relevant part of TED pages
    """
    try:
        notice_ugly = soup.find("div", {"id" : "notice-content"}).getText(" ")
    except:
        try:
            notice_ugly = soup.find("div", {"id" : "notice-content"}).find_next_sibling("div").getText(" ")
        except:
            notice_ugly = "Not found"
    return notice_ugly

def check_ending(directory):
    """
    Make sure that the path ends in a slash to avoid errors with glob
    """
    directory = str(directory).replace("\\", "/")
    if directory.endswith("/"):
        return directory
    else:
        return directory + "/"

def prepare_raw_dir(raw_directory : str, scrape_date : str):
    """
    Helper to follow folder structure
    """
    raw_directory = check_ending(raw_directory)
    raw_directory2 = raw_directory + scrape_date + "/"

    return raw_directory2

def prepare_notice_dir(notice_dir : str, project : str) -> str:
    """
    Helper to follow old folder structure
    """
    output_dir = check_ending(notice_dir)

    if project not in os.listdir(output_dir):
        orig_dir = os.getcwd()
        os.chdir(output_dir)
        os.mkdir(project)
        os.chdir(output_dir + project + "/")
        os.mkdir("unparsed raw pages")
        os.mkdir("parsed raw pages")
        os.mkdir("parsed tables")
        os.chdir(orig_dir)
    output_dir = output_dir + project + "/"

    return output_dir

def prepare_notice_dir2(notice_dir : str) -> str:
    """
    Helper to follow nicer folder structure
    """
    return check_ending(notice_dir)

def prepare_notice_folders(raw_directory : str, output_dir : str, scrape_date : str, project : str):

    raw_directory2 = prepare_raw_dir(raw_directory, scrape_date)
    output_dir = prepare_notice_dir2(output_dir)#, scrape_date, project)

    return raw_directory2, output_dir
    
# raw_directory2 = 'c:/Users/OSBPAKSI/Carl Zeiss AG/Data & Analytics AT CH SEE - Data Projects/01_Projects/Web Scraper/01_Data/Tenders/raw pages/19_1_2025/'
# output_dir = 'c:/Users/OSBPAKSI/Carl Zeiss AG/Data & Analytics AT CH SEE - Data Projects/01_Projects/Web Scraper/01_Data/Tenders/parsed ugly/'
def parse_notice_from_page(raw_directory : str, output_dir : str, scrape_date : str, project : str) -> None:
    """
    Extract the relevant contents of html pages from TED

    params:
    raw_directory: the folder in which full html pages are stored for each date
    output_dir: the folder in which parsed CSV outputs are stored for each project
    scrape_date: dd_mm_yyyy as a string used for subfolders in the raw dict 
    project: the folder in the output directory where parsed files for the project are stored
    """
    raw_directory, output_dir = prepare_notice_folders(raw_directory, output_dir, scrape_date, project)

    raw_files = raw_directory + '*.txt'
    txt_files = glob.glob(raw_files)
    result_dict = dict()
    # Loop through each CSV file and append its contents to the combined dataframe
    for txt_file in txt_files:  
        inner_dict = dict()  
        with open(txt_file, "r", encoding ="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser") 
            notice_raw = extract_notice_block(soup)
            inner_dict["Notice"] = notice_raw
            summary_raw = extract_summary_block(soup)
            inner_dict["Summary"] = summary_raw
        short_name = txt_file.split("\\")[-1]
        result_dict[short_name] = inner_dict

    output_file = output_dir + "parse_{}_{}.csv".format(scrape_date, project)
    pd.DataFrame(result_dict).to_csv(output_file, encoding = "utf-8")

    return result_dict

def parse_notices_from_pages(raw_directory : str, output_dir : str, scrape_dates : list, project : str) -> None:
    """
    Extract the relevant contents of html pages from TED

    params:
    raw_directory: the folder in which full html pages are stored for each date
    output_dir: the folder in which parsed CSV outputs are stored for each project
    scrape_dates: list of string in dd_mm_yyyy format used for subfolders in the raw dict
    project: the folder in the output directory where parsed files for the project are stored
    """

    for date in scrape_dates:
        parse_notice_from_page(raw_directory = raw_directory, 
                        output_dir = output_dir,
                        scrape_date = date, 
                        project = project)
import os
import pandas as pd
import time
from datetime import date
from selenium import webdriver 
from selenium.webdriver.common.by import By
import json

def _handle_cookies(browser, url):
    """
    Click on the agree to cookie use button

    params:
    browser: webdriver browser object
    url: the link to the page where we want to work
    """

    browser.get(url)
    time.sleep(10)
    cookies_rejection_xpath = "/html/body/div[1]/div/div/div[2]/a[2]"

    try:
        browser.find_element(By.XPATH, cookies_rejection_xpath).click()
    except:
        print("Oopsie, somebody has eaten all the cookies")

def _write_file(parent_directory, link, html) -> None:
    """
    Write the file to a folder with today's date
    Structure: Austria > unparsed raw pages > 05_01_2025 

    params:
    parent_directory: folder in which the project is # TODO eliminate the need for this by using the project argument somehow
    link: url containing the TED ID
    html: the entire unparsed page
    """
    folder_name = date.today().strftime('%d_%m_%Y')             ##### str(date.today().day) + "_" + str(date.today().month) + "_" + str(date.today().year) + "/"
    #parent_directory = "c:/Users/OSBPAKSI/Carl Zeiss AG/Data & Analytics AT CH SEE - Data Projects/01_Projects/Web Scraper/01_Data/Tenders/raw pages/" #TODO: change to refactored structure and folder -> use relative paths?
    output_directory = os.path.join(parent_directory, folder_name)  
    
    if folder_name.replace("/","") not in os.listdir(parent_directory):
        os.mkdir(output_directory) 
    if not output_directory.endswith("/"):
        output_directory = output_directory + "/"

    output_filename = output_directory + "html_" + link.split("/")[-1] + ".txt"

    with open(output_filename, "w", encoding = "utf-8") as f:
        f.write(html)

def get_urls(excel_path : str) -> list:
    """
    Get urls to TED from Excel file (obtained through saving all results with a single attribute)
    """
    df = pd.read_excel(excel_path, sheet_name="search_results_title") 
    full_url_list = df["Notice publication number"].apply(lambda x: "https://ted.europa.eu/en/notice/-/detail/" + str(x))

    return list(full_url_list)


def scrape(full_url_list : list, output_directory : str, headless : bool, chunksize : int = 1500) -> list:

    """
    Visit the pages and save the html with short breaks, sequentially

    params:
    full_url_list: object containing all links which need to be scraped
    output_directory: the folder in which the raw pages should be stored
    headless: should the browser be visible or run in the background
    chunksize: the website refuses to serve queries after a while, 1500 pages taking around 3 hours seem reliable (3 for testing)

    returns:
    remaining_urls: a list of the urls which did not fit in the current chunk
    """

    os.environ['WDM_SSL_VERIFY'] = '0'
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-search-engine-choice-screen")
    if headless:
        options.add_argument("--headless=new")
    browser = webdriver.Chrome(options=options)

    # The main url is not scraped, just serves as an entry point
    main_url = "https://ted.europa.eu/en/search/result?classification-cpv=38000000"
    _handle_cookies(browser, main_url)

    if len(full_url_list) > 0:
        current_chunk = full_url_list[ :chunksize]
        remaining_urls = full_url_list[chunksize: ]
        for link in current_chunk:

            browser.get(link)
            time.sleep(4)
            try:
                html = browser.page_source
            except:
                print("Oopsie, saving " + link + " failed!")

            try:                
                _write_file(output_directory, link, html)
            except:
                print("Oopsie, writing " + link + " failed!")
            time.sleep(2)

        return remaining_urls
    
    else:
        return [] 
    
def filtered_scrape(full_url_list : list, output_directory : str, headless : bool, kw : list, chunksize : int = 1500) -> list:

    """
    Visit the pages and save the html with short breaks, sequentially

    params:
    full_url_list: object containing all links which need to be scraped
    output_directory: the folder in which the raw pages should be stored
    headless: should the browser be visible or run in the background
    chunksize: the website refuses to serve queries after a while, 1500 pages taking around 3 hours seem reliable (3 for testing)

    returns:
    remaining_urls: a list of the urls which did not fit in the current chunk
    """

    os.environ['WDM_SSL_VERIFY'] = '0'
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-search-engine-choice-screen")
    if headless:
        options.add_argument("--headless=new")
    browser = webdriver.Chrome(options=options)

    # The main url is not scraped, just serves as an entry point
    main_url = "https://ted.europa.eu/en/search/result?classification-cpv=38000000"
    _handle_cookies(browser, main_url)

    if len(full_url_list) > 0:
        current_chunk = full_url_list[ :chunksize]
        remaining_urls = full_url_list[chunksize: ]
        for link in current_chunk:

            browser.get(link)
            time.sleep(4)
            try:
                html = browser.page_source
            except:
                print("Oopsie, saving " + link + " failed!")

            try:     
                if _filter_for_keywords(html, kw):           
                    _write_file(output_directory, link, html)
            except:
                print("Oopsie, writing " + link + " failed!")
            time.sleep(2)

        return remaining_urls
    
    else:
        return [] 
    
def _filter_for_keywords(text : str, kws : list) -> bool:
    """
    Check for the presence of keywords in text 

    params:
    text: body of text such as a full html page
    kws: keywords we would like to check for, augmented a bit

    returns:
    bool: True if at least one keyword appears in the text (not case-sensitive) # TODO extend for case-sensitivity
    """

    keywords_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'keywords.json')
    with open(keywords_file_path, 'r') as file:
        aug_kw_collection = json.load(file)

    all_kw = []
    for kw in kws:
        all_kw = all_kw + aug_kw_collection.get(kw, [])
        if kw not in all_kw:
            all_kw.append(kw)
    
    text2 = text.lower()
    for kw in all_kw:
        if kw in text2:
            return True 
    
    return False    
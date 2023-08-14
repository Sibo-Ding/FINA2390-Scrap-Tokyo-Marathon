# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 20:41:48 2022

@author: Sibo Ding
"""

'''
This code scrapes Tokyo Marathon 2021 Results.
Can input certain search criteria.
Approximate 7 hours to scrape all results.
An Easter egg in the description of search criteria.

References about XPath:
https://medium.com/pythoneers/web-scraping-using-selenium-python-6c511258ab50
https://www.guru99.com/xpath-selenium.html
https://devhints.io/xpath
https://www.w3schools.com/xml/xpath_syntax.asp
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
import pandas as pd
import time

'''
Below is function to fill search criteria:
1. Race Category: Select 1 item from the following list:
['', 'Elite Semi-Elite Marathon Men', 'Elite Semi-Elite Marathon Women',
 'General Marathon Men', 'General Marathon Women',
 'Marathon Wheelchair Men', 'Marathon Wheelchair Women',
 '10km Wheelchair Men', '10km Wheelchair Women',
 '10km Visually Impaired Men', '10km Visually Impaired Women', 
 '10km Intellectually Challenged Men', '10km Intellectually Challenged Women',
 '10km Organ Transplant Recipients Men', '10km Organ Transplant Recipients Women',
 '10km Junior & Youth Men', '10km Junior & Youth Women']
2. Bib: Input anything or ''
3. Name: Input anything or ''
4. Age: Select 1 item from the following list:
['', '16-19', '20-24', '25-29', '30-34' ,'35-39', '40-44', '45-49',
 '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80+']
5. Sex: Input a list containing 'Men' or 'Women' or both or neither
6. Nationality: Input 1 ISO 3-letter country code or ''

E.g. {'Race Category': 'General Marathon Women',
      'Bib': '', 'Name': '小林 緑子', 'Age': '', 'Sex': ['Women'],
      'Nationality': 'JPN'}
If all search criteria are empty, it will scrape all results.
'''
dict_search_criteria = {'Race Category': '10km Organ Transplant Recipients Men', 
                        'Bib': '', 'Name': '', 'Age': '', 'Sex': [],
                        'Nationality': ''}

# Function to fill search criteria
# dict_search_criteria: a dictionary containing all search criteria
def search(dict_search_criteria):
    # https://iqss.github.io/dss-webscrape/filling-in-web-forms.html
    # https://jzchangmark.wordpress.com/2015/03/05/%E9%80%8F%E9%81%8E-selenium-%E6%93%8D%E4%BD%9C%E4%B8%8B%E6%8B%89%E5%BC%8F%E9%81%B8%E5%96%AE-select/
    # Because the website contains Japanese characters in Race Category and Age,
    # create a list of selections in English corresponding to the website by index
    list_category = [
        '', 'Elite Semi-Elite Marathon Men', 'Elite Semi-Elite Marathon Women',
        'General Marathon Men', 'General Marathon Women',
        'Marathon Wheelchair Men', 'Marathon Wheelchair Women',
        '10km Wheelchair Men', '10km Wheelchair Women',
        '10km Visually Impaired Men', '10km Visually Impaired Women', 
        '10km Intellectually Challenged Men', '10km Intellectually Challenged Women',
        '10km Organ Transplant Recipients Men', '10km Organ Transplant Recipients Women',
        '10km Junior & Youth Men', '10km Junior & Youth Women']
    category_dropdown = Select(browser.find_element_by_id('category'))
    category_dropdown.select_by_index(
        list_category.index(dict_search_criteria['Race Category']))
    
    # Fill Bib and Name using send_keys
    browser.find_element_by_id('number').send_keys(dict_search_criteria['Bib'])
    
    browser.find_element_by_id('name').send_keys(dict_search_criteria['Name'])
    
    list_age = ['', '16-19', '20-24', '25-29', '30-34' ,'35-39', '40-44',
                '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80+']
    age_dropdown = Select(browser.find_element_by_id('age'))
    age_dropdown.select_by_index(list_age.index(dict_search_criteria['Age']))
    
    # A list containing 'Men' or 'Women' or both or neither
    if 'Men' in dict_search_criteria['Sex']:
        browser.find_element_by_id('sex_m').click()
    if 'Women' in dict_search_criteria['Sex']:
        browser.find_element_by_id('sex_f').click()
    
    # The value of Nationality is ISO 3-letter country code
    country_dropdown = Select(browser.find_element_by_id('country'))
    country_dropdown.select_by_value(dict_search_criteria['Nationality'])


# Function to scrape individual player info
def player():
    list_id = []  # Save individual player info into a temporary list
    # Scrape "Overall Place", "Bib", "Name"
    for i in range(1, 4):
        data1 = browser.find_element_by_xpath \
            (f'//div[@class="cont3"]/table[1]/tbody/tr[2]/td[{i}]')
        list_id.append(data1.text)
            
    # Scrape "Race Category", "Category Place"; "Age", "Age Place";
    # "Sex", "Gender Place"; "Nationality", "Nationality Place"
    for i in range(1, 5):
        for j in range(1, 3):
            data2 = browser.find_element_by_xpath \
                (f'//div[@class="cont3"]/table[2]/tbody/tr[{i}]/td[{j}]')
            list_id.append(data2.text)
    
    # Scrape "Time(net)", "Time(gross)"
    try:  # Japanese player has row 7
        browser.find_element_by_xpath \
            ('//div[@class="cont3"]/table[2]/tbody/tr[7]/td')
        for i in range(6, 8):  # Scrape row 6 and 7
            data3 = browser.find_element_by_xpath \
                (f'//div[@class="cont3"]/table[2]/tbody/tr[{i}]/td')
            list_id.append(data3.text)
    except NoSuchElementException:  # Non-Japanese player does not have row 7
        for i in range(5, 7):  # Scrape row 5 and 6
            data3 = browser.find_element_by_xpath \
                (f'//div[@class="cont3"]/table[2]/tbody/tr[{i}]/td')
            list_id.append(data3.text)
        
    list_tot.append(list_id)  # Append individual list to total list
    
    # Click "Back to list" button
    browser.find_element_by_xpath('//a[contains(text(),"Back to list")]').click()
    
    browser.refresh()  # To avoid stale element reference exception
    # https://stackoverflow.com/questions/27003423/staleelementreferenceexception-on-python-selenium


# Function to scrape each search page by clicking into individual player
def page():
    for i in range(2, 52):
        try:
            # To avoid no such element exception,
            # let browser wait (at most 10s) until name button is clickable
            WebDriverWait(browser, 10) \
                .until(EC.element_to_be_clickable(
                    (By.XPATH, f'//table[@class="m-item_tbl mb10"]/tbody/tr[{i}]/td[4]/a'))).click()
            browser.refresh()
        except TimeoutException:
            break  # No player after the last player, break the loop

        player()
    
    # Export a temporary .csv file after finishing each page
    df_temp = pd.DataFrame(list_tot, columns=[
        'Overall Place', 'Bib', 'Name', 'Race Category', 'Category Place',
        'Age', 'Age Place', 'Sex', 'Gender Place', 'Nationality', 'Nationality Place',
        'Time(net)', 'Time(gross)'])
    df_temp.to_csv('Tokyo Marathon 2021 Temporary Results.csv', index=False)


# Main scraping function
def scraping():
    # First page, click "Search" button
    browser.find_element_by_id('btn_submit').click()
    browser.refresh()
    
    page()
    stop = time.time()  # Print the progress
    print('1/369 page has finished in', (stop-start)/60, 'minutes.')
    
    # Click next page button
    for i in range(2, 7):
        try:
            WebDriverWait(browser, 10) \
                .until(EC.element_to_be_clickable(
                    (By.XPATH, f'//div[@class="fnav pager"]/ul/li[{i}]/a'))).click()
            browser.refresh()
        except TimeoutException:
            break  # In case no page after the last page, break the loop
        
        page()
        stop = time.time()
        print(f'{i}/369 pages have finished in', (stop-start)/60, 'minutes.')
    
    # From page 7 page on, next page is always 7-th button
    for i in range(7, 370):
        try:
            WebDriverWait(browser, 10) \
                .until(EC.element_to_be_clickable(
                    (By.XPATH, '//div[@class="fnav pager"]/ul/li[7]/a'))).click()
            browser.refresh()
        except TimeoutException:
            break
        
        page()
        stop = time.time()
        print(f'{i}/369 pages have finished in', (stop-start)/60, 'minutes.')


# Function to extract English words from Japanese using regular expression
def extract_english_str(df):
    # Create an output dataframe
    df1 = pd.DataFrame()
    
    df1[['Overall Place', 'Bib']] = df[['Overall Place', 'Bib']]
    
    # Extract everything after (but not include) "／"
    # \／: The separator between Japanese and English
    # .: any character; *: zero or more occurrences
    # https://stackoverflow.com/questions/4419000/regex-match-everything-after-question-mark
    # Same logic below
    df1['Name'] = df['Name'].str.extract('\／(.*)')
    
    df1[['Time(net)', 'Time(gross)']] = df[['Time(net)', 'Time(gross)']]
    
    # Replace"・" by space; regex=False: the pattern is not a regular expression
    df1['Race Category'] = df['Race Category'].str.extract('\／(.*)') \
        .iloc[:, 0].str.replace('・', ' ', regex=False)
    
    # Extract all digits, unstack to n columns (for n numbers), convert to int
    # https://stackoverflow.com/questions/60471885/how-to-extract-multiple-numbers-from-pandas-dataframe
    # Same logic below
    df1[['Category Place', 'Category Total']] = \
        df['Category Place'].str.extractall('(\d+)').unstack().astype(int)
    
    df1['Age'] = df['Age']
    
    # Extract age group within ( ); replace "～" by "-"
    df1['Age Group'] = df['Age Place'].str.extract('\((.*)\)') \
        .iloc[:, 0].str.replace('～', '-', regex=False)
    
    # Extract digits after "：" and "／", and separate into two columns
    df1[['Age Place', 'Age Total']] = \
        df['Age Place'].str.extract('\：(.*)\／(.*)').astype(int)
    
    df1['Sex'] = df['Sex'].str.extract('\／(.*)')
    
    df1[['Gender Place', 'Gender Total']] \
        = df['Gender Place'].str.extractall('(\d+)').unstack().astype(int)
    
    # Extract everything after (and include) the first A-Z
    # https://stackoverflow.com/questions/30326562/regular-expression-match-everything-after-a-particular-word
    # As "JAPAN" is written in Japanese, which is NaN in English, fill it
    df1['Nationality'] = df['Nationality'].str.extract('([A-Z].*)').fillna('JAPAN')
    
    df1[['Nationality Place', 'Nationality Total']] = \
        df['Nationality Place'].str.extractall('(\d+)').unstack().astype(int)
    
    return df1


start = time.time()

# Launch Chrome browser
my_path = r'D:\HKU\Courses\Finance\FINA2390 Financial Programming and Databases\4 Web Scarping\chromedriver.exe'
browser = webdriver.Chrome(executable_path=my_path)
# browser.maximize_window()

# Open the webpage
url = 'https://www.marathon.tokyo/2021/result/index.php'
browser.get(url)

search(dict_search_criteria)

list_tot = []  # Create a list containing total results
scraping()  # Main scraping function

browser.quit()  # Close the browser

# Convert results list into a dataframe
df = pd.DataFrame(list_tot, columns=[
    'Overall Place', 'Bib', 'Name', 'Race Category', 'Category Place',
    'Age', 'Age Place', 'Sex', 'Gender Place', 'Nationality', 'Nationality Place',
    'Time(net)', 'Time(gross)'])
# Filter out invalid players
df = df.iloc[:18399, :]
# Function to extract English words from Japanese using regular expression
df1 = extract_english_str(df)
# Export .csv file
df1.to_csv('Tokyo Marathon 2021 Search Results.csv', index=False)

stop = time.time()
print('Finish scraping in', (stop-start)/60, 'minutes.')

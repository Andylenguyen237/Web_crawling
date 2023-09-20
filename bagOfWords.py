from typing import Dict, List
import pandas as pd
import json
import requests
import bs4
import urllib
import unicodedata
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from bs4 import BeautifulSoup

from robots import process_robots, check_link_ok


# Producing a Bag Of Words for All Pages (2 Marks)
def bagOfWords(link_dictionary: Dict[str, List[str]], csv_filename: str):

    data = []

    for seed_url, url_list in link_dictionary.items():
        for link in url_list:
            tokens = preprocessing(link)
            if len(tokens) == 0: tokens = ' '
            #print("LINK URL: ", link)
            #print("WORDS: ", ' '.join([word for word in tokens]))
            data.append({'link_url': link, 'words': ' '.join([word for word in tokens]), 'seed_url': seed_url})

    # Convert the list to a pandas DataFrame
    df = pd.DataFrame(data)

    # Sort the DataFrame by link_url and seed_url
    df_sorted = df.sort_values(by=['link_url', 'seed_url'])

    # Write the DataFrame to a CSV file
    df_sorted.to_csv(csv_filename, index=False)

    return df

def preprocessing(link_to_extract: str):

    # Use correct enconding
    html = requests.get(link_to_extract).content.decode('utf-8')

    # Parse and select the content-text div element
    soup = BeautifulSoup(html, 'html.parser')
    content_div = soup.find('div', {'id': 'mw-content-text'})

    # Remove all th elements with the class of infobox-label
    for th in content_div.find_all('th', {'class': 'infobox-label'}):
        th.extract()

    # Remove all div elements with the class of printfooter
    for div in content_div.find_all('div', {'class': 'printfooter'}):
        div.extract()

    # Remove all div elements with the id of toc
    for div in content_div.find_all('div', {'id': 'toc'}):
        div.extract()

    # Remove all table elements with the class of ambox
    for table in content_div.find_all('table', {'class': 'ambox'}):
        table.extract()

    # Remove all div elements with the class of asbox
    for div in content_div.find_all('div', {'class': 'asbox'}):
        div.extract()

    # Remove all span elements with the class of mw-editsection
    for span in content_div.find_all('span', {'class': 'mw-editsection'}):
        span.extract()

    # Extract the text from the remaining mw-content-text tree 
    text = ' '.join([s.strip() for s in content_div.strings])

    # Normalize the text
    text = text.casefold()
    text = unicodedata.normalize('NFKD', text)
    text = re.sub(r'[^a-z\s\\]', ' ', text)
    text = re.sub(r'[\t\n]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    # Remove stop words and short tokens, and stem the remaining tokens
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    tokens = text.split()
    tokens = [stemmer.stem(token) for token in tokens if token not in stop_words and len(token) > 1]


    return tokens
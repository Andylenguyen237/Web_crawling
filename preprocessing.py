import json

import requests
from bs4 import BeautifulSoup
import urllib
import unicodedata
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

from robots import process_robots, check_link_ok

def preprocessing(link_to_extract: str, json_filename: str):

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
    tokens = [stemmer.stem(token) for token in tokens if token not in stop_words and len(token) > 1 and not any(char.isdigit() for char in token)]

    # Remove tokens that has numerical value
    for token in tokens:
        if re.search(r'\d', token): tokens.remove(token)

    # Output to json file
    with open (json_filename, 'w') as fp:
        json.dump(tokens, fp)

    tokenise = {}
    tokenise[link_to_extract] = tokens
    return tokenise

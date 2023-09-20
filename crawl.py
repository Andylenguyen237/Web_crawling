import pandas as pd
import json
from typing import Dict, List
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urldefrag
import unicodedata
import re
import matplotlib.pyplot as plt
from robots import process_robots, check_link_ok

# A simple page limit used to catch procedural errors.
SAFE_PAGE_LIMIT = 1000


# Get All Links (3 marks)
def craw_allLinks(starting_links: List[str], json_filename: str) -> Dict[str, List[str]]:

    all_links = {}

    # Input original links and crawl
    for original_link in starting_links:

        base_url_match = re.search(r'(https?:\/\/[^\/]+)', original_link)
        base_url = base_url_match.group(1)
        seed_item = original_link[len(base_url):]

        robot_rules = robot_processing(base_url)

        all_links[original_link] = crawl(base_url, seed_item, robot_rules)

    # Output to JSON file
    with open(json_filename, 'w') as json_f:
        json.dump(all_links, json_f)

    return all_links


def robot_processing(base_url: str): 

    robots_item = '/robots.txt'
    robots_url = base_url + robots_item
    page = requests.get(robots_url)
    robot_rules = process_robots(page.text)

    return robot_rules

def crawl(base_url: str, seed_item: str, robot_rules):

    seed_url = base_url + seed_item
    page = requests.get(seed_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    visited = {}
    visited[seed_url] = True
    pages_visited = 1

    links = soup.findAll('a') 
    seed_link = soup.findAll('a', href=re.compile(r"^" + seed_item))

    # FIND ALL LINKS IN WEBPAGE THAT HAS <a href> 
    to_visit_relative = [l for l in links if l not in seed_link and "href" in l.attrs]

    # RESOLVE TO ABSOLUTE URLs (change relative urls to complete ones)
    to_visit = []
    for link in to_visit_relative:
        if not check_link_ok(robot_rules, link['href']): continue
        to_visit.append(urljoin(seed_url, link['href']))

    # RESOLVE ALL FRAGMENTS IN URL AND DUPLICATES URL
    url_with_no_trap = []
    for link in to_visit:
        url_obj = urldefrag(link)
        url_with_no_trap.append(url_obj.url)
    url_with_no_trap = list(set(url_with_no_trap))

    # ONLY GET THE LINKS THAT ARE /samplewiki/ and /fullwiki/
    all_possible_links = []
    for link in url_with_no_trap: 
        match_pattern = re.search("(\/samplewiki\/|\/fullwiki\/)", link)
        if match_pattern:
            all_possible_links.append(link)

    while (all_possible_links):

        if pages_visited == SAFE_PAGE_LIMIT: break

        link = all_possible_links.pop(0)

        # Exclude duplicate seed link (starting link)
        if link in visited: continue

        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')

        visited[link] = True

        # Extract all sublinks in the list
        new_links = soup.findAll('a')

        # Crawl pages in sub links 
        for new_link in new_links:
            
            if "href" not in new_link.attrs: continue
            new_item = new_link['href']
            if not check_link_ok(robot_rules, new_item): continue
            new_url = urljoin(link, new_item)
            new_url_obj = urldefrag(new_url)
            new_url_no_frag = new_url_obj.url

            if new_url_no_frag in visited: continue
            new_match_pattern = re.search("(\/samplewiki\/|\/fullwiki\/)", new_url_no_frag)
        
            if new_match_pattern and new_url_no_frag not in visited and new_url_no_frag not in all_possible_links:
                all_possible_links.append(new_url_no_frag)
        
        pages_visited = pages_visited + 1


    visited_list = list(visited.keys())
    return sorted(visited_list)





import asyncio
import aiohttp
from lxml import html
import json
import csv
# import pandas as pd
import xml.etree.ElementTree as ET
import requests

def fetch_sitemap():
    sitemap_response = requests.get('https://www.mayoclinic.org/patient_consumer_drug.xml')
    root = ET.fromstring(sitemap_response.content)
    namespaces = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [elem.text for elem in root.findall('.//sitemap:loc', namespaces)]
    return urls

def parse_response(resp):
    tree = html.fromstring(resp.content)
    title = tree.xpath('//div[@class="cmp-title"]/h1/text()')[0]
    description = ''.join(tree.xpath('//div[@id="drug-description"]/p/text()'))
    
    return {"Name":title, "Description":description}

def main():
    urls = fetch_sitemap()
    product_page = requests.get(urls[0])
    if product_page.status_code == 200:
        product_details = parse_response(product_page)
        print(product_details)

main()
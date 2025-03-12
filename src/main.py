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

print(len(fetch_sitemap()))

start_url = ''

def main():
    pass
import asyncio
import aiohttp
from lxml import html, etree
import json
import csv
import pandas as pd
import xml.etree.ElementTree as ET
import requests
import re

def fetch_sitemap():
    sitemap_response = requests.get('https://www.mayoclinic.org/patient_consumer_drug.xml')
    root = ET.fromstring(sitemap_response.content)
    namespaces = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [elem.text for elem in root.findall('.//sitemap:loc', namespaces)]
    return urls

def parse_response(resp, i):
    tree = html.fromstring(resp)
    title = tree.xpath('//div[@class="cmp-title"]/h1/text()')[0]
    cleaned_title = re.sub(r'\s*\(.*?\)', '', title).strip()
    description = ''.join(tree.xpath('//div[@id="drug-description"]/p/text()'))
    side_effects_tree = tree.xpath('//div[@id="drug-side-effects"]')[0]
    side_effects_raw = ''.join([etree.tostring(e, encoding='unicode', method='html') for e in side_effects_tree[1:]])
    side_effects = side_effects_tree.xpath('.//li//text()')

    raw_data_list.append({"name": cleaned_title, "name_raw":title, "description":description, "side_effects":side_effects, "side_effects_raw": side_effects_raw, "url": i})
    clean_data.append({"name":cleaned_title, "description":description, "side_effects":side_effects, "url": i})

def main():
    urls = fetch_sitemap()
    product_page = requests.get(urls[0])
    if product_page.status_code == 200:
        product_details = parse_response(product_page)
        print(product_details)

async def main():
    async with aiohttp.ClientSession() as session:
        count = 1
        for i in urls:
            async with session.get(i) as resp:
                response = await resp.text()
                print(f"{count}/{len(urls)}")
                count+=1
                if resp.status != 200: #Check if status code is OK or not
                    print({'URL':i, "Status":resp.status})
                else:
                    try:
                        parse_response(response, i)
                    except Exception as e:
                        print({"URL":i, "Exception":e})
                        
urls = fetch_sitemap()
raw_data_list = []
clean_data = []
asyncio.run(main())

df1 = pd.DataFrame(clean_data)
df1.to_csv(f"Medicine.csv", index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")

df2 = pd.DataFrame(raw_data_list)
df2.to_csv(f"Medicine_Raw.csv", index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
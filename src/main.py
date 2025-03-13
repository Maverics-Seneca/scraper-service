import asyncio
import aiohttp
from lxml import html, etree
import json
# import csv
# import pandas as pd
import xml.etree.ElementTree as ET
import requests
import re
import os
import base64
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')
decoded_credentials = base64.b64decode(firebase_credentials).decode('utf-8')
service_account_info = json.loads(decoded_credentials)
cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)
db = firestore.client()
collection_ref = db.collection('drugsInfo')
index_doc_ref = collection_ref.document('_drug_list')
index_doc = index_doc_ref.get()
existing_drug_ids = set(index_doc.to_dict().get('drugIDs', []))

headers_sitemap = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Sec-Fetch-Site': 'none',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Cache-Control': 'no-cache',
    'Sec-Fetch-Mode': 'navigate',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Safari/605.1.15',
    'Accept-Language': 'en-CA,en-US;q=0.9,en;q=0.8',
    'Priority': 'u=0, i',
}

headers = {
    'Pragma': 'no-cache',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Sec-Fetch-Site': 'same-origin',
    'Accept-Language': 'en-CA,en-US;q=0.9,en;q=0.8',
    'Sec-Fetch-Mode': 'navigate',
    'Cache-Control': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Safari/605.1.15',
    'Referer': 'https://www.mayoclinic.org/drugs-supplements',
    'Sec-Fetch-Dest': 'document',
    'Priority': 'u=0, i',
}

def push_data(data):
    BATCH_SIZE = 50  # Firestore batch size
    total_entries = len(data)
    for i in range(0, total_entries, BATCH_SIZE):
        batch = db.batch()
        batch_data = data[i:i + BATCH_SIZE]
        for entry in batch_data:
            doc_ref = collection_ref.document(entry['id'])  # Use 'id' as document ID
            batch.set(doc_ref, entry)
        batch.commit()

def fetch_sitemap():
    sitemap_response = requests.get('https://www.mayoclinic.org/patient_consumer_drug.xml', headers=headers_sitemap)
    root = ET.fromstring(sitemap_response.content)
    namespaces = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [elem.text for elem in root.findall('.//sitemap:loc', namespaces)]
    urls = [i for i in urls if i.split('/')[-1] not in existing_drug_ids]
    return list(set(urls))

def parse_response(resp, i):
    tree = html.fromstring(resp)
    title = tree.xpath('//div[@class="cmp-title"]/h1/text()')[0]
    cleaned_title = re.sub(r'\s*\(.*?\)', '', title).strip()
    description = ''.join(tree.xpath('//div[@id="drug-description"]/p/text()'))
    side_effects_tree = tree.xpath('//div[@id="drug-side-effects"]')[0]
    side_effects_raw = ''.join([etree.tostring(e, encoding='unicode', method='html') for e in side_effects_tree[1:]])
    side_effects = side_effects_tree.xpath('.//li//text()')

    raw_data_list.append({"id": i.split('/')[-1], "name": cleaned_title, "name_raw":title, "description":description, "side_effects":side_effects, "side_effects_raw": side_effects_raw, "url": i})
    clean_data.append({"id": i.split('/')[-1], "name":cleaned_title, "description":description, "side_effects":side_effects, "url": i})

async def main():
    async with aiohttp.ClientSession() as session:
        count = 1
        for i in urls:
            async with session.get(i, headers=headers) as resp:
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
# print(len(urls))
# urls = urls[:101]
if len(urls) != 0:
    raw_data_list = []
    clean_data = []
    asyncio.run(main())
    push_data(clean_data)
    updated_drug_ids = existing_drug_ids.union(entry['id'] for entry in clean_data)
    index_doc_ref.set({'drugIDs': list(updated_drug_ids)})

# df1 = pd.DataFrame(clean_data)
# df1.to_csv(f"Medicine.csv", index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
# df2 = pd.DataFrame(raw_data_list)
# df2.to_csv(f"Medicine_Raw.csv", index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
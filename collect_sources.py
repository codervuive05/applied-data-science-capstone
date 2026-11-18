"""Optional source collection methods; baseline analysis uses frozen IBM CSVs.

Live SpaceX API schemas and Wikipedia tables can change. These outputs are kept
separate from the historical 90-row modeling cohort.
"""
from pathlib import Path
import json, urllib.request
ROOT=Path(__file__).parent
def collect_api():
 url='https://api.spacexdata.com/v4/launches/past'
 with urllib.request.urlopen(url,timeout=60) as response: records=json.load(response)
 # IDs in rocket/launchpad/payloads/cores can be joined to their v4 endpoints.
 rows=[{'id':r['id'],'date_utc':r['date_utc'],'rocket_id':r['rocket'],
        'launchpad_id':r['launchpad'],'payload_ids':r['payloads'],
        'cores':r['cores']} for r in records]
 (ROOT/'data/live_api_records.json').write_text(json.dumps(rows,indent=2))
 return rows
def collect_wikipedia():
 import pandas as pd
 from io import StringIO
 url='https://en.wikipedia.org/w/index.php?title=List_of_Falcon_9_and_Falcon_Heavy_launches&oldid=1027686922'
 req=urllib.request.Request(url,headers={'User-Agent':'SpaceXCapstoneEducationalAnalysis/1.0'})
 with urllib.request.urlopen(req,timeout=60) as response: html=response.read().decode('utf-8')
 tables=pd.read_html(StringIO(html))
 candidates=[t for t in tables if 'Flight' in str(t.columns) and 'Payload' in str(t.columns)]
 for i,t in enumerate(candidates): t.to_csv(ROOT/f'data/wiki_launches_{i}.csv',index=False)
 return candidates
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(); p.add_argument('source',choices=['api','wikipedia']); args=p.parse_args()
 print(len(collect_api() if args.source=='api' else collect_wikipedia()))

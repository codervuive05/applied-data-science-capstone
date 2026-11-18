from pathlib import Path
import urllib.request
import json

root = Path(__file__).parent
base = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/'
files = {
 'dataset_part_1.csv':'datasets/dataset_part_1.csv',
 'dataset_part_2.csv':'datasets/dataset_part_2.csv',
 'dataset_part_3.csv':'datasets/dataset_part_3.csv',
 'Spacex.csv':'labs/module_2/data/Spacex.csv',
 'spacex_launch_geo.csv':'datasets/spacex_launch_geo.csv',
 'spacex_launch_dash.csv':'datasets/spacex_launch_dash.csv',
 'API_call_spacex_api.json':'datasets/API_call_spacex_api.json',
}
for name, path in files.items():
 target=root/'data'/name
 if not target.exists():
  urllib.request.urlretrieve(base+path,target)
 print(name,target.stat().st_size)
(root/'data'/'sources.json').write_text(json.dumps({n:base+p for n,p in files.items()},indent=2))

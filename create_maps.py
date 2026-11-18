"""Folium maps with a local Natural Earth basemap, avoiding tile dependencies."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).parent; sys.path.insert(0,str(ROOT/'.packages'))
import pandas as pd
import folium
from folium.plugins import MarkerCluster,MousePosition
g=pd.read_csv(ROOT/'data/spacex_launch_geo.csv')
world=json.loads((ROOT/'data/ne_110m_admin_0_countries.geojson').read_text(encoding='utf-8'))
world['features']=[f for f in world['features'] if f['properties']['NAME'] in ['United States of America','Canada','Mexico','Cuba','Bahamas']]
coast_path=ROOT/'data/ne_10m_coastline.geojson'
coast=json.loads(coast_path.read_text(encoding='utf-8')) if coast_path.exists() else json.loads((ROOT/'data/florida_coast.geojson').read_text())
def local_map(center,zoom,detail=False):
 m=folium.Map(location=center,zoom_start=zoom,tiles=None,max_zoom=18,control_scale=True,prefer_canvas=True)
 m.options['maxZoom']=18
 folium.GeoJson(world,name='Natural Earth countries',style_function=lambda f:{'fillColor':'#e9eee8','color':'#9aa79d','weight':1,'fillOpacity':1}).add_to(m)
 if detail:
  # Keep only coast segments near Cape Canaveral / central Florida.
  lines=[]
  for f in coast['features']:
   geometry=f['geometry']; candidates=geometry['coordinates'] if geometry['type']=='MultiLineString' else [geometry['coordinates']]
   for line in candidates:
    selected=[p for p in line if -81.2<p[0]<-80 and 27.9<p[1]<29.2]
    if len(selected)>1: lines.append({'type':'Feature','properties':{},'geometry':{'type':'LineString','coordinates':selected}})
  folium.GeoJson({'type':'FeatureCollection','features':lines},name='Natural Earth 10m coast',style_function=lambda f:{'color':'#087e8b','weight':2}).add_to(m)
  (ROOT/'data/florida_coast.geojson').write_text(json.dumps({'type':'FeatureCollection','features':lines}))
 m.get_root().html.add_child(folium.Element('<div style="position:fixed;bottom:12px;left:10px;z-index:9999;background:white;padding:6px;font:12px Arial">Basemap: Natural Earth (public domain). No road basemap; selected proximity points are approximate.</div>'))
 MousePosition().add_to(m)
 return m
m=local_map([32,-95],4)
for i,(name,r) in enumerate(g.groupby('Launch Site').first().iterrows()):
 folium.Marker([r.Lat,r.Long],tooltip=folium.Tooltip(name,permanent=True,direction='right',offset=(15,i*22-20)),popup=name).add_to(m)
 folium.Circle([r.Lat,r.Long],radius=1000,color='#087e8b').add_to(m)
folium.LayerControl().add_to(m); m.save(ROOT/'output/launch_map.html')
records=local_map([28.57,-80.59],11,True); cluster=MarkerCluster(name='Launch records',options={'spiderfyOnMaxZoom':True}).add_to(records)
for _,r in g.iterrows():
 folium.Marker([r.Lat,r.Long],tooltip=f"Flight {r['Flight Number']} / class {r['class']}",popup=f"{r['Launch Site']}<br>Class {r['class']}",icon=folium.Icon(color='green' if r['class'] else 'red')).add_to(cluster)
folium.LayerControl().add_to(records); records.save(ROOT/'output/records_map.html')
prox=local_map([28.58,-80.69],11,True); launch=[28.562302,-80.577356]
folium.Marker(launch,tooltip='CCAFS LC-40',popup='CCAFS LC-40').add_to(prox)
refs={'Coast reference (0.92 km)':[28.5632,-80.5680],'Road reference (0.55 km)':[28.5623,-80.5830],'Rail reference (1.31 km)':[28.572,-80.585],'Titusville reference (23.16 km)':[28.6122,-80.8076]}
for name,loc in refs.items():
 folium.Marker(loc,tooltip=name,popup=name,icon=folium.Icon(color='orange')).add_to(prox)
 folium.PolyLine([launch,loc],color='#087e8b',tooltip=name).add_to(prox)
folium.LayerControl().add_to(prox); prox.save(ROOT/'output/proximity_map.html')
print('Created 3 Folium maps with local vector basemap')

"""Reproduce SpaceX capstone results using the frozen IBM teaching datasets."""
from pathlib import Path
import sys, json, sqlite3
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'.packages'))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score
import folium
from folium.plugins import MarkerCluster, MousePosition

OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
df=pd.read_csv(ROOT/'data/dataset_part_2.csv')
df['Date']=pd.to_datetime(df.Date)
df['Year']=df.Date.dt.year
sql_df=pd.read_csv(ROOT/'data/Spacex.csv')
geo=pd.read_csv(ROOT/'data/spacex_launch_geo.csv')
dash=pd.read_csv(ROOT/'data/spacex_launch_dash.csv')
plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.titlesize':15})
COLORS=['#a94935','#087e8b']
def save(name):
 plt.tight_layout(); plt.savefig(OUT/(name+'.png'),dpi=180,bbox_inches='tight'); plt.close()
def scatter(x,y,name,xlabel,ylabel):
 fig,ax=plt.subplots(figsize=(10,4.4))
 for v,c in enumerate(COLORS):
  d=df[df.Class==v]; ax.scatter(d[x],d[y],color=c,label=['No successful recovery','Successful recovery'][v],s=48,alpha=.8,edgecolor='white',linewidth=.4)
 ax.set(xlabel=xlabel,ylabel=ylabel); ax.legend(loc='best',fontsize=9); save(name)
scatter('FlightNumber','LaunchSite','flight_site','Flight number','Launch site')
scatter('PayloadMass','LaunchSite','payload_site','Payload mass (kg)','Launch site')
scatter('FlightNumber','Orbit','flight_orbit','Flight number','Orbit')
scatter('PayloadMass','Orbit','payload_orbit','Payload mass (kg)','Orbit')
orbits=df.groupby('Orbit').Class.agg(['mean','count']).sort_values('mean',ascending=False)
fig,ax=plt.subplots(figsize=(10,4.4)); ax.bar(orbits.index,orbits['mean']*100,color='#087e8b'); ax.set(ylabel='Successful recovery (%)',ylim=(0,115),xlabel='Orbit')
for i,row in enumerate(orbits.itertuples()): ax.text(i,row.mean*100+2,f'n={row.count}',ha='center',fontsize=9)
save('orbit_rate')
years=df.groupby('Year').Class.agg(['mean','count'])
fig,ax=plt.subplots(figsize=(10,4.4)); ax.plot(years.index,years['mean']*100,'o-',color='#087e8b'); ax.set(ylabel='Successful recovery (%)',xlabel='Year',ylim=(0,105)); ax.set_xticks(years.index)
for x,r in years.iterrows(): ax.annotate(f'n={int(r["count"])}',(x,r['mean']*100),xytext=(0,8),textcoords='offset points',ha='center',fontsize=8)
save('yearly_rate')
sites=df.groupby('LaunchSite').Class.agg(['sum','count','mean'])
for x,ycol,name in [('FlightNumber','LaunchSite','flight_site'),('PayloadMass','LaunchSite','payload_site'),('FlightNumber','Orbit','flight_orbit'),('PayloadMass','Orbit','payload_orbit')]:
 fig,ax=plt.subplots(figsize=(11,4.1))
 for k,color in [(0,'#b05945'),(1,'#087e8b')]:
  selected=df[df.Class==k]; ax.scatter(selected[x],selected[ycol],c=color,label='Class '+str(k),alpha=.8,s=42)
 ax.set_xlabel('Payload mass (kg)' if x=='PayloadMass' else 'Flight number'); ax.set_ylabel('Launch site' if ycol=='LaunchSite' else 'Orbit'); ax.legend(loc='upper left',bbox_to_anchor=(1.01,1)); fig.tight_layout(); fig.savefig(OUT/(name+'.png'),dpi=160); plt.close(fig)
groups=df.groupby('Orbit').Class.agg(['mean','count']); fig,ax=plt.subplots(figsize=(11,4.1)); ax.bar(groups.index,groups['mean'],color='#087e8b'); ax.set_ylim(0,1.18); ax.set_ylabel('Positive landing rate'); ax.set_xlabel('Orbit')
for i,(_,row) in enumerate(groups.iterrows()): ax.text(i,row['mean']+.025,'n='+str(int(row['count'])),ha='center',fontsize=10)
fig.tight_layout(); fig.savefig(OUT/'orbit_rate.png',dpi=160); plt.close(fig)

conn=sqlite3.connect(':memory:'); sql_df.to_sql('launches',conn,index=False)
queries={
 '01_unique_sites':'SELECT DISTINCT Launch_Site FROM launches ORDER BY Launch_Site',
 '02_cca_records':"SELECT Date, Booster_Version, Launch_Site FROM launches WHERE Launch_Site LIKE 'CCA%' ORDER BY Date LIMIT 5",
 '03_nasa_payload':"SELECT SUM(PAYLOAD_MASS__KG_) AS total_kg FROM launches WHERE Customer='NASA (CRS)'",
 '04_v11_payload':"SELECT AVG(PAYLOAD_MASS__KG_) AS average_kg FROM launches WHERE Booster_Version LIKE 'F9 v1.1%'",
 '05_first_ground':"SELECT MIN(Date) AS first_ground_success FROM launches WHERE Landing_Outcome='Success (ground pad)'",
 '06_drone_payload':"SELECT Booster_Version, PAYLOAD_MASS__KG_ FROM launches WHERE Landing_Outcome='Success (drone ship)' AND PAYLOAD_MASS__KG_>4000 AND PAYLOAD_MASS__KG_<6000",
 '07_mission_outcomes':'SELECT Mission_Outcome, COUNT(*) AS launches FROM launches GROUP BY Mission_Outcome ORDER BY launches DESC',
 '08_max_payload':'SELECT Booster_Version, PAYLOAD_MASS__KG_ FROM launches WHERE PAYLOAD_MASS__KG_=(SELECT MAX(PAYLOAD_MASS__KG_) FROM launches)',
 '09_2015_failures':"SELECT substr(Date,6,2) AS month, Landing_Outcome, Booster_Version, Launch_Site FROM launches WHERE substr(Date,1,4)='2015' AND Landing_Outcome='Failure (drone ship)' ORDER BY Date",
 '10_rank_outcomes':"SELECT Landing_Outcome, COUNT(*) AS launches FROM launches WHERE Date BETWEEN '2010-06-04' AND '2017-03-20' GROUP BY Landing_Outcome ORDER BY launches DESC",
}
results={}
for name,q in queries.items():
 r=pd.read_sql_query(q,conn); results[name]=r.to_dict('records'); r.to_csv(OUT/(name+'.csv'),index=False)
(ROOT/'queries.sql').write_text('\n\n'.join('-- '+n+'\n'+q+';' for n,q in queries.items()))

X=pd.read_csv(ROOT/'data/dataset_part_3.csv'); y=df.Class.to_numpy()
assert len(X)==len(df)==90 and X.notna().all().all()
assert set(y)=={0,1} and int(y.sum())==60
assert X.FlightNumber.to_list()==df.FlightNumber.to_list()
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.2,random_state=2,stratify=y)
cv=StratifiedKFold(n_splits=5,shuffle=True,random_state=42)
specs={
 'Logistic regression':(LogisticRegression(max_iter=3000),{'model__C':[.01,.1,1,10]}),
 'Support vector machine':(SVC(),{'model__C':[.1,1,10],'model__kernel':['linear','rbf'],'model__gamma':['scale',.01,.1]}),
 'Decision tree':(DecisionTreeClassifier(random_state=42),{'model__max_depth':[2,3,4,6,None],'model__min_samples_leaf':[1,2,4],'model__criterion':['gini','entropy']}),
 'K nearest neighbors':(KNeighborsClassifier(),{'model__n_neighbors':[3,5,7,9],'model__weights':['uniform','distance'],'model__p':[1,2]}),
}
metrics=[]; fitted={}
for name,(model,params) in specs.items():
 pipeline=Pipeline([('scale',StandardScaler()),('model',model)])
 grid=GridSearchCV(pipeline,params,cv=cv,scoring='accuracy',n_jobs=1)
 grid.fit(X_train,y_train); pred=grid.predict(X_test); fitted[name]=grid
 metrics.append({'model':name,'cv_accuracy':grid.best_score_,'test_accuracy':accuracy_score(y_test,pred),'precision':precision_score(y_test,pred,zero_division=0),'recall':recall_score(y_test,pred),'f1':f1_score(y_test,pred),'params':grid.best_params_,'confusion_matrix':confusion_matrix(y_test,pred,labels=[0,1]).tolist()})
best=max(metrics,key=lambda r:r['cv_accuracy'])
fig,ax=plt.subplots(figsize=(10,4.4)); idx=np.arange(4); ax.bar(idx-.18,[m['cv_accuracy'] for m in metrics],width=.36,label='Best training CV',color='#087e8b'); ax.bar(idx+.18,[m['test_accuracy'] for m in metrics],width=.36,label='Held-out test',color='#d19b51'); ax.set_xticks(idx,['Logistic regression','SVM','Decision tree','KNN']); ax.set(ylim=(0,1.12),ylabel='Accuracy'); ax.legend(); save('model_accuracy')
cm=np.array(best['confusion_matrix']); fig,ax=plt.subplots(figsize=(6,4.4)); ax.imshow(cm,cmap='Blues'); ax.set(xticks=[0,1],yticks=[0,1],xticklabels=['No successful landing','Successful landing'],yticklabels=['No successful landing','Successful landing'],xlabel='Predicted',ylabel='Actual')
for i in range(2):
 for j in range(2): ax.text(j,i,str(cm[i,j]),ha='center',va='center',fontsize=26,color='white' if cm[i,j]>cm.max()/2 else '#152e45')
save('confusion_matrix')

success=dash.groupby('Launch Site')['class'].sum()
fig,ax=plt.subplots(figsize=(8,4.4)); ax.pie(success,labels=success.index,autopct='%1.1f%%',colors=['#087e8b','#d19b51','#486b9a','#b05945']); ax.set_title('Share of successful landings by site (56-launch sample)'); save('dash_all')
site=success.idxmax(); dist=dash[dash['Launch Site']==site]['class'].value_counts().sort_index()
fig,ax=plt.subplots(figsize=(8,4.4)); ax.pie(dist,labels=['No successful landing' if i==0 else 'Successful landing' for i in dist.index],autopct='%1.1f%%',colors=COLORS); ax.set_title(site+' outcomes'); save('dash_site')
fig,ax=plt.subplots(figsize=(10,4.4))
for i,c in enumerate(COLORS):
 d=dash[dash['class']==i]; ax.scatter(d['Payload Mass (kg)'],d['class'],label=['No successful landing','Successful landing'][i],color=c,alpha=.65,s=55)
ax.set(xlabel='Payload mass (kg)',ylabel='Outcome',yticks=[0,1],ylim=(-.25,1.25)); ax.legend(); save('dash_payload')

m=folium.Map(location=[32,-95],zoom_start=4,tiles='OpenStreetMap')
cluster=MarkerCluster(name='Launch records').add_to(m)
for _,r in geo.iterrows():
 folium.Marker([r.Lat,r.Long],popup=f"Flight {r['Flight Number']}: {r['Launch Site']} / class {r['class']}",icon=folium.Icon(color='green' if r['class'] else 'red')).add_to(cluster)
for site,r in geo.groupby('Launch Site').first().iterrows():
 folium.Circle([r.Lat,r.Long],radius=1000,color='#087e8b',tooltip=site).add_to(m)
 folium.Marker([r.Lat,r.Long],tooltip=site).add_to(m)
MousePosition().add_to(m); folium.LayerControl().add_to(m); m.save(OUT/'launch_map.html')
# Approximate infrastructure coordinates chosen for geographic comparison, not surveyed distances.
launch=[28.562302,-80.577356]
features={'Coast reference':[28.5632,-80.5680],'Road reference':[28.5623,-80.5830],'Rail reference':[28.5720,-80.5850],'Titusville reference':[28.6122,-80.8076]}
from math import radians,sin,cos,asin,sqrt
def km(a,b):
 p1,p2=radians(a[0]),radians(b[0]); dp=p2-p1; dl=radians(b[1]-a[1]); return 6371*2*asin(sqrt(sin(dp/2)**2+cos(p1)*cos(p2)*sin(dl/2)**2))
prox=folium.Map(location=launch,zoom_start=13,tiles='OpenStreetMap'); folium.Marker(launch,tooltip='CCAFS LC-40').add_to(prox)
distances={}
for name,loc in features.items():
 distance=km(launch,loc); distances[name]=distance
 folium.Marker(loc,tooltip=f'{name}: {distance:.2f} km straight line').add_to(prox)
 folium.PolyLine([launch,loc],tooltip=f'{distance:.2f} km',color='#087e8b').add_to(prox)
prox.save(OUT/'proximity_map.html')
summary={'rows':len(df),'successes':int(y.sum()),'failures':int((y==0).sum()),'date_min':str(df.Date.min().date()),'date_max':str(df.Date.max().date()),'sites':sites.reset_index().to_dict('records'),'orbits':orbits.reset_index().to_dict('records'),'years':years.reset_index().to_dict('records'),'sql':results,'models':metrics,'best_model':best['model'],'train_n':len(y_train),'test_n':len(y_test),'baseline':float(y_test.mean()),'distances_km':distances,'dash_success':success.to_dict()}
(OUT/'results.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))

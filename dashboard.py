from pathlib import Path
import sys
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'.packages'))
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

df=pd.read_csv(ROOT/'data/spacex_launch_dash.csv')
app=Dash(__name__)
app.layout=html.Main([
 html.H1('SpaceX Launch Records'),
 html.P('IBM historical teaching sample: 56 launches. Class 1 = successful landing.'),
 dcc.Dropdown(id='site',options=[{'label':'All sites','value':'ALL'}]+[{'label':x,'value':x} for x in sorted(df['Launch Site'].unique())],value='ALL',clearable=False),
 dcc.Graph(id='pie'),
 html.Label('Payload range (kg)'),
 dcc.RangeSlider(id='payload',min=0,max=float(df['Payload Mass (kg)'].max()),step=100,value=[0,float(df['Payload Mass (kg)'].max())],marks={0:'0',5000:'5000',10000:'10000'}),
 dcc.Graph(id='scatter'),
],style={'fontFamily':'Arial','maxWidth':'1100px','margin':'30px auto'})
@app.callback(Output('pie','figure'),Output('scatter','figure'),Input('site','value'),Input('payload','value'))
def update(site,payload):
 selected=df if site=='ALL' else df[df['Launch Site']==site]
 # Slider filters both figures consistently.
 selected=selected[selected['Payload Mass (kg)'].between(*payload)].copy()
 selected['Outcome']=selected['class'].map({0:'No successful landing',1:'Successful landing'})
 if site=='ALL':
  counts=selected.groupby('Launch Site',as_index=False)['class'].sum()
  pie=px.pie(counts,values='class',names='Launch Site',title='Share of successful landings by site')
 else:
  pie=px.pie(selected,names='Outcome',title=site+' outcomes')
 scatter=px.scatter(selected,x='Payload Mass (kg)',y='class',color='Booster Version Category',hover_data=['Launch Site','Flight Number'],title='Payload mass versus recovery outcome')
 scatter.update_yaxes(tickvals=[0,1],ticktext=['No successful landing','Successful landing'])
 return pie,scatter
if __name__=='__main__': app.run(host='127.0.0.1',port=8051,debug=False)

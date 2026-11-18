"""Build a slide-format PDF from the locally regenerated capstone evidence."""
from pathlib import Path
import sys,json,textwrap
ROOT=Path(__file__).parent; sys.path.insert(0,str(ROOT/'.packages'))
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,white
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from PIL import Image
R=json.loads((ROOT/'output/results.json').read_text())
OUT=ROOT/'output'; PDF=OUT/'Data Science Capstone Project Report.pdf'
GIT='https://github.com/codervuive05/applied-data-science-capstone'
W,H=960,540; c=canvas.Canvas(str(PDF),pagesize=(W,H)); c.setTitle('Data Science Capstone Project Report - SpaceX Falcon 9')
NAVY='#153148'; TEAL='#087e8b'; GRAY='#536271'; num=0
body=ParagraphStyle('body',fontName='Helvetica',fontSize=18,leading=26,textColor=HexColor(NAVY))
small=ParagraphStyle('small',parent=body,fontSize=13,leading=17)
def p(text,x,y,w,style=body):
 para=Paragraph(text,style); _,h=para.wrap(w,1000); para.drawOn(c,x,y-h); return h
def start(title,section=''):
 global num
 num+=1; c.setFillColor(white); c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(HexColor(NAVY)); c.setFont('Helvetica-Bold',31); c.drawString(44,H-58,title)
 c.setFillColor(HexColor(TEAL)); c.rect(44,H-76,50,3,stroke=0,fill=1)
 c.setFillColor(HexColor(GRAY)); c.setFont('Helvetica',9); c.drawString(44,20,'SpaceX Falcon 9 | IBM historical teaching datasets | '+section); c.drawRightString(W-40,20,str(num))
def end(): c.showPage()
def link(path='',y=47):
 url=GIT+path; c.setFont('Helvetica',11); c.setFillColor(HexColor(TEAL)); c.drawString(44,y,url); c.linkURL(url,(44,y-2,44+c.stringWidth(url,'Helvetica',11),y+12),relative=0)
def bullets(title,items,path='',note=None):
 start(title); y=425
 for text in items:
  h=p(text,50,y,855); y-=h+18
 if note: p(note,50,103,855,small)
 link(path); end()
def chart(title,file,insight,source='90-launch modeling cohort',note=None):
 start(title,'Results')
 img=Image.open(OUT/file); iw,ih=img.size; box=(50,145,860,295); scale=min(box[2]/iw,box[3]/ih); dw,dh=iw*scale,ih*scale
 c.drawImage(str(OUT/file),box[0]+(box[2]-dw)/2,box[1]+(box[3]-dh)/2,dw,dh,mask='auto')
 p(insight,50,128,860,ParagraphStyle('caption',parent=body,fontSize=16,leading=21))
 if note: p(note,50,68,860,ParagraphStyle('note',parent=small,fontSize=10,leading=12))
 c.setFont('Helvetica',9); c.setFillColor(HexColor(GRAY)); c.drawString(50,37,'Source: '+source); end()
def table(title,headers,rows,caption='',widths=None,font=16):
 start(title,'Results'); data=[[Paragraph(str(x),ParagraphStyle('th',parent=small,fontSize=font,leading=font+3,textColor=white)) for x in headers]]
 data += [[Paragraph(str(x),ParagraphStyle('td',parent=small,fontSize=font,leading=font+3)) for x in r] for r in rows]
 t=Table(data,colWidths=widths or [860/len(headers)]*len(headers)); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor(NAVY)),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#eef5f6')]),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,0),(-1,0),1,HexColor(TEAL))])); tw,th=t.wrap(860,350)
 if th>340: raise ValueError(f'Table too tall: {title} {th}')
 t.drawOn(c,50,435-th)
 if caption: p(caption,50,min(435-th-18,125),860,small)
 link('/blob/main/queries.sql'); end()

start('Data Science Capstone Project Report')
p('Predicting Falcon 9 first-stage landing outcomes',50,375,830,ParagraphStyle('hero',parent=body,fontSize=32,leading=41))
p('Applied Data Science Capstone<br/>Historical SpaceX analysis and reproducible evidence<br/>19 November 2026',50,235,830)
link(); end()
bullets('Executive Summary',[
 'Methods: IBM frozen API-derived data, source collection workflows, data cleaning, SQL, visual EDA, Folium maps, Plotly Dash, and four classifiers.',
 '90 Falcon 9 launches (2010-2020): 60 positive landing labels and 30 negative labels. Overall positive rate: 66.7%.',
 'SVM and KNN tied at 86.3% training cross-validation accuracy. A predeclared ordering selects SVM; held-out SVM accuracy is 77.8% (14/18).',
 'KNN and the decision tree reach 83.3% on this test set. A small random test set and historical feature availability limit operational use.'
])
bullets('Introduction',[
 'Business context: reusable first stages can affect launch economics. Landing outcome analysis can support risk assessment for a competing launch provider.',
 'Problem: predict the course-defined binary Falcon 9 first-stage landing label using historical mission and booster characteristics.',
 'Questions: how do payload, launch site, orbit, and experience relate to landing success? Which model generalizes best under a consistent evaluation?',
 'Scope: historical educational analysis. This study does not estimate current launch prices or demonstrate a causal cost saving.'
])
table('Datasets and analysis scope',['Dataset','Rows','Use'],[
 ['dataset_part_1 / part_2 / part_3','90 each','Cleaning lineage / labeled EDA / encoded model features'],
 ['Spacex.csv','101','Ten SQL exercises; historical mission records'],
 ['spacex_launch_geo.csv','56','Folium sites, individual launch markers, proximity'],
 ['spacex_launch_dash.csv','56','Interactive site and payload exploration']],
 'These cohorts differ. Their counts and rates are reported separately and are not pooled.',[320,95,445])
bullets('Data Collection - SpaceX API',[
 'GET /v4/launches/past returns launch JSON. Keep Falcon 9 records and a fixed historical cutoff for comparable analysis.',
 'Join rocket, launchpad, payload, and core IDs to /v4/rockets, /launchpads, /payloads, and /cores endpoints.',
 'Normalize fields into Date, PayloadMass, Orbit, LaunchSite, core attributes, landing Outcome, Latitude, and Longitude.',
 'This report recomputes results from IBM frozen CSVs and the supplied API snapshot. Live API collection code is provided separately; it was not used to change the historical cohort.'
],'/blob/main/collect_sources.py')
bullets('Data Collection - Web Scraping',[
 'Source: Wikipedia Falcon 9 / Falcon Heavy launch list, revision oldid=1027686922, as specified in the course lab.',
 'Workflow: request HTML -> parse tables -> identify launch tables -> extract date, booster, site, payload mass, orbit, customer, and outcomes -> normalize rows.',
 'Remove footnotes and normalize numeric units and dates. Keep mission success distinct from first-stage landing success.',
 'Source workflow is implemented in collect_sources.py. Quantitative SQL results here use IBM Spacex.csv; no fresh Wikipedia extraction is claimed.'
],'/blob/main/collect_sources.py')
bullets('Data Wrangling Methodology',[
 'Use IBM Falcon 9 cohort, renumber FlightNumber, parse dates, retain one record per flight, and inspect missing values and data types.',
 'The supplied PayloadMass values already include course mean imputation. Do not replace real zero-mass entries in the separate SQL/dashboard cohorts without justification.',
 'Class = 0 for unsuccessful or absent landings; Class = 1 for the course-defined successful landing outcomes. Positive ocean landings are not proof of booster recovery.',
 'Use the supplied one-hot feature matrix for orbit, site, serial, and boolean attributes. Fit StandardScaler only inside each training fold.'
],'/blob/main/analyze.py')
bullets('EDA with Data Visualization',[
 'Scatter plots: FlightNumber vs LaunchSite and Orbit show experience patterns; PayloadMass vs LaunchSite and Orbit show payload context.',
 'Orbit success bars compare conditional landing rates; sample counts prevent overinterpreting tiny orbit groups.',
 'Yearly trend: aggregate mean(Class) by launch year to inspect historical changes in observed landing labels.',
 'These are descriptive associations. Site, orbit, payload, era, and booster version are confounded.'
],'/blob/main/analyze.py')
chart('Flight Number versus Launch Site','flight_site.png','Later flights show more positive labels at all three sites. KSC has 17/22 positive outcomes; CCAFS has 33/55.')
chart('Payload Mass versus Launch Site','payload_site.png','Sites have different payload distributions. Launch site alone cannot explain why a landing succeeds.')
chart('Success Rate by Orbit','orbit_rate.png','GTO: 14/27 (51.9%); ISS: 13/21 (61.9%); VLEO: 12/14 (85.7%). Single-launch orbits are highly uncertain.')
chart('Flight Number versus Orbit','flight_orbit.png','Positive labels become common later in the sequence, while orbit mix changes. Flight number partly captures historical development.')
chart('Payload Mass versus Orbit','payload_orbit.png','Very heavy payloads are concentrated in VLEO. Compare payloads within mission context rather than treating mass as a universal threshold.')
chart('Yearly Landing Success Trend','yearly_rate.png','Positive rate rises from 0/1 in 2010 to 16/19 in 2020, with a dip in 2018. Annual sample sizes and mission mix vary.')
table('Landing Rates by Launch Site',['Site','Positive / total','Rate'],[[r['LaunchSite'],f"{r['sum']} / {r['count']}",f"{r['mean']:.1%}"] for r in R['sites']], 'KSC and VAFB show similar rates, but their samples are smaller than CCAFS.',[380,240,240])
bullets('EDA with SQL',[
 'Load the 101-row Spacex.csv into SQLite. queries.sql contains all ten reproducible queries.',
 'SELECT DISTINCT and LIKE identify launch sites. SUM and AVG summarize customer payloads and booster versions.',
 'MIN finds the earliest ground-pad landing. WHERE filters drone-ship landings by mass, and a MAX subquery identifies the heaviest missions.',
 'GROUP BY counts mission outcomes; date filters and substr extract the 2015 failures and rank historical landing outcomes.'
],'/blob/main/queries.sql')
table('SQL Results - Sites and First Records',['Date','Booster','Site'],[[r['Date'],r['Booster_Version'],r['Launch_Site']] for r in R['sql']['02_cca_records']], 'Four unique labels: CCAFS LC-40, CCAFS SLC-40, KSC LC-39A, VAFB SLC-4E. LC-40 and SLC-40 are retained as source labels.',[220,340,300])
table('SQL Results - Payloads and First Landing',['Query','Result'],[
 ['NASA (CRS) total payload','45,596 kg'],['F9 v1.1 average payload','2,534.67 kg'],['First successful ground-pad landing','2015-12-22'],['Maximum payload mass','15,600 kg (12 matching booster records)']], 'NASA is matched exactly as NASA (CRS); F9 v1.1 uses a prefix match. Dates use source UTC records.',[530,330])
table('SQL Results - Drone-Ship Landings',['Booster','Payload (kg)'],[[r['Booster_Version'],r['PAYLOAD_MASS__KG_']] for r in R['sql']['06_drone_payload']], 'Successful drone-ship landings with payload strictly greater than 4,000 kg and less than 6,000 kg.',[580,280])
table('SQL Results - Mission Outcomes',['Raw source outcome','Count'],[[r['Mission_Outcome'].replace(' ','&nbsp;'),r['launches']] for r in R['sql']['07_mission_outcomes']], 'Raw categories include one trailing-space Success. After trimming: 99 Success, 1 Success (payload status unclear), 1 Failure (in flight). Mission outcome differs from landing outcome.',[650,210])
for i in range(2):
 records=R['sql']['08_max_payload'][i*6:(i+1)*6]
 table(f'SQL Results - Maximum Payload ({i+1}/2)',['Booster version','Payload (kg)'],[[r['Booster_Version'],r['PAYLOAD_MASS__KG_']] for r in records], 'All 12 matching records share the maximum payload mass of 15,600 kg.',[620,240],font=15)
table('SQL Results - 2015 Landing Failures',['Month','Booster','Launch site'],[[{'01':'January','04':'April'}[r['month']],r['Booster_Version'],r['Launch_Site']] for r in R['sql']['09_2015_failures']], 'Two drone-ship landing failures are recorded in 2015 for this query. This filter does not include every possible type of landing failure.',[200,360,300])
table('SQL Results - Landing Outcome Rankings',['Landing outcome','Count'],[[r['Landing_Outcome'],r['launches']] for r in R['sql']['10_rank_outcomes']], 'Inclusive date interval: 2010-06-04 to 2017-03-20. Tied counts have equal frequency.',[670,190],font=14)
bullets('Interactive Visual Analytics',[
 'Folium: site markers and 1 km circles, a cluster of 56 launch records colored by outcome, layer controls, mouse coordinates, and proximity lines.',
 'Proximity map: inspect coastal location and nearby transport reference points. Distances use the haversine formula and approximate manually selected coordinates.',
 'Plotly Dash: choose a site, adjust payload range, view success pie charts, and compare payload mass against outcome by booster category.',
 'Both dashboard figures respond to the selected site and payload range. The interactive data cohort has 56 launches and must not be pooled with the 90-row modeling cohort.'
],'/blob/main/dashboard.py',note='Map code: '+GIT+'/blob/main/analyze.py')
for title,file,caption in [
 ('Folium - Launch Sites and Records','map_sites.jpg','Four source site labels identify the Florida and California launch locations. CCAFS labels refer to closely located source records.'),
 ('Folium - Individual Launch Outcomes','map_records.jpg','Green and red launch markers represent course success and failure labels. Coincident coordinates are expanded for inspection.'),
 ('Folium - Proximity Analysis','map_proximity.jpg','CCAFS LC-40 is approximately 0.92 km from the chosen coast point and 23.16 km from the Titusville reference. Points are illustrative, not surveyed nearest features.')]:
 if (OUT/file).exists(): chart(title,file,caption,'Folium / Natural Earth public-domain geography',note='Approximate coordinates and distances are in analyze.py. Local basemap has no road detail.')
chart('Plotly Dash - Successful Landings by Site','dash_all.png','KSC LC-39A contributes 10/24 (41.7%) of positive labels in the 56-launch sample. This is a share of successes, not the site success rate.','56-launch dashboard cohort')
chart('Plotly Dash - Selected Site Outcomes','dash_site.png','For KSC LC-39A, the pie switches to the success/failure distribution. The site selector and payload slider filter the underlying records.','56-launch dashboard cohort')
if (OUT/'dashboard.jpg').exists(): chart('Plotly Dash - Running Application','dashboard.jpg','The running dashboard provides the site dropdown, payload range filter, and both result figures.','Locally tested Plotly Dash app')
chart('Payload versus Launch Outcome','dash_payload.png','Payload mass alone does not cleanly separate outcomes. The running app adds color by booster version category and mission hover details.','56-launch dashboard cohort')
bullets('Predictive Analysis - Evaluation Design',[
 'Use 90 labeled launches and the supplied encoded feature matrix. Stratified train/test split: 72 training and 18 test examples; random_state=2.',
 'Tune logistic regression, SVM, decision tree, and KNN with five shuffled stratified folds on the training set only (random_state=42).',
 'Pipeline scaling prevents train/test normalization leakage. Select by mean training cross-validation accuracy, with listed model order breaking exact ties.',
 'The test set has 12 positive and 6 negative labels. Always predicting positive gives 66.7% accuracy; one test error changes accuracy by 5.6 percentage points.'
],'/blob/main/analyze.py')
table('Predictive Analysis - Model Comparison',['Model','CV accuracy','Test accuracy','Test F1'],[[r['model'],f"{r['cv_accuracy']:.1%}",f"{r['test_accuracy']:.1%}",f"{r['f1']:.3f}"] for r in R['models']], 'SVM and KNN tie on CV. SVM is selected by fixed ordering; KNN and tree score higher on this small test set. Test performance is not used to select hyperparameters.',[350,175,175,160])
chart('Predictive Analysis - Evaluation Results','model_accuracy.png','Cross-validation selects SVM under the fixed tie rule. Test accuracies span 77.8%-83.3%; the difference is only one launch.','72 training / 18 test; identical stratified split')
chart('Predictive Analysis - Confusion Matrix','confusion_matrix.png','Selected SVM: TN=3, FP=3, FN=1, TP=11. Precision=78.6%, recall=91.7%, F1=0.846. False positives are material for optimistic landing estimates.','18 held-out launches; positive = Class 1')
bullets('Best Model and Practical Limits',[
 'SVM and KNN have the same best mean CV score (86.3%). SVM is retained by fixed ordering, using a linear kernel and C=0.1.',
 'SVM test accuracy is 77.8%, compared with the always-positive baseline of 66.7%. It misses 1 of 12 positives but predicts success for 3 of 6 negatives.',
 'The supplied matrix includes serial IDs and snapshot attributes such as reuse count. Availability at launch time must be audited before prospective deployment.',
 'A next evaluation should use a chronological holdout and grouped booster validation, remove unavailable future information, and report calibrated probabilities.'
],'/blob/main/analyze.py')
bullets('Conclusion and Further Insights',[
 'Landing labels improve over the historical period, but mission mix and booster technology change together. High site or orbit rates do not establish causality.',
 'Payload and orbit should be evaluated jointly. Tiny orbit groups with 100% success do not establish reliable operational performance.',
 'For planning, use scenario-based expected loss: estimated failure probability times recovery-loss cost. Costs are scenario inputs, not inferred from this dataset.',
 'Extend the study with calibrated uncertainty, temporal validation, and a data-availability checklist. Collect weather and mission constraints before operational use.'
],'/blob/main/README.md')
bullets('Sources and Reproducibility',[
 'IBM Skills Network historical teaching datasets: dataset_part_1.csv, dataset_part_2.csv, dataset_part_3.csv, Spacex.csv, spacex_launch_geo.csv, spacex_launch_dash.csv. Exact source URLs are recorded in data/sources.json.',
 'Original data lineage: SpaceX API v4 and the Wikipedia launch list revision used by the course. Maps: Folium / Leaflet and Natural Earth public-domain geography.',
 'Run download_data.py, analyze.py, create_maps.py, dashboard.py, then build_report.py. Results, SQL outputs, figures, maps, and the report are stored in output/.',
 'Prepared with AI assistance. Quantitative results were regenerated from the listed IBM datasets. The learner should review the analysis and comply with course rules before submission.'
],'/blob/main/README.md')
c.save(); print(PDF,num,'slides')

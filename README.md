# Applied Data Science Capstone: Falcon 9 landing outcomes

Reproducible analysis of the historical IBM course datasets. This project was
prepared with AI assistance; the learner must review the work and follow the
course's rules before submission.

## Report

[Data Science Capstone Project Report](output/Data%20Science%20Capstone%20Project%20Report.pdf)

## Reproduce

Python 3.11+ is recommended. In an isolated environment:

```powershell
python -m pip install -r requirements.txt
python download_data.py
python analyze.py
python create_maps.py
python dashboard.py
# Dashboard: http://127.0.0.1:8051/
python build_report.py
```

`analyze.py` fits four models with five-fold stratified training cross-validation,
scaling within each fold, and an independent stratified 18-launch test set.
`create_maps.py` replaces the default tile-dependent maps with Folium maps using
local Natural Earth geography. `output/*.html` can be opened in a browser; map
JavaScript/CSS dependencies are still loaded from their public CDNs.

Report screenshots record the tested map and dashboard views. Rebuilding the
analysis regenerates numeric figures; refresh screenshots separately after UI
changes. The PDF builder uses the saved screenshots when present.

## Files

- `SpaceX_Capstone.ipynb`: navigable notebook for the analysis components.
- `download_data.py`: downloads the seven IBM source datasets.
- `collect_sources.py`: optional live API and Wikipedia collection methods;
  these live methods were not used to regenerate the historical report.
- `analyze.py`: EDA, all ten SQL results, model search, metrics, and plots.
- `queries.sql`: SQL for sites, payloads, landings, outcomes, ranking, and time.
- `dashboard.py`: running Plotly Dash app with site and payload filters.
- `create_maps.py`: site map, clustered launch records, and proximity map.
- `build_report.py`: creates the slide-format PDF from regenerated results.
- `data/sources.json`: IBM dataset URLs; CSV snapshots are included.
- `output/results.json`: all quantitative report results and hyperparameters.

## Dataset boundaries

The 90-row modeling cohort is dated 2010-06-04 through 2020-11-05. It has 60
positive landing labels and 30 negatives. Separate datasets contain 101 SQL
records and 56 geographic/dashboard records. Rates across these cohorts are
not interchangeable.

Class 1 follows the course definition and can include successful ocean
touchdowns. It does not by itself prove the booster was recovered or reused.
Mission success, landing success, and subsequent reuse are different outcomes.

## Results and limitations

- SVM and KNN tie at 86.29% mean training CV accuracy. Fixed model order selects
  SVM; test accuracy is 77.78% (14/18), precision 78.57%, recall 91.67%.
- Decision tree and KNN score 83.33% on the same test set. This test difference
  is one launch, and test scores are not used for model selection.
- Selected SVM confusion matrix (rows actual, columns predicted; labels 0,1):
  `[[3,3],[1,11]]`.
- Supplied feature snapshots may include information unavailable before a
  launch, including reuse counts. A chronological evaluation, a booster-group
  split, and an availability audit are necessary for operational predictions.
- Proximity coordinates are manually chosen approximate reference points.
  Haversine distances are straight-line distances, not surveyed nearest
  infrastructure distances. The local basemap has no road/rail detail.

## Sources and attribution

IBM Skills Network course CSVs and API snapshot: see `data/sources.json`.
Source lineage: [SpaceX API](https://github.com/r-spacex/SpaceX-API) and the
[Wikipedia revision](https://en.wikipedia.org/w/index.php?title=List_of_Falcon_9_and_Falcon_Heavy_launches&oldid=1027686922)
used by the course. Optional source collectors are provided, but no fresh API
or Wikipedia data are claimed for the frozen-cohort results.

Maps use [Natural Earth](https://www.naturalearthdata.com/) public-domain
geography from the [official vector repository](https://github.com/nvkelso/natural-earth-vector/tree/master/geojson).
`ne_110m_admin_0_countries.geojson` supplies country boundaries and
`florida_coast.geojson` is a spatial subset of `ne_10m_coastline.geojson`.
Maps are rendered with Folium/Leaflet. No other learner's slides or notebook
solutions are included in this repository.

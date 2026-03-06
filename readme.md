#Licensing (demo data):

` docker run --rm -v "$(pwd)/output:/output" reporter`

## Licensing (your data):

`docker run --rm -v "$(pwd)/data:/data" -v "$(pwd)/output:/output" -e DATA_PATH=/data/licensing.json reporter python run_reports.py licensing`

## Company (example or your data):

`docker run --rm -v "$(pwd)/data:/data" -v "$(pwd)/output:/output" reporter python run_reports.py company`

`docker run --rm -v "$(pwd)/data:/data" -v "$(pwd)/output:/output" reporter python run_reports.py company /data/by-company.json`

## SharePoint (example or your data):

`docker run --rm -v "$(pwd)/data:/data" -v "$(pwd)/output:/output" reporter python run_reports.py sharepoint`
`docker run --rm -v "$(pwd)/data:/data" -v "$(pwd)/output:/output" reporter python run_reports.py sharepoint /data/sharepoint.json`
# Jira Slow Queries Log Parser
Jira Server and Data Center products keep logs of JQL searches which take longer than a limit (400 ms).  
These logs can be found under *<JIRA_HOME>*/log/atlassian_slow_queries.log file. This file should something like this:
```
2016-11-21 09:08:49,068 http-nio-8080-exec-16 INFO johndoe 548x103721x5 11nnyad /url/ [issue.search.providers.LuceneSearchProvider_SLOW] JQL query '{project = Teams in Space} ' produced lucene query project:10000' and took '561' ms to run.
```

This tool helps you to analyze this log file in a more structured way. 
Slow queries log file is parsed and its fields displayed as columns in a csv file
where lines are ordered by execution time so that you can easy find top time consuming queries.

Currently only Jira 7 versions are supported.

## How to run locally 
Run following command in root directory to install requirements
```
pip install -r requirements.txt
```

Run following command to start web app
```
pip install -r requirements.txt
```
It will start a lightweight Flask application on your local machine. 
Go to link on the console upload you file and get the results.

This is a better choice if you don't want to send your logs files outside of your network.
## How to run on Cloud
This app deployed as a Google Cloud Function on
https://us-central1-api-project-1093761300360.cloudfunctions.net/slow_queries_log_parser

**Note:** App might have a small warm-up time if it has not ben used for a while. 
Please give it a couple of seconds to open.
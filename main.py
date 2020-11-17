import io
import re
import zipfile

import pandas as pd
from flask import make_response, abort, render_template


def parse_logs(log_file):
    slow_queries = []
    for line in log_file:
        # line = log_file.readline()
        if type(line) is bytes:
            line = line.decode("utf-8", 'ignore')
        if not line:
            break
        line = line.rstrip()

        splits = line.split("INFO", 1)
        if len(splits) < 2:
            slow_queries.append(new_error_line(line))
            continue

        words_before_info = splits[0].split()
        if len(words_before_info) < 3:
            continue

        words_after_info = splits[1].split()
        if "Sending mailitem" in line:
            match = re.search('JQL query \'(.+?)\' produced lucene query', splits[1])
            if not match:
                continue
            else:
                function = match.group(1)
        elif "ScriptRunner" in line:
            match = re.search('with clause \'(.+?)\' took', splits[1])
            if not match:
                continue
            else:
                function = match.group(1)

        else:
            match = re.search('JQL query \'(.+?)\' produced lucene query', splits[1])
            if not match:
                continue
            else:
                function = match.group(1)

        duration = get_duration_from_line(line)

        date = words_before_info[0] + ' ' + words_before_info[1]
        thread = words_before_info[2]
        user = words_after_info[0]
        slow_queries.append(new_slow_query(date, thread, user, function, duration))

    return slow_queries


def get_duration_from_line(line):
    match = re.search('took \'(.+?)\' ms', line)
    if not match:
        return None  # Line does not contain a valid duration information just skip
    else:
        return match.group(1)


def new_slow_query(date, thread, user, function, duration):
    return {
        'date': date,
        'thread': thread,
        'user': user,
        'function': function,
        'duration': duration,
    }


def new_error_line(line):
    return {
        'function': 'ERROR Could not parse the line',
        'line': line
    }


def get_first_file_from_zip(zip_file):
    zfile = zipfile.ZipFile(io.BytesIO(zip_file.read()), 'r')
    files_in_zip = zfile.infolist()
    if len(files_in_zip) == 0:
        return None
    elif len(files_in_zip) == 1:
        return zfile.open(files_in_zip[0])  # Extract and return the only element in zip
    else:  # If there are multiple files in a zip
        largest_file = None
        largest_file_size = 0
        for finfo in files_in_zip:
            if "atlassian-jira-slow-queries" in finfo.filename:  # Extract the one with a matching name
                return zfile.open(finfo)
            if finfo.file_size > largest_file_size:
                largest_file = finfo
        return zfile.open(largest_file)  # or extract the one with largest size if there is a no name match


# This is the main functionality of the app and its entry point in Google Cloud Functions
def main(request):
    if request.method == 'POST':
        files = request.files
        if not files:
            return abort(400, "Please provide either a .log file or a .zip file containing this log.")

        request_file = next(iter(files.values()))
        log_file = None

        if request_file.filename.lower().endswith('.zip'):
            log_file = get_first_file_from_zip(request_file)
        else:  # request_file.filename.lower().endswith(('.txt', '.log')):
            log_file = request_file
        slow_queries = parse_logs(log_file)

        df = pd.DataFrame(slow_queries)
        df["duration"] = pd.to_numeric(df["duration"])
        df = df.sort_values(by=['duration'], ascending=False)

        resp = make_response(df.to_csv())
        resp.headers["Content-Disposition"] = "attachment; filename=slow_queries.csv"
        resp.headers["Content-Type"] = "text/csv"

        return resp
    else:
        return render_template('index.html')


# This is the entry point of app on a local development environment
if __name__ == "__main__":
    from flask import Flask, request

    app = Flask(__name__)


    @app.route('/', methods=['GET', 'POST'])
    def index():
        return main(request)


    app.run('127.0.0.1', 8000, debug=True)

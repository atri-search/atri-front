# Copyright 2020 Marcos Pontes. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY MARCOS PONTES ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL MARCOS PONTES OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of MARCOS PONTES.
import json

import requests

from flask import render_template, request, flash, url_for, redirect

from . import search_blueprint as bp
from atri.config import BASE_API_URL


@bp.route("/", methods=['GET'])
def home():
    return render_template("index.html")


@bp.route("/search/file", methods=['GET'])
def file():
    return render_template("file-search.html")


@bp.route("/search", methods=['GET'])
def search_text():
    collection_name = request.args.get("collection", None)
    keywords = request.args.get("keywords", None)

    advanced = request.args.get("advanced", None)

    kwargs = dict()

    if collection_name and keywords:
        if advanced:
            return search(collection_name, keywords=keywords, **json.loads(advanced))
        else:
            return search(collection_name, keywords=keywords)

    if not collection_name:
        flash("[ERROR] You need to select one collection.")
        if keywords:
            kwargs['keywords'] = keywords

    if not keywords:
        flash("[ERROR] You need to put some input.")
        if collection_name:
            kwargs['collection_name'] = collection_name
            kwargs['advanced'] = advanced

    return render_template('index.html', **kwargs)


@bp.route("/reports", methods=['GET'])
def reports():
    return render_template("qrel.html")


@bp.route("/search/file", methods=['POST'])
def search_file():
    data = request.form

    collection_name = data.get("collection", None)
    advanced = data.get("advanced", None)
    file_up = request.files.getlist("file")

    kwargs = dict()
    if collection_name:
        send_file = [('files', (f.filename, f.stream, f.mimetype)) for f in file_up]

        if not send_file:
            flash("[ERROR] You need to put one file.")
            if collection_name:
                kwargs['collection_name'] = collection_name
                kwargs['advanced'] = advanced
        else:
            if advanced:
                try:
                    return search(collection_name, file_search=send_file, **json.loads(advanced))
                except:
                    flash("[ERROR] Invalid input.")
            else:
                try:
                    return search(collection_name, file_search=send_file)
                except:
                    flash("[ERROR] Invalid input.")

    if not collection_name:
        flash("[ERROR] You need to select one collection.")

    return render_template("file-search.html", **kwargs)


def search(collection_name, *, keywords=None, file_search=None, **kwargs):
    try:
        query_json = kwargs
        if keywords:
            query_json['summarization'] = True
            response = requests.post(BASE_API_URL + f'/search/{collection_name}',
                                     json={'query': keywords, 'advanced_options': query_json})
        else:
            query_json['summarization'] = False
            payload = {"multiquery": query_json.pop('multiquery', False),
                       "options_payload": json.dumps(query_json)
                       }
            response = requests.post(BASE_API_URL + f'/search/{collection_name}/file',
                                     files=file_search,
                                     data=payload)
    except requests.exceptions.RequestException:
        return render_template("error.html")

    if response.status_code != 200:
        flash("[ERROR] Something went wrong. Please try again.")
        return redirect(url_for('search.home'))

    json_response = response.json()

    if 'reports' in json_response:
        # group reports by metric
        reports_by_metric = {}
        try:
            for metrics in json_response['reports'].values():
                # metric: {'labels': [], 'values': []}
                for metric, value in metrics.items():
                    # split metric by @
                    metric_name = metric.split('@')[0]
                    if metric_name not in reports_by_metric:
                        reports_by_metric[metric_name] = {'labels': [], 'values': []}
                    reports_by_metric[metric_name]['labels'].append(metric.split('@')[1])
                    reports_by_metric[metric_name]['values'].append(value)
        except Exception as e:
            flash(f"[ERROR] {e}")
            return render_template("error.html")

        return render_template("reports.html", qrel=list(json_response['reports'].keys())[0], reports=reports_by_metric)

    return render_template("relevant.html", results=json_response, keywords=keywords if keywords else
                           [f[1][0] for f in file_search],  # Get the file names
                           collection_name=collection_name)


@bp.route("/collection/<string:collection_name>/defaults", methods=['GET', 'POST'])
def search_configurations(collection_name):
    if request.method == 'GET':
        response = None
        try:
            response = requests.get(BASE_API_URL + f"/default/similarity/{collection_name}")
        except requests.exceptions.RequestException:
            flash("[ERROR] Unexpected error")

        if response:
            configuration = response.json()
        else:
            configuration = {"error": "Unexpected error"}

        return render_template('advanced.html', defaults=configuration)

    elif request.method == 'POST':
        data = request.get_json()
        search_defaults = data.get('search_defaults', None)
        search_defaults = json.loads(search_defaults) if search_defaults else {}

        request_data = {
            "search_defaults": search_defaults
        }
        try:
            response = requests.put(BASE_API_URL + f'/default/similarity/{collection_name}', json=request_data)
            return response.json()
        except requests.exceptions.RequestException:
            return render_template("error.html")

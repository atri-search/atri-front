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

from flask import render_template, request, flash, redirect, url_for
import requests

from atri.config import BASE_API_URL
from . import collection_blueprint as bp


# ------------------------------------------ Collection CRUD -------------------------------------------------------- #

@bp.route("/collection/<string:collection_name>/page/<int:page>", methods=['GET'])
def collection_page(collection_name, page):
    base_link = f"{BASE_API_URL}/collection/{collection_name}"
    try:
        response = requests.get(base_link, params={'page': page}).json()
        coll = response["collection"]
        fl = response.get("files", [])
        total_pages = response.get("pages", 1)
        current_page = response.get("current_page", 1)
    except (requests.exceptions.RequestException, KeyError):
        return render_template("error.html")
    return render_template("file-list.html", collection=coll, files=fl, defaults=coll['index_defaults'],
                           total_pages=total_pages, current_page=current_page)


@bp.route("/collection/<string:collection_name>", methods=['GET', 'POST', 'DELETE'])
def collection(collection_name):
    base_link = f"{BASE_API_URL}/collection/{collection_name}"
    if request.method == 'GET':
        try:
            response = requests.get(base_link, params={'page': 1}).json()
            coll = response["collection"]
            fl = response.get("files", [])
            total_pages = response.get("pages", 1)
            current_page = response.get("current_page", 1)
        except (requests.exceptions.RequestException, KeyError):
            return render_template("error.html")
        return render_template("collection.html", collection=coll, files=fl, defaults=coll['index_defaults'],
                               total_pages=total_pages, current_page=current_page)
    elif request.method == 'POST':
        import json as j

        data = request.form

        new_name = data.get('name', collection_name)
        new_name = new_name if new_name != collection_name else None

        index_defaults = data.get('advanced', None)
        index_defaults = j.loads(index_defaults) if index_defaults else {}

        request_data = {
            "name": new_name,
            "description": data.get('description', None),
            "index_defaults": index_defaults
        }

        try:
            response = requests.put(BASE_API_URL + f'/collection/{collection_name}', json=request_data)
        except requests.exceptions.RequestException:
            return render_template("error.html")

        json_response = response.json()

        if 'error' in json_response:
            flash("[ERROR] " + json_response['error'])
        elif 'success' in json_response:
            flash(json_response['success'])

        return redirect(url_for("collection.collection", collection_name=request_data['name'] if request_data['name']
                        else collection_name))

    elif request.method == 'DELETE':
        response = None
        try:
            response = requests.delete(BASE_API_URL + f"/collection/{collection_name}")
        except requests.exceptions.RequestException:
            flash("[ERROR] Unexpected error")

        if response.status_code == 204:  # no content
            flash("[SUCCESS] Collection deleted")
        else:
            flash("[ERROR] Collection not found")
            return render_template("error.html")

        return "process finished"


@bp.route("/collection/register", methods=['GET', 'POST'])
def register_collection():
    if request.method == 'GET':
        return render_template("collection_register.html")

    data = request.form
    request_data = {
        "name": data['name'],
        "description": data['description']
    }
    try:
        response = requests.post(BASE_API_URL + '/collection', json=request_data)
    except requests.exceptions.RequestException:
        return render_template("error.html")

    json = response.json()

    if 'error' in json:
        flash("[ERROR] " + json['error'])
        return redirect(request.url)
    elif 'success' in json:
        flash(json['success'])

    return redirect(url_for("collection.collection", collection_name=data['name']))

# ------------------------------------------ File CRUD -------------------------------------------------------- #


@bp.route("/collection/<string:collection_name>/upload", methods=['POST'])
def upload_files(collection_name):
    file_up = request.files.getlist("file")

    send_file = [('files', (file.filename, file.stream, file.mimetype)) for file in file_up]
    try:
        response = requests.post(BASE_API_URL + f"/collection/{collection_name}/file/upload",
                                 files=send_file)
    except requests.exceptions.RequestException:
        flash("[ERROR] Unexpected error.")
        return redirect(url_for("collection.collection", collection_name=collection_name))

    json = response.json()

    if 'error' in json:
        flash("[ERROR] " + json['error'])
    elif 'success' in json:
        flash(json['success'])

    return redirect(url_for("collection.collection", collection_name=collection_name))


@bp.route("/collection/<string:collection_name>/<string:filename>", methods=['GET', 'DELETE'])
def manage_collection_file(collection_name, filename):
    response = None
    if request.method == 'GET':
        try:
            response = requests.get(BASE_API_URL + f"/collection/{collection_name}/{filename}")
        except requests.exceptions.RequestException:
            flash("[ERROR] Unexpected error")

        if response:
            file_content = response.json()
        else:
            file_content = {"error": "Unexpected error"}

        return render_template('file-show.html', filename=filename, filecontent=file_content)

    try:
        response = requests.delete(BASE_API_URL + f"/collection/{collection_name}/{filename}")
    except requests.exceptions.RequestException:
        flash("[ERROR] Unexpected error")

    if response:
        json = response.json()
        if 'error' in json:
            flash("[ERROR] " + json['error'])
        if 'success' in json:
            flash(json['success'])

    return "finished process"


# ---------------------------------------------- Collection Process  -------------------------------------------------#

@bp.route("/collection/<string:collection_name>/process", methods=['GET'])
def process_collection(collection_name):
    try:
        response = requests.post(BASE_API_URL + f"/index/{collection_name}")

    except requests.exceptions.RequestException:
        flash("[ERROR] Unexpected error")
        return render_template("error.html")

    if response.status_code == 200:
        flash("[SUCCESS] Collection indexed.")
    else:
        flash("[ERROR] Indexing error.")

    return "collection processed"

# Copyright 2020 Marcos Pontes. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.

#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.

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

# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of MARCOS PONTES.

"""
    UI Application of atri tool.
"""
import json

import requests
from flask import request, url_for
from flask import Flask, render_template

from atri.config import BASE_API_URL, FRONT_IP, FRONT_PORT

app = Flask(__name__)
app.config['SECRET_KEY'] = 'atri_is_cool'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

from atri.info import info_blueprint

app.register_blueprint(info_blueprint)

from atri.collection import collection_blueprint

app.register_blueprint(collection_blueprint)

from atri.search import search_blueprint

app.register_blueprint(search_blueprint)


@app.errorhandler(404)
def page_not_found(error):
    """
        Handler para erros inesperados.
    """
    return render_template("error.html", error=error)


def macro_collections():
    """
        Macro que coleta metadados sobre todas coleções presentes no sistema de arquivos do atri.
    """
    response = requests.get(f"{BASE_API_URL}/collection")

    try:
        collections = response.json()['collections']
    except KeyError:
        return []

    return collections


def redirect_url(default='search.home'):
    """
        Macro para redirecionar url.
    """
    return request.args.get('next') or request.referrer or url_for(default)


def to_pretty_json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      indent=2, separators=(',', ': '))


app.jinja_env.filters['tojson_pretty'] = to_pretty_json
app.jinja_env.globals.update(macro_collections=macro_collections)

if __name__ == "__main__":
    app.run(FRONT_IP, port=FRONT_PORT, debug=False)

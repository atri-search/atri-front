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
import requests
from flask import render_template, request, flash
from . import info_blueprint as bp
from ..config import BASE_API_URL


@bp.route("/docs", methods=['GET'])
def about_us():
    return render_template("index.html")


@bp.route("/integrations", methods=['GET'])
def integrations():
    return render_template("integrations.html")


@bp.route("/eval", methods=['POST'])
def eval():
    # receive data from ajax
    data = request.get_json()
    ground_truth = [int(value) if int(value) >= 0 else 0 for value in data.get('relevance_feedback', [])]
    at_k = len(data.get('relevance_feedback', []))

    precision = 0.0
    ndcg = 0.0

    if sum(ground_truth) > 0:

        # evaluate data
        try:
            response = requests.post(BASE_API_URL + f"/eval", json={
                "ground_truth": ground_truth,
                "metrics": [f"precision@{at_k}", f"ndcg@{at_k}"]
            }).json()

            precision = response.get("precision@{}".format(at_k), 0.0)
            ndcg = response.get("ndcg@{}".format(at_k), 0.0)

        except requests.exceptions.RequestException:
            flash("[ERROR] Unexpected error")

    return {
        "precision": precision,
        "ndcg": ndcg
    }


from flask import Flask, request, jsonify, after_this_request
from tweet_analysis import runscripts

app = Flask(__name__)

@app.route('/', methods=['GET'])
def run():
    @after_this_request
    def add_header(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    runscripts()
    jsonResp = "Complete"
    print(jsonResp)
    return jsonify(message=jsonResp)


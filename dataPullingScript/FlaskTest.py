from flask import Flask, request, jsonify, after_this_request
from tweet_analysis import runscripts
app = Flask(__name__)



@app.route('/hello2', methods=['GET'])
def run():
    @after_this_request
    def add_header(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    runscripts()
    jsonResp = "Complete"
    print(jsonResp)
    return jsonify(jsonResp)

if __name__ == '__main__':
    app.run(host='localhost', port=3000)
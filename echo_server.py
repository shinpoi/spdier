from flask import Flask, request
from werkzeug.routing import Rule

app = Flask(__name__)

app.url_map.add(Rule('/', endpoint='echo'))
app.url_map.add(Rule('/<path>', endpoint='echo'))

@app.endpoint('echo')
def echo_server(**kwargs):
    url = request.full_path
    method = request.method
    header = request.headers
    data = request.data.decode()


    return f'''======
Raw: {request}
URL: {method} {url}
--
header:
{header}
--
data:
{data}
'''

if __name__ == "__main__":
    app.run('127.0.0.1', 8080)
    # app.run('0.0.0.0', 8080)

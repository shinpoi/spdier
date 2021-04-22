from flask import Flask, request

app = Flask(__name__)
@app.route("/")
@app.route("/<path:path>")
def echo_server(path):
    url = request.full_path
    method = request.method
    header = request.headers
    data = request.data.decode()


    return f'''======
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

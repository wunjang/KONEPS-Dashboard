from flask import Flask, render_template
from flask import request
from bokeh.embed import server_document

app = Flask(__name__)

@app.route('/')
def index():
    args = request.args
    script = server_document('http://13.211.37.124:5006/KONEPS-Dashboard', arguments=args)
    return render_template('index.html', script=script)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

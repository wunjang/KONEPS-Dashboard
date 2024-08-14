from flask import Flask, render_template
from bokeh.embed import server_document

app = Flask(__name__)

@app.route('/')
def index():
    script = server_document('http://3.27.183.61:5006/KONEPS-Dashboard')
    return render_template('index.html', script=script)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

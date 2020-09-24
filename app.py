import os
from flask import Flask

app = Flask(__name__)

@app.route('/api')
def home():
    return '<h1>Welcome to the Flames of Exile landing page.</h1>'


if __name__ == '__main__':
    app.run()
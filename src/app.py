# Description: This file is the main file for the server. It will handle all the requests and responses from the client.
from flask import Flask, render_template, request
#from waitress import serve

app = Flask(__name__)

@app.route('/')

def index():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True) #default port is 5000, look at the terminal to see the port number
    #app.run(host="0.0.0.0", port="8000", debug=True)
    #serve(app, host="0.0.0.0", port="8000")
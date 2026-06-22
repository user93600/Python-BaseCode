from flask import Flask,jsonify

app=Flask(__name__)

@app.route('/api/data')
def get_data():
    sample=[
        {"id":1,"value":42},
        {"id":2,"value":87}
    ]
    return jsonify(sample)

if __name__=="__main__":
    app.run(host="127.0.0.1",port=5000,debug=True)
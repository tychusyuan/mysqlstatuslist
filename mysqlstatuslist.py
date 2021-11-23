import pymysql
import socket
import json
import sys
from flask import Flask, request, jsonify, render_template, make_response, send_from_directory

app = Flask(__name__)

def performance_schema(item):
    db = pymysql.connect(host=item['host'],
                        port=item['port'],
                        user=item['user'],
                        password=item['pwd'],
                        database='performance_schema',
                        charset='utf8mb4')
    
    cursor = db.cursor()
    
    sql = "select * from performance_schema.global_status union all select 'servertime',now()"
    try:
        cursor.execute("set session max_execution_time=0")
        cursor.execute(sql)
        return cursor.fetchall()
    except:
        print ("Error: unable to fetch data")
        return {}
    finally:
        db.close()

@app.route('/stats', methods=['POST'])
def stats():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
        
    hosts = request.json.get('hosts', None)
    if hosts is None:
        return jsonify({"msg": "Missing hosts parameter"}), 400

    result = []
    for item in hosts:
        result.append({item['host']+"_"+str(item['port']):performance_schema(item)})

    return jsonify({"result": result}), 200 

@app.route('/', methods=['GET'])
def indx():
    return render_template('index.html',result={})

if __name__ == "__main__":
    app.debug = False
    app.run(port=8080)
from flask import Flask, request, jsonify
import psycopg2, json, uuid, os
app = Flask(__name__)

def get_db():
    return psycopg2.connect(host=os.getenv('DB_HOST','postgres'), dbname='orders_db', user='postgres', password='password')

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    order_id = str(uuid.uuid4())
    corr_id = request.headers.get('X-Correlation-Id', str(uuid.uuid4()))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO orders (id, status, data) VALUES (%s,'CREATED',%s)", (order_id, json.dumps(data)))
    cur.execute("INSERT INTO outbox (event_type, payload, correlation_id) VALUES ('order.created', %s, %s)", (json.dumps({"order_id":order_id}), corr_id))
    conn.commit()
    return jsonify({"order_id": order_id, "status": "CREATED"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
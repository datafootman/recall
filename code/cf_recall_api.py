from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from models import RecallModel, recall_interface, read_data, update_matrices

app = Flask(__name__)
model = RecallModel(num_users=1000000, num_items=100000, long_term_decay=0.99, short_term_decay=0.9)
executor = ThreadPoolExecutor(max_workers=10)  # 控制并发数量


@app.route('/cf_recall', methods=['POST'])
def cf_recall():
    user_id = int(request.args.get('user_id'))
    top_k = int(request.args.get('top_k', 10))
    future = executor.submit(recall_interface, model, user_id, top_k)
    recommendations = future.result()
    return jsonify(recommendations)


@app.route('/update', methods=['POST'])
def update():
    executor.submit(update_matrices, model)
    return jsonify({"status": "update in progress"}), 202


@app.route('/save', methods=['POST'])
def save():
    long_term_path = request.form.get('long_term_path')
    short_term_path = request.form.get('short_term_path')
    executor.submit(model.save_matrices, long_term_path, short_term_path)
    return jsonify({"status": "save in progress"}), 202


@app.route('/load', methods=['POST'])
def load():
    long_term_path = request.form.get('long_term_path')
    short_term_path = request.form.get('short_term_path')
    executor.submit(model.load_matrices, long_term_path, short_term_path)
    return jsonify({"status": "load in progress"}), 202


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8013, threaded=True)

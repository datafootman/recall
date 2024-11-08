from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# 假设这些是可用的episode_key
AVAILABLE_EPISODES = ["059cQQsbyk", "A12bCQWxyz", "B34dPDQwrl", "C56fQRTyui", "D78gSTUvwx"]

# # 实例化RecallModel
# storage_dir = '/path/to/storage'
# recall_model = RecallModel(long_term_decay=0.9, short_term_decay=0.7, storage_dir=storage_dir)
#
# # 加载之前的矩阵和indices
# recall_model.load_matrices()
# recall_model.load_indices()


@app.route('/recall/long_term', methods=['GET'])
def long_term_recall():
    user_id = request.args.get('user_id')
    top_k = int(request.args.get('top_k', 10))

    if user_id:
        result = recall_model.recall(user_id, top_k)
        return jsonify(result['long_term_recall'])
    else:
        return jsonify([])


@app.route('/recall/short_term', methods=['GET'])
def short_term_recall():
    user_id = request.args.get('user_id')
    top_k = int(request.args.get('top_k', 10))

    if user_id:
        result = recall_model.recall(user_id, top_k)
        return jsonify(result['short_term_recall'])
    else:
        return jsonify([])


@app.route('/recall/random_fake', methods=['GET'])
def random_fake_recall():
    user_id = request.args.get('user_id')
    top_k = int(request.args.get('top_k', 10))

    if user_id:
        random_episodes = random.sample(AVAILABLE_EPISODES, min(top_k, len(AVAILABLE_EPISODES)))
        return jsonify(random_episodes)
    else:
        return jsonify([])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8013, threaded=True)

from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# 假设这些是可用的episode_key
AVAILABLE_EPISODES = [
    "059cQQsbyk",
    "05haASFSfP",
    "05u3FCawAE",
    "06qiECB8Fx",
    "08MxnynTXP",
    "08RUUE0mjq",
    "08wPlOBsAg",
    "09CMMG1N4Q",
    "0Axt6jRB1B",
    "0CZchtO87g",
    "0D0SNa8Gc4",
    "0DGDWWb5WM",
    "0DaEtmrGJx",
    "0EEQFJbtZm",
    "0EZsD40qfb",
    "0Gcgn1bzwI",
    "0Gw7rdTGtX",
    "0HakGUmuxC",
    "0L7abWo4qT",
    "0LcxETITQj",
    "0Ma4qqMEv1",
    "0NBfEQuBfu",
    "0NSEZG6om9",
    "0NuWwyqGbW",
    "0Oupl8jf0c",
    "0PsWzZclHA",
    "0Shsg225tQ",
    "0T5uUX0xay",
    "0TCg8xYz6m",
    "0TJMZ9jIKl",
    "0ZmYM4yu0w",
    "0bu20wegAs",
    "0cfyagx0w3",
    "0cq2JpI8NM",
    "0eSjoLStBE",
    "0eWpnOm24W",
    "0fwgSwEX75",
    "0gBXpAWOlF",
    "0hBVIDprLx",
    "0hIhzcfi1A",
    "0iGmBQhDe9",
    "0kg9GKbJ6g",
    "0lZeHNggM5",
    "0q9rR4sfwc",
    "0qC2Z8ix0s",
    "0t2TQue27u",
    "0tXym2HTzR",
    "0tcEoIGX1g",
    "0u2l2C7SnK",
    "0uapYO5Kac",
    "0v2Wog6Wwf",
    "0vXjMsMcQj",
    "0wJepCLgvB",
    "0wKhPEbaVQ",
    "0x9I3lAGLE",
    "0yWs84Xdsa",
    "13v7fO847S",
    "14Mfpo0c1D",
    "15YfPNbEWE",
    "16YbACilsz",
    "17HONVk4ep",
    "18hz7eOV7t",
    "19aeQdjiiO",
    "1BLJYX5EBE",
    "1CcLJwYkGT",
    "1DibhcJgRo",
    "1E1LasmAr9",
    "1Gjz7WfPL6",
    "1HzmmbtQT6",
    "1K5kOrIcYJ",
    "1LDHtUZ1Y9",
    "1LMNS0aFOz",
    "1Lpazh434A",
    "1MEimA2CcN",
    "1MKxmKvJm1",
    "1OMKX5q0yg",
    "1OnlsDXpoa",
    "1REnbrUULY",
    "1RiMQDCHYm",
    "1SsQQ8OJfM",
    "1TLBpWlYBw",
    "1VKCkrjz8t",
    "1XJouCRFBT",
    "1ZIlodVuW4",
    "1aiQbl6Mpg",
    "1bCINGxYGo",
    "1bSl0xuRHo",
    "1eTxRRP4ch",
    "1ejQRSX79r",
    "1gaAiFeUp8",
    "1glPELPKR9",
    "1gp2OXNZkH",
    "1gvODUWgq0",
    "1kmQe5W5vU",
    "1lJLd4Nv47",
    "1llOsW7Gxd",
    "1nEPD3JFR8",
    "1nP2NuqT8g",
    "1oOoTJkZuk",
    "1oYp4me9OQ",
    "1oxGEFNCxv",
    "1qvM6QMyj3",
    "1qyuwyEgy2",
    "1roIUWYiEt",
    "1sQtZMFUoF",
    "1t6nsWaKgq",
    "1yCJ3SEux1",
    "1yuTUf6lTH",
    "1zO5Qd0FaV",
    "1zb7puVjeR",
    "24JthN1Ck3",
    "25NMSkJ40F",
    "28x63LoZGb",
    "29FKPzQLee",
    "2CF1jWPs85",
    "2Citj7zFWR",
    "2CoeMU2Siw",
    "2DAvP9GYlF",
    "2F3OF6nmrT",
    "2HRavyC3xX",
    "2Ii6RfS9aO",
    "2JuetEMYFB",
    "2NcwPz6oto",
    "2SVYC0uCA7",
    "2U32oRCwVO",
    "2UGR8w2zz1",
    "2UMHOjRr37",
    "2UettHcGdN",
    "2UfYDyR7PH",
    "2VA6WBRRNv",
    "2WF6B0ApOH",
    "2WIG3Ok4RC",
    "2WJbtLxVcv",
    "2X5tRyP8if",
    "2XVywkdcby",
    "2YfaK1SZzx",
    "2aMz63FpIs",
    "2acZN6R19A",
    "2b7tBDheWF",
    "2eWYI6USTU",
    "2evJXRdzxj",
    "2fMv6tUsia",
    "2fjFuIqRHL",
    "2h4dhU9kXc",
    "2kWUxYGvxY",
    "2l53mn0f0n",
    "2lXjwR3yZJ",
    "2mFwDh6DhX",
    "2mURRTeR4P",
    "2qyIGiUVKm",
    "2sO5KTgAGy",
    "2sRgqF5c04",
    "2tlPSD4tGr",
    "2vmLaCJEBb",
    "2w1MKQdWps",
    "2wzenTvxzS",
    "2xpadPlMTf",
    "2y2XadzwvR",
    "2zngyMtzGp",
    "30ToSvxMY5",
    "31D2eqrmwg",
    "31k1hypMTB",
    "337PcCjZcO",
    "341xRRHWPd",
    "358LIxbXn7",
    "37IJzATNVG",
    "39CSDBQ8at",
    "3Ad22iQg7p",
    "3BizRdPZLj",
    "3DpKlJR3mR",
    "3E1JcKBlKf",
    "3EHoUQXBnY",
    "3Ey895NDF4",
    "3HKvUou6bD",
    "3Iy3e6vkI7",
    "3K17kBPlyP",
    "3KZC78PSDc",
    "3KcxRHtnzi",
    "3L78T2YVW7",
    "3LQwXxqrSv",
    "3LtRtpe06x",
    "3MvcUrPgXp",
    "3N4aqbcLOZ",
    "3OXZlVrX3d",
    "3PdxRIe7dH",
    "3Q3sf9RHjP",
    "3RhHa58Y1U",
    "3UCA911qoN",
    "3X6bCEko7j",
    "3XAbC9y7IF",
    "3Z20a9aNTs",
    "3fp1EG7ngm",
    "3gL8VCwhDn",
    "3iAzgMY0c1",
    "3jJvnJJ0bI",
    "3jyIgU3F17",
    "3lCVjdalen",
    "3liwHJjOdn",
    "3mJV8R3wLj",
    "3n28NiLFP7"
]

@app.route('/recall/long_term', methods=['POST'])
def long_term_recall():
    user_id = request.args.get('user_id')
    top_k = int(request.args.get('top_k', 10))

    if user_id:
        random_episodes = random.sample(AVAILABLE_EPISODES, min(top_k, len(AVAILABLE_EPISODES)))
        response = {
            "user_id": user_id,
            "long_term_recall": random_episodes
        }
        return jsonify(response)
    else:
        return jsonify({
            "error": "User ID is required"
        }), 400


@app.route('/recall/short_term', methods=['POST'])
def short_term_recall():
    user_id = request.args.get('user_id')
    top_k = int(request.args.get('top_k', 10))

    if user_id:
        random_episodes = random.sample(AVAILABLE_EPISODES, min(top_k, len(AVAILABLE_EPISODES)))
        response = {
            "user_id": user_id,
            "short_term_recall": random_episodes
        }
        return jsonify(response)
    else:
        return jsonify({
            "error": "User ID is required"
        }), 400


@app.route('/recall/random_fake', methods=['POST'])
def random_fake_recall():
    user_id = request.args.get('user_id')
    top_k = int(request.args.get('top_k', 10))

    if user_id:
        random_episodes = random.sample(AVAILABLE_EPISODES, min(top_k, len(AVAILABLE_EPISODES)))
        response = {
            "user_id": user_id,
            "random_fake_recall": random_episodes
        }
        return jsonify(response)
    else:
        return jsonify({
            "error": "User ID is required"
        }), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8013, threaded=True)

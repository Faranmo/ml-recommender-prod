from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# Recommend function
def recommend_for_user(user_id):
    recommendations = [random.randint(1000, 1100) for _ in range(5)]
    return recommendations

@app.route('/')
def home():
    return jsonify({"message": "Recommender API is running!"})

@app.route('/recommend', methods=['GET'])
def recommend():
    user_id = request.args.get('user_id', default=1, type=int)
    recommendations = recommend_for_user(user_id)
    return jsonify({"user_id": user_id, "recommendations": recommendations})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

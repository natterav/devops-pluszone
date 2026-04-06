from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text", "").lower()

    skills = []

    if "javascript" in text:
        skills.append("JavaScript")
    if "python" in text:
        skills.append("Python")
    if "react" in text:
        skills.append("React")

    return jsonify({
        "skills": skills,
        "score": len(skills) * 20
    })

@app.route("/")
def home():
    return "Python service running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

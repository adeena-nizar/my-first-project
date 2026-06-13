import os
import re
from collections import Counter
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


def summarize(text: str, num_sentences: int = 5) -> str:
    text = text.strip()
    if not text:
        return "Please paste some notes to summarize."

    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) <= num_sentences:
        return " ".join(sentences)

    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    stopwords = {
        "the", "and", "for", "are", "was", "were", "but", "not", "you",
        "this", "that", "with", "have", "from", "they", "will", "been",
        "has", "had", "its", "also", "more", "can", "all", "one", "our",
        "into", "than", "then", "when", "where", "which", "who", "how",
        "what", "there", "their", "would", "could", "should", "such",
        "about", "after", "before", "between", "each", "many", "most",
        "other", "over", "same", "some", "these", "those", "through",
    }
    filtered = [w for w in words if w not in stopwords]
    freq = Counter(filtered)

    def score(sentence):
        tokens = re.findall(r'\b[a-zA-Z]{3,}\b', sentence.lower())
        return sum(freq.get(t, 0) for t in tokens if t not in stopwords)

    ranked = sorted(enumerate(sentences), key=lambda x: score(x[1]), reverse=True)
    top_indices = sorted([i for i, _ in ranked[:num_sentences]])
    summary = " ".join(sentences[i] for i in top_indices)
    return summary


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/summarize", methods=["POST"])
def summarize_route():
    data = request.get_json(silent=True) or {}
    notes = data.get("notes", "")
    if not notes.strip():
        return jsonify({"error": "No notes provided."}), 400
    result = summarize(notes)
    return jsonify({"summary": result})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)

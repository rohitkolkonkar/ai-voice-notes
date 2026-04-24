from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route('/')
def index():
    return send_file('ai_voice_note_summarizer.html')

@app.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.json
    transcript = data.get('transcript', '')

    if not transcript:
        return jsonify({'error': 'Transcript is required'}), 400

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GROQ_API_KEY}'
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert at extracting structured intelligence from voice notes and meeting transcripts.\nReturn ONLY a JSON object with NO markdown, NO backticks, NO preamble. Exactly this shape:\n{\n  \"tldr\": \"One crisp sentence capturing the core message.\",\n  \"keyPoints\": [\"point 1\", \"point 2\", \"point 3\"],\n  \"actionItems\": [\"action 1\", \"action 2\", \"action 3\"],\n  \"sentiment\": \"positive|neutral|urgent|mixed\",\n  \"wordCount\": 120\n}\nRules: keyPoints = 3-5 insight bullets. actionItems = 2-6 concrete tasks (start each with a verb). Keep everything under 20 words per item."
            },
            {
                "role": "user", 
                "content": f"Voice note transcript:\n\n\"{transcript}\""
            }
        ],
        "response_format": { "type": "json_object" }
    }

    try:
        # Use Groq's openai-compatible endpoint
        response = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        raw_content = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
        return jsonify({'result': raw_content})

    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if response is not None and hasattr(response, 'json'):
            try:
                error_msg = response.json().get('error', {}).get('message', error_msg)
            except:
                pass
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

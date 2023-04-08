from flask import Flask, request, jsonify
import os
import tempfile
import requests
from dotenv import load_dotenv
import replicate
import openai


load_dotenv()

# Initialize the OpenAI API
api_key = os.environ.get('OPENAI_API_KEY')
openai.api_key = api_key

app = Flask(__name__, static_folder='.', static_url_path='')
REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN')

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    print("Received request")  # Add this line

    # Get the audio file from the request
    audio = request.files['audio']

    # Save the audio file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        audio.save(fp)
        audio_file_path = fp.name

    # Run the Replicate model on the audio file
    output = replicate.run(
        "openai/whisper:e39e354773466b955265e969568deb7da217804d8e771ea8c9cd0cef6591f8bc",
        input={"audio": open(audio_file_path, "rb")}
    )

    print("Transcription result: ", output)  # Add this line

    # Cleanup: delete the temporary audio file
    os.remove(audio_file_path)

    return jsonify(output)

# You are a helpful assistant that summarizes text. When I provide you with a text block containing human conversation, please analyze and summarize the main ideas or key points discussed, while keeping the essence of the dialogues intact. To improve readability and organization, kindly include markup and headings where helpful. This will not only assist me in quickly grasping the important aspects of the conversation but also make the information more accessible and easy to navigate. Your attention to detail and clear structure will enable me to understand and respond effectively.

@app.route('/summarize', methods=['POST'])
def summarize_text():
    data = request.get_json()
    text = data['text']

    # Summarize the text using GPT-3.5-turbo from the OpenAI API
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "When I provide you with a text block containing human conversation, please analyze and summarize the main ideas or key points discussed, while keeping the essence of the dialogues intact. To improve readability and organization, kindly include markup and headings where helpful. This will not only assist me in quickly grasping the important aspects of the conversation but also make the information more accessible and easy to navigate. Your attention to detail and clear structure will enable me to understand and respond effectively."},
                    {"role": "user", "content": f"Please summarize this succinctly. Use bullet points where helpful: {text}"}
                ],
                "max_tokens": 100,
                "n": 1,
                "temperature": 0.7
            }

        )

        response.raise_for_status()  # Raise an exception if there's an error
        json_response = response.json()
        summary = json_response['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        print("Error calling OpenAI API:", e)
        summary = "Error: Cannot summarize text due to a connection issue with the OpenAI API. Please check the server logs for more details."
    except Exception as e:
        print("Unexpected error:", e)
        summary = "Error: Unexpected error while summarizing text. Please check the server logs for more details."

    return jsonify({"summary": summary})


@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)
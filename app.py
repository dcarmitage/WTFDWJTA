from flask import Flask, request, jsonify
import os
import tempfile
import replicate

app = Flask(__name__, static_folder='.', static_url_path='')
API_TOKEN = os.environ['REPLICATE_API_TOKEN']

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

@app.route('/summarize', methods=['POST'])
def summarize_text():
    data = request.get_json()
    text = data['text']

    # Summarize the text using a function or an API of your choice
    summary = text  # Replace this line with summarization logic

    return jsonify({"summary": summary})

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)
// Recording
let chunks = [];
let recorder;
let audioBlob;

const startButton = document.getElementById('startRecording');
const stopButton = document.getElementById('stopRecording');
const playButton = document.getElementById('playRecording');
const downloadLink = document.getElementById('downloadRecording');
const transcribeButton = document.getElementById('transcribe');
const summaryButton = document.getElementById('summarize');
const transcriptionArea = document.getElementById('transcription');
const summaryArea = document.getElementById('summary');

startButton.onclick = async () => {
    chunks = [];
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        recorder = new MediaRecorder(stream);
        recorder.ondataavailable = e => chunks.push(e.data);
        recorder.onstop = exportRecording;
        recorder.start();
        startButton.disabled = true;
        stopButton.disabled = false;
    } catch (error) {
        console.error('Error starting the recording:', error);
        alert('An error occurred while starting the recording. Please check the console for more details.');
    }
};

stopButton.onclick = () => {
    recorder.stop();
    startButton.disabled = false;
    stopButton.disabled = true;
};

playButton.onclick = () => {
    const audio = new Audio(URL.createObjectURL(audioBlob));
    audio.play();
};

// Save recorded audio and enable playback and transcription
function exportRecording() {
    audioBlob = new Blob(chunks, { type: 'audio/ogg; codecs=opus' });
    const url = URL.createObjectURL(audioBlob);

    downloadLink.href = url;
    downloadLink.download = 'recording.ogg';
    downloadLink.style.display = 'block';

    playButton.disabled = false;
    transcribeButton.disabled = false;
}

// Transcription and Summarization
const SERVER_URL = 'http://127.0.0.1:5000';

transcribeButton.onclick = async () => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.ogg');

    const spinner = document.getElementById('spinner');
    spinner.style.display = 'block'; // Show the spinner

    transcribeButton.disabled = true;

    try {
        const response = await fetch(SERVER_URL + '/transcribe', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const jsonResponse = await response.json();
            const transcriptionText = jsonResponse.transcription;

            transcriptionArea.textContent = transcriptionText;
            summaryButton.disabled = false;
        } else {
            throw new Error(`Transcription request failed with status ${response.status}`);
        }
    } catch (error) {
        console.error('Error during transcription:', error);
        alert('An error occurred while transcribing the audio. Please check the console for more details.');
        transcribeButton.disabled = false;
    } finally {
        spinner.style.display = 'none'; // Hide the spinner
    }
};

summaryButton.onclick = async () => {
    summaryButton.disabled = true;

    try {
        const response = await fetch(SERVER_URL + '/summarize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: transcriptionArea.textContent })
        });

        if (response.ok) {
            const { summary } = await response.json();
            summaryArea.textContent = summary;
        } else {
            throw new Error(`Summarization request failed with status ${response.status}`);
        }
    } catch (error) {
        console.error('Error during summarization:', error);
        alert('An error occurred while summarizing the text. Please check the console for more details.');
        summaryButton.disabled = false;
    }
};
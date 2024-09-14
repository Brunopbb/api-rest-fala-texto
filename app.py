from flask import Flask, request, jsonify
from flask import render_template
from huggingface_hub import login
from datasets import DatasetDict, Dataset, Audio, load_dataset, concatenate_datasets
from flask_cors import CORS
from dotenv import load_dotenv
import os
import io
import soundfile as sf
from pydub import AudioSegment

from data_process import *


app = Flask(__name__)
CORS(app)

load_dotenv()
huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
huggingface_id = os.getenv("HUGGINGFACE_REPO_ID")

login(huggingface_token)



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload-audio', methods=["POST"])
def upload_audio():
    if 'audios' not in request.files:
        return jsonify({"Error": "Nehnum arquivo foi enviado"}), 400
    
    audio_files = request.files.getlist("audios")
    transcriptions = get_transcription(audio_files)

    if len(audio_files) == 0 or len(audio_files) > 10:
        jsonify({"Error": "Envie apenas 10 audios por vez"}), 400

    exists_dataset = None

    try:
        exists_dataset = load_dataset(huggingface_id, split="train")
        exists_transcriptions = set(exists_dataset['transcription'])
    except FileNotFoundError:
        exists_dataset = None
        exists_transcriptions = set()
    
    data = {
            'audio': [],
            'transcription': []
        }
    
    for audio_file, text in zip(audio_files, transcriptions):
        if audio_file.filename == "" or text in exists_transcriptions:
            continue
    
        audio_data = audio_file.read()

        audio = AudioSegment.from_file(io.BytesIO(audio_data))
    
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        samples, sample_rate = sf.read(wav_io)
        
        data["audio"].append({"array": samples, "sampling_rate": sample_rate})
        data["transcription"].append(text)
        
    dataset = Dataset.from_dict(data)
    dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))


    if exists_dataset:
        new_data = concatenate_datasets([exists_dataset, dataset])
    else:
        new_data = dataset

    new_data.push_to_hub(huggingface_id)
        

    return jsonify({"Mensagem": "Audios recebidos"}), 200

if __name__ == "__main__":
    app.run(debug=True,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 5000)))
    


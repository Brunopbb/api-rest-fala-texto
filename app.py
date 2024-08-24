from flask import Flask, request, jsonify
from flask import render_template
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, storage
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

load_dotenv()
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS_PATH")
firebase_bucket = os.getenv("FIREBASE_STORAGE_BUCKET")

cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred, {
    'storageBucket' : firebase_bucket
})

bucket = storage.bucket()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload-audio', methods=["POST"])
def upload_audio():
    if 'audios' not in request.files:
        return jsonify({"Error": "Nehnum arquivo foi enviado"}), 400
    
    audio_files = request.files.getlist("audios")

    if len(audio_files) == 0 or len(audio_files) > 10:
        jsonify({"Error": "Envie apenas 10 audios por vez"}), 400

    uploaded_files_urls = []

    for audio_file in audio_files:
        if audio_file.filename == "":
            continue

        blob = bucket.blob(audio_file.filename)
        blob.upload_from_file(audio_file)
        blob.make_public()

        uploaded_files_urls.append(blob.public_url)

    return jsonify({"Mensagem": "Audios recebidos"}), 200

if __name__ == "__main__":
    app.run(debug=True,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 5000)))
    

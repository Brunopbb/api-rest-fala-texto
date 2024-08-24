from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
upload_folder = "uploads"

os.makedirs(upload_folder, exist_ok=True)
app.config['upload_folder'] = upload_folder

@app.route('/upload-audio', methods=["POST"])
def upload_audio():
    if 'audios' not in request.files:
        return jsonify({"Error": "Nehnum arquivo foi enviado"}), 400
    
    audio_files = request.files.getlist("audios")

    if len(audio_files) == 0 or len(audio_files) > 10:
        jsonify({"Error": "Envie apenas 10 audios por vez"}), 400

    saved_files = []

    for audio_file in audio_files:
        if audio_file.filename == "":
            continue

        file_path = os.path.join(app.config["upload_folder"], audio_file.filename)

        audio_file.save(file_path)

        saved_files.append(audio_file.filename)

    return jsonify({"Mensagem": "Audios recebidos"}), 200

if __name__ == "__main__":
    app.run(debug=True)

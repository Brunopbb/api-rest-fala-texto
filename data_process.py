

def get_transcription(audio_list):
    transcription = [audio.filename.split('.')[0] for audio in audio_list]
    return transcription



    
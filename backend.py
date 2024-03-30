from flask import Flask, request, jsonify
import requests
from faster_whisper import WhisperModel

model_size = "medium"
model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")

app = Flask(__name__)

@app.route('/query-prices', methods=['POST'])
def query_prices():
    procedure_json = request.get_json()
    insurance_provider = procedure_json['insurance_provider']
    dict = {}
    for procedure in procedure_json['procedures']:
        print(procedure)
        answer = requests.get("https://www.dolthub.com/api/v1alpha1/dolthub/hospital-price-transparency/master?q=SELECT+*+FROM+%60prices%60+WHERE+CODE%3D\"{}\"+AND+payer+LIKE+\"%25{}%25\"+LIMIT+1%3B".format(procedure, insurance_provider))
        answer = answer.json()
        dict[procedure] =  float(answer['rows'][0]['price']) - float(procedure_json['procedures'][procedure])
    return jsonify(dict)

@app.route('/process-audio', methods=['POST'])
def process_audio():
    request.files['audio'].save("audio.mp3")

    # Use FasterWhisper to convert audio to text
    segments, info = model.transcribe("audio.mp3", beam_size=5)
    final_text = ""
    for segment in segments:
        final_text += segment.text

    return final_text

if __name__ == '__main__':
    app.run(debug = True)
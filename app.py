import os
import random

from flask import Flask, jsonify, request, send_from_directory, session

from Calcolo_probabilita import DOMANDE, lista_probabilita

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

DOMANDE = {

    1: "Il tuo personaggio è reale?",
    2: "Il tuo personaggio indossa una mascchera o un costume?",
    3: "Il tuo personaggio usa molta tecnologia?",
    4: "Il tuo personaggio ha superpoteri?"

}
MAPPA_RISPOSTE = {
    "1": 1.0,  # SÌ
    "3": 0.5,  # Non so
    "5": 0.0   # NO
}

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.route('/api/start', methods=['GET'])
def start_game():
    
    # Inizializzo le liste nella sessione se non esistono
    if 'domande_fatte' not in session:
        session['domande_fatte'] = []
    if 'risposte_fatte' not in session:
        session['risposte_fatte'] = []

    domande_rimaste = list(DOMANDE.keys())
    prossima_domanda = random.choice(domande_rimaste)

    return jsonify({

        "finished": False,
        "question_id": prossima_domanda,
        "question_text": DOMANDE[prossima_domanda],
        "progress": {

            "answered": 0,
            "total": len(DOMANDE)
        }
    })


@app.route('/api/answer', methods=['POST'])
def handle_answer():

    dati_ricevuti = request.get_json()

    id_domanda = int(dati_ricevuti.get('domanda'))
    risposta_stringa = dati_ricevuti.get('risposta')

    valore_risposta = MAPPA_RISPOSTE.get(risposta_stringa, 0.5)

    domande_fatte_temp = session.get('domande_fatte', [])
    risposte_fatte_temp = session.get('risposte_fatte', [])

    domande_fatte_temp.append(id_domanda)
    risposte_fatte_temp.append(valore_risposta)

    session['domande_fatte'] = domande_fatte_temp
    session['risposte_fatte'] = risposte_fatte_temp

    probabilita = lista_probabilita(session['domande_fatte'], session['risposte_fatte'])

    domande_rimaste = list(set(DOMANDE.keys()) - set(session['domande_fatte']))

    if len(domande_rimaste) == 0:

        risultato = sorted(probabilita, key=lambda p: p['probabilita'], reverse=True)[0]
        return jsonify({

            "finished": True,
            "result": risultato['nome']
        })
    else:
        prossima_domanda = random.choice(domande_rimaste)
        return jsonify({

            "finished": False,
            "question_id": prossima_domanda,
            "question_text": DOMANDE[prossima_domanda],
            "progress":{

                "answered": len(session['domande_fatte']),
                "total": len(DOMANDE) 

            }
        })


def next_step():
    domande_fatte = session.get("domande_fatte", [])
    risposte_fatte = session.get("risposte_fatte", [])
    domande_rimaste = list(set(DOMANDE.keys()) - set(domande_fatte))

    if not domande_rimaste:
        probabilita = lista_probabilita(domande_fatte, risposte_fatte)
        risultato = sorted(
            probabilita,
            key=lambda personaggio: personaggio["probabilita"],
            reverse=True,
        )[0]
        session.clear()
        return {
            "finished": True,
            "result": risultato["nome"],
            "probability": round(risultato["probabilita"], 4),
        }

    prossima_domanda = random.choice(domande_rimaste)
    return {
        "finished": False,
        "questionId": prossima_domanda,
        "question": DOMANDE[prossima_domanda],
        "progress": {
            "answered": len(domande_fatte),
            "total": len(DOMANDE),
        },
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

import os
import random

from flask import Flask, jsonify, request, send_from_directory, session

from Calcolo_probabilita import DOMANDE, MAPPA_RISPOSTE, lista_probabilita


app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

RISPOSTE = MAPPA_RISPOSTE


@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/start")
def start_game():
    session["domande_fatte"] = []
    session["risposte_fatte"] = []
    return jsonify(next_step())


@app.post("/api/answer")
def answer_question():
    data = request.get_json(silent=True) or {}
    domanda = data.get("domanda")
    risposta = data.get("risposta")

    if domanda is None or risposta not in RISPOSTE:
        return jsonify({"error": "Domanda o risposta non valida"}), 400

    domande_fatte = session.get("domande_fatte", [])
    risposte_fatte = session.get("risposte_fatte", [])
    domande_fatte.append(int(domanda))
    risposte_fatte.append(RISPOSTE[risposta])
    session["domande_fatte"] = domande_fatte
    session["risposte_fatte"] = risposte_fatte

    return jsonify(next_step())


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
        "question_id": prossima_domanda,
        "question_text": DOMANDE[prossima_domanda],
        "progress": {
            "answered": len(domande_fatte),
            "total": len(DOMANDE),
        },
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

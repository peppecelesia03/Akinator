import os
import random
from flask import Flask, jsonify, request, send_from_directory, session
from Calcolo_probabilita import lista_probabilita
from database import DOMANDE, MAPPA_RISPOSTE

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

# Rotta che reindirizza l'utente su index.html
@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

# Rotta che avvia il gioco ripulendo la sessione 
@app.route('/api/start', methods=['GET'])
def start_game():

    session.clear()
    # Inizializzo le liste nella sessione
    session['domande_fatte'] = []
    session['risposte_fatte'] = []

    # Scelgo la prossima domanda con la funzione random
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

    # Recuperiamo le liste della sessione dell'utente attuale e creiamo delle copie temporanee
    domande_fatte_temp = [int(x) for x in session.get('domande_fatte', [])]
    risposte_fatte_temp = [int(x) for x in session.get('risposte_fatte', [])]
    
    # Con questo mi creo una Cronologia delle domande e delle risposte già fatte
    domande_fatte_temp.append(id_domanda)
    risposte_fatte_temp.append(valore_risposta)

    # Salviamo nuovamente le liste aggiornate nella sessione
    session['domande_fatte'] = domande_fatte_temp
    session['risposte_fatte'] = risposte_fatte_temp

    # Usiamo i dati specifici dell'utente per calcolare la probabilità
    probabilita = lista_probabilita(session['domande_fatte'], session['risposte_fatte'])

    domande_rimaste = list(set(DOMANDE.keys()) - set(session['domande_fatte']))

    if len(domande_rimaste) == 0:

        # Riordino la lista mettendo in cima il personaggio con la probabilità più ALTA
        risultato = sorted(probabilita, key=lambda p: p['probabilita'], reverse=True)[0]
        session.clear()# <- l'utente puo ricaricare la pagina ed iniziare una nuova partita
        return jsonify({
            "finished": True,
            "result": risultato['nome'],
            "probability": round(risultato['probabilita'], 4)
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

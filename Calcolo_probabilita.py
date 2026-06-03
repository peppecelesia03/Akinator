import random
from flask import Flask, render_template, request, session
from database import DATABASE_PERSONAGGI

app = Flask(__name__)
app.secret_key = 'INSERIRE_CHIAVE_SEGRETA' # <- serve per evitare che l'utente manometta i dati 

DOMANDE = {

    1: "Il tuo personaggio è reale?",
    2: "Il tuo personaggio indossa una mascchera o un costume?",
    3: "Il tuo personaggio usa molta tecnologia?",
    4: "Il tuo personaggio ha superpoteri?"

}

@app.route('/')
def index():
    # Inizializzo le liste nella sessione se non esistono
    if 'domande_fatte' not in session:
        session['domande_fatte'] = []
    if 'risposte_fatte' not in session:
        session['risposte_fatte'] = []

    # Leggo le risposte inviate dal browser
    domanda = request.args.get('domanda')
    risposta = request.args.get('risposta')

    if domanda and risposta:
        # Recuperiamo le liste della sessione dell'utente attuale e creiamo delle copie temporanee
        domande_fatte_temp = session['domande_fatte']
        risposte_fatte_temp = session['risposte_fatte']

        # Con questo mi creo una Cronologia delle domande e delle risposte già fatte
        domande_fatte_temp.append(int(domanda))
        risposte_fatte_temp.append(float(risposta))

        # Salviamo nuovamente le liste aggiornate nella sessione
        session['domande_fatte'] = domande_fatte_temp
        session['risposte_fatte'] = risposte_fatte_temp

    # Usiamo i dati specifici dell'utente per calcolare la probabilità
    probabilita = lista_probabilita(session['domande_fatte'], session['risposte_fatte'])
    print('probabilità: ', probabilita)

    domande_rimaste = list(set(DOMANDE.keys()) - set(session['domande_fatte']))

    if len(domande_rimaste) == 0:
        # Riordino la lista mettendo in cima il personaggio con la probabilità più ALTA
        risultato = sorted(probabilita, key = lambda p: p['probabilita'], reverse = True)[0]
        session.clear() # <- l'utente puo ricaricare la pagina ed iniziare una nuova partita
        return render_template('index.html', risultato = risultato['nome'])
    
    else:
        prossima_domanda = random.choice(domande_rimaste) # <- prendo una domanda a caso nella lista domande_rimaste
        return render_template('index.html', domanda = prossima_domanda, domanda_testo = DOMANDE[prossima_domanda])
    
def lista_probabilita(domande_fatte, risposte_fatte):
    # In questa funzione creo la lista probabilità
    probabilita = []

    for personaggio in DATABASE_PERSONAGGI:
        probabilita.append({
            'nome': personaggio['nome'],       
            'probabilita': calcolo_probabilita_personaggio(personaggio, domande_fatte, risposte_fatte, DATABASE_PERSONAGGI)
        })
    
    return probabilita

def calcolo_probabilita_personaggio(personaggio, domande_fatte, risposte_fatte, tutti_i_personaggi):
    # La P nelle variabili sta per Probabilità

    # Fase A: inizializzo la Probabilità di partenaza uguale per tutti, nel teorema di bayes viene chiamato 'Prior'
    P_personaggio = 1 / len(tutti_i_personaggi)
    
    # --- Fase B: La somiglianza con il personaggio attuale (P_risposta_data) ---
    # Il codice esamina la cronologia delle risposte date dall'utente (zip(domande_fatte, risposte_fatte))
    # e le confronta con le risposte ideali del personaggio:
    P_risposta_data = 1
    for domanda, risposta in zip(domande_fatte, risposte_fatte):
        punteggio = 1 - abs(risposta - risposta_personaggio(personaggio, domanda))
        P_risposta_data *= max(punteggio, 0.01)

    # --- Fase C: La somiglianza con tutti gli altri personaggi (P_risposta_non_data) ---
    # Qui il codice fa la stessa identica cosa di prima,
    # ma calcola la media di quanto le risposte dell'utente somiglino a tutti gli altri personaggi del database, 
    # escludendo quello attuale (if nessun_personaggio['nome'] != personaggio['nome']).
    # Serve a capire se le risposte dell'utente sono uniche per questo personaggio o se si adattano genericamente a chiunque altro.
    P_risposta_non_data = 1
    for domanda, risposta in zip(domande_fatte, risposte_fatte): 
        altro_punteggio = []
        for nessun_personaggio in tutti_i_personaggi:
            if nessun_personaggio['nome'] != personaggio['nome']:
                punteggio = 1 - abs(risposta - risposta_personaggio(nessun_personaggio, domanda))
                altro_punteggio.append(punteggio)

        P_risposta_nessun_personaggio = sum(altro_punteggio) / len(altro_punteggio) if altro_punteggio else 0.01
        P_risposta_non_data *= max(P_risposta_nessun_personaggio, 0.01)

    # --- Fase D: Il Teorema di Bayes applicato ---
    numeratore = P_risposta_data * P_personaggio
    P_risposta = numeratore + ((1 - P_personaggio) * P_risposta_non_data)

    if P_risposta == 0:
        return 0.0
    
    P_personaggio_dato_risposte = numeratore / P_risposta
    return P_personaggio_dato_risposte

def risposta_personaggio(personaggio, domanda):
    if 'risposte' in personaggio and domanda in personaggio['risposte']:
        return personaggio['risposte'][domanda]
    elif 'risposta' in personaggio and domanda in personaggio['risposta']:
        return personaggio['risposta'][domanda]
    return 0.5     
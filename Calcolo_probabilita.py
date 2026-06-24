from database import DATABASE_PERSONAGGI

def lista_probabilita(domande_fatte, risposte_fatte):
 # La P nelle variabili sta per Probabilità

#-------------------------------------------------
# In questa sezione creo un dizionario vuoto (che serivirà a salvare i punteggi provvisori di ogni personaggio)
# e imposto a zero un contatore (somma_totale_numeratori). E con P_prior do la stessa probabilita
# ad ogni personaggio nel database

    numeratori = {}
    somma_totale_numeratori = 0.0

    P_prior = 1 / len(DATABASE_PERSONAGGI)

#-------------------------------------------------
# Qui il codice esamina un personaggio alla volta e guarda la cronologia di tutte 
# le domande fatte finora e delle risposte date dall'utente.

# abs(risposta - risposta_personaggio(personaggio, domanda))
# Calcola la distanza tra la risposta dell'utente e la risposta ideale del personaggio del database
# ESEMPIO: se la risposta alla domanda "ha superpoteri" rispondiamo SI(1.0) pensando a Bataman(0.10) la differenza sarà |1.0 - 0.10| = 0.90

# punteggio = 1 - ...
# Trasforma la distanza in un punteggio di "somiglianza". Se la distanza era 0.90,
# la somiglianza è 1 - 0.90 = 0.10. Più l'utente risponde in modo simile al database,
# più questo punteggio si avvicina a 1.0.

# max(punteggio, 0.01)
# Se l'utente dice SI ma per il database è un NO, il punteggio sarebbe 0. Moltiplicare
# per 0 azzererebbe all'istante la probabilità del personaggio per il resto della partita,
# rendendo impossibile recuperare un errore. Usando 0.01, il personaggio viene "penalizzato"
# ma non eliminato del tutto.

# P_risposta_data *= ...
# Moltiplica tra loro i punteggi di tutte le domande fatte. Se le risposte dell'utente
# combaciano con il profilo di Batman, questo valore rimmarà alto; se divergono
#crollera vicino lo zero.

    for personaggio in DATABASE_PERSONAGGI:
        
        nome = personaggio['nome']

        P_risposta_data = 1.0
        for domanda, risposta in zip(domande_fatte, risposte_fatte):
            punteggio = 1 - abs(risposta - risposta_personaggio(personaggio, domanda))
            P_risposta_data *= max(punteggio, 0.01)

#-------------------------------------------------
# Qui il programma per il personaggio corrente calcola il numeratore del Teorema di Bayes
# ovvero moltiplica la somiglianza totale appena calcolata (P_risposta_data) per la
# probabilità iniziale (P_prior)
# Salva questo valore nel dizionario associandolo al nome del personaggio
# ESEMPIO: numeratori['Batman] = 0.23
# e questo valore viene aggiunto alla variabile somma_totale_numeratori.
# Quando il ciclo for avrà finito di girare tutti i personaggi, questa variabile
# conterrà la somma dei punteggi di tutti.
# Questa somma equivale esattamente al denominatore P(E) del Teorema di Bayes(la probabilità totale delle riposte) 

        numeratore = P_risposta_data * P_prior
        numeratori[nome] = numeratore
        somma_totale_numeratori += numeratore

#-------------------------------------------------
# Qui il programmma trasforma i numeratori grezzi in percentuali reali

# numeratori[nome] / somma_totale_numeratori
# Prende il punteggio del singolo personaggio e lo divide per la somma di tutti i personaggi.
# Se il numeratore di Batman è 0.21 e la somma di tutti i numeratori è 0.24, Batman otterà
# 0.21/0.24 = 0.875 ovvero l'87.5%

# if somma_totale_numeratori > 0 else 0.0
# Serve semplicemente a evitare che il server vada in errore di "divisione per zero"
# all'inizio del gioco, quando non è stata fatta ancora nessuna domanda.

    probabilita_finali = []
    for personaggio in DATABASE_PERSONAGGI:
        nome = personaggio['nome']
        p_finale = (numeratori[nome] / somma_totale_numeratori) if somma_totale_numeratori > 0 else 0.0

        probabilita_finali.append({

            'nome': nome,
            'probabilita': p_finale

        }) 

    return probabilita_finali

#-------------------------------------------------

def risposta_personaggio(personaggio, domanda):
    
    return personaggio['risposta'].get(domanda, 0.5)
from database import DATABASE_PERSONAGGI


DOMANDE = {
    1: "Il tuo personaggio è reale?",
    2: "Il tuo personaggio indossa una mascchera o un costume?",
    3: "Il tuo personaggio usa molta tecnologia?",
    4: "Il tuo personaggio ha superpoteri?",
}

MAPPA_RISPOSTE = {
    "1": 1.0,  # Si
    "3": 0.5,  # Non so
    "5": 0.0,  # No
}


def lista_probabilita(domande_fatte, risposte_fatte):
    probabilita = []

    for personaggio in DATABASE_PERSONAGGI:
        probabilita.append(
            {
                "nome": personaggio["nome"],
                "probabilita": calcolo_probabilita_personaggio(
                    personaggio,
                    domande_fatte,
                    risposte_fatte,
                    DATABASE_PERSONAGGI,
                ),
            }
        )

    return probabilita


def calcolo_probabilita_personaggio(
    personaggio,
    domande_fatte,
    risposte_fatte,
    tutti_i_personaggi,
):
    p_personaggio = 1 / len(tutti_i_personaggi)

    p_risposta_data = 1
    for domanda, risposta in zip(domande_fatte, risposte_fatte):
        punteggio = 1 - abs(risposta - risposta_personaggio(personaggio, domanda))
        p_risposta_data *= max(punteggio, 0.01)

    p_risposta_non_data = 1
    for domanda, risposta in zip(domande_fatte, risposte_fatte):
        altri_punteggi = []
        for altro_personaggio in tutti_i_personaggi:
            if altro_personaggio["nome"] != personaggio["nome"]:
                punteggio = 1 - abs(
                    risposta - risposta_personaggio(altro_personaggio, domanda)
                )
                altri_punteggi.append(punteggio)

        media_altri = (
            sum(altri_punteggi) / len(altri_punteggi) if altri_punteggi else 0.01
        )
        p_risposta_non_data *= max(media_altri, 0.01)

    numeratore = p_risposta_data * p_personaggio
    p_risposta = numeratore + ((1 - p_personaggio) * p_risposta_non_data)

    if p_risposta == 0:
        return 0.0

    return numeratore / p_risposta


def risposta_personaggio(personaggio, domanda):
    risposte = personaggio.get("risposte", personaggio.get("risposta", {}))
    return risposte.get(domanda, 0.5)

DATABASE_PERSONAGGI = [

    {"nome": "Batman",              "risposta":{1: 0.01, 2: 0.99, 3: 0.95, 4: 0.10}},
    {"nome": "Superman",            "risposta":{1: 0.01, 2: 0.95, 3: 0.20, 4: 0.99}},
    {"nome": "Elon Musk",           "risposta":{1: 0.99, 2: 0.05, 3: 0.90, 4: 0.01}},
    {"nome": "Sherlock Holmes",     "risposta":{1: 0.05, 2: 0.10, 3: 0.05, 4: 0.01}}

]

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
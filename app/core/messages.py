"""
20 preset messages selectable by AI based on lead analysis.
Each has tags that the AI uses to match against lead categories.
"""
from dataclasses import dataclass


@dataclass
class PresetMessage:
    id: int
    name: str
    tags: list[str]          # AI uses these to match
    min_score: int           # minimum lead score to use this message
    text: str


PRESET_MESSAGES: list[PresetMessage] = [
    PresetMessage(
        id=1,
        name="ecommerce_ads",
        tags=["ecommerce", "shop", "prodotti", "vendita online", "negozio"],
        min_score=60,
        text=(
            "Ciao {page_name}! Ho visto le tue inserzioni su Facebook e ho notato che stai investendo "
            "nel marketing digitale per il tuo e-commerce. "
            "Aiuto brand come il tuo a ottimizzare le campagne e aumentare il ROAS. "
            "Ti andrebbe una chiamata veloce di 15 minuti per vedere se posso aiutarti?"
        ),
    ),
    PresetMessage(
        id=2,
        name="local_business_ads",
        tags=["locale", "ristorante", "bar", "negozio fisico", "servizi locali"],
        min_score=50,
        text=(
            "Ciao {page_name}! Ho notato le tue inserzioni nella mia zona. "
            "Lavoro con attività locali per aumentare clienti e visibilità online. "
            "Ho alcune idee specifiche per il tuo settore che potrebbero interessarti. "
            "Possiamo parlarne?"
        ),
    ),
    PresetMessage(
        id=3,
        name="real_estate",
        tags=["immobiliare", "casa", "affitto", "vendita immobili", "agenzia immobiliare"],
        min_score=65,
        text=(
            "Ciao {page_name}! Ho visto le tue campagne immobiliari su Facebook. "
            "So come generare lead qualificati per agenzie come la tua a costi molto più bassi. "
            "Hai 10 minuti questa settimana per una demo veloce?"
        ),
    ),
    PresetMessage(
        id=4,
        name="coaching_consulting",
        tags=["coach", "consulente", "formazione", "corso online", "mentoring", "training"],
        min_score=60,
        text=(
            "Ciao {page_name}! Ho visto che stai promuovendo i tuoi servizi di coaching/consulenza. "
            "Lavoro con professionisti come te per automatizzare l'acquisizione clienti e scalare il business. "
            "Ti mando alcune idee pratiche se ti interessa?"
        ),
    ),
    PresetMessage(
        id=5,
        name="beauty_wellness",
        tags=["beauty", "estetica", "benessere", "spa", "parrucchiere", "fitness", "palestra"],
        min_score=50,
        text=(
            "Ciao {page_name}! Le tue inserzioni nel settore beauty/wellness hanno attirato la mia attenzione. "
            "Aiuto centri come il tuo a riempire il calendario con appuntamenti tramite campagne mirate. "
            "Potrebbe interessarti una consulenza gratuita di 20 minuti?"
        ),
    ),
    PresetMessage(
        id=6,
        name="saas_software",
        tags=["software", "saas", "app", "tecnologia", "startup", "digital"],
        min_score=70,
        text=(
            "Ciao {page_name}! Ho visto le tue campagne per il prodotto software. "
            "Sono specializzato in growth per SaaS - acquisizione utenti, trial conversion e retention. "
            "Hai voglia di confrontarci su come scalare in modo sostenibile?"
        ),
    ),
    PresetMessage(
        id=7,
        name="food_beverage",
        tags=["food", "cibo", "ristorante", "delivery", "prodotti alimentari"],
        min_score=50,
        text=(
            "Ciao {page_name}! Ho notato le tue inserzioni nel settore food. "
            "Lavoro con brand alimentari per aumentare le vendite sia online che in store tramite strategie social mirate. "
            "Posso mostrarti qualche caso studio simile al tuo?"
        ),
    ),
    PresetMessage(
        id=8,
        name="high_spend_generic",
        tags=["alto budget", "campagna professionale", "brand nazionale"],
        min_score=80,
        text=(
            "Ciao {page_name}! Ho analizzato le vostre campagne pubblicitarie e vedo un'ottima base di lavoro. "
            "Credo ci siano margini significativi per migliorare le performance. "
            "Sarei interessato a mostrarvi un'analisi gratuita delle vostre campagne attuali. "
            "Con chi potrei parlare del marketing?"
        ),
    ),
    PresetMessage(
        id=9,
        name="event_entertainment",
        tags=["eventi", "concerti", "intrattenimento", "spettacolo", "festival"],
        min_score=55,
        text=(
            "Ciao {page_name}! Ho visto le tue inserzioni per l'evento. "
            "Aiuto organizzatori come te a riempire i posti attraverso campagne Facebook ads ottimizzate. "
            "Ti mando qualche idea su come aumentare le vendite dei biglietti?"
        ),
    ),
    PresetMessage(
        id=10,
        name="education_courses",
        tags=["educazione", "corso", "scuola", "università", "certificazione", "formazione"],
        min_score=60,
        text=(
            "Ciao {page_name}! Ho visto le tue inserzioni per il corso/formazione. "
            "So come aumentare le iscrizioni e abbassare il costo per lead per realtà educational come la tua. "
            "Hai 15 minuti questa settimana?"
        ),
    ),
    PresetMessage(
        id=11,
        name="travel_tourism",
        tags=["viaggio", "turismo", "hotel", "vacanze", "agenzia viaggi", "tour operator"],
        min_score=55,
        text=(
            "Ciao {page_name}! Ho notato le tue campagne nel settore travel. "
            "Lavoro con agenzie e strutture ricettive per aumentare le prenotazioni dirette e ridurre la dipendenza da OTA. "
            "Ti interessa una consulenza gratuita?"
        ),
    ),
    PresetMessage(
        id=12,
        name="healthcare_medical",
        tags=["salute", "medico", "clinica", "dentista", "sanità", "farmacia", "benessere"],
        min_score=65,
        text=(
            "Ciao {page_name}! Ho visto le tue inserzioni nel settore salute. "
            "Aiuto cliniche e professionisti medici ad aumentare i pazienti rispettando le normative pubblicitarie. "
            "Possiamo fare una call per discutere la vostra situazione?"
        ),
    ),
    PresetMessage(
        id=13,
        name="automotive",
        tags=["auto", "moto", "concessionario", "veicoli", "automotive"],
        min_score=60,
        text=(
            "Ciao {page_name}! Ho visto le vostre campagne nel settore automotive. "
            "Genero lead qualificati per concessionari tramite campagne Facebook ottimizzate. "
            "Vi mando un caso studio di un concessionario simile con i risultati ottenuti?"
        ),
    ),
    PresetMessage(
        id=14,
        name="fashion_clothing",
        tags=["moda", "abbigliamento", "fashion", "vestiti", "accessori", "lusso"],
        min_score=60,
        text=(
            "Ciao {page_name}! Ho notato le vostre inserzioni nel settore moda. "
            "Aiuto brand fashion a costruire un funnel di vendita efficace su Meta per aumentare le vendite online. "
            "Sarei felice di condividere alcune strategie specifiche per il vostro brand."
        ),
    ),
    PresetMessage(
        id=15,
        name="financial_services",
        tags=["finanza", "investimenti", "assicurazione", "prestiti", "credito", "banca"],
        min_score=70,
        text=(
            "Ciao {page_name}! Ho visto le vostre campagne nel settore finanziario. "
            "Lavoro con istituti e consulenti finanziari per generare lead qualificati rispettando le compliance del settore. "
            "Vi interessa un confronto?"
        ),
    ),
    PresetMessage(
        id=16,
        name="b2b_services",
        tags=["b2b", "servizi aziendali", "consulenza aziendale", "software b2b", "hr"],
        min_score=65,
        text=(
            "Ciao {page_name}! Ho analizzato le vostre inserzioni B2B. "
            "So che trovare lead aziendali qualificati su Facebook può essere una sfida. "
            "Ho sviluppato un approccio specifico per il B2B che funziona bene. "
            "Vale la pena confrontarsi 15 minuti?"
        ),
    ),
    PresetMessage(
        id=17,
        name="low_budget_newcomer",
        tags=["piccola impresa", "nuovo inserzionista", "budget basso", "prima campagna"],
        min_score=40,
        text=(
            "Ciao {page_name}! Ho visto che hai iniziato a fare inserzioni su Facebook. "
            "Complimenti per aver investito nel marketing digitale! "
            "Se vuoi, posso darti qualche consiglio gratuito per migliorare le performance delle tue campagne. "
            "Fammi sapere!"
        ),
    ),
    PresetMessage(
        id=18,
        name="retargeting_heavy",
        tags=["retargeting", "campagna avanzata", "funnel", "remarketing"],
        min_score=75,
        text=(
            "Ciao {page_name}! Ho notato che stai usando tecniche di retargeting avanzate nelle vostre campagne. "
            "Ottimo approccio! Credo possiamo portarlo al livello successivo con alcune ottimizzazioni. "
            "Hai voglia di confrontarti con un esperto del settore?"
        ),
    ),
    PresetMessage(
        id=19,
        name="home_services",
        tags=["casa", "arredamento", "ristrutturazione", "impianti", "pulizie", "giardinaggio"],
        min_score=50,
        text=(
            "Ciao {page_name}! Ho visto le tue inserzioni per i servizi casa. "
            "Lavoro con imprese del settore per generare richieste di preventivo qualificate nella zona target. "
            "Possiamo parlarne velocemente?"
        ),
    ),
    PresetMessage(
        id=20,
        name="generic_followup",
        tags=["generico", "altro"],
        min_score=45,
        text=(
            "Ciao {page_name}! Ho visto le tue inserzioni su Facebook e mi ha colpito il tuo approccio al marketing. "
            "Lavoro con imprenditori per ottimizzare le campagne pubblicitarie e aumentare il ROI. "
            "Se ti va, possiamo fare una chiamata veloce per vedere se posso esserti utile?"
        ),
    ),
]


def get_message_by_id(message_id: int) -> PresetMessage | None:
    return next((m for m in PRESET_MESSAGES if m.id == message_id), None)


def get_all_messages() -> list[PresetMessage]:
    return PRESET_MESSAGES

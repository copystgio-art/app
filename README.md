# FB Ad Library Automation

Ricerca automatica di inserzioni su Facebook Ad Library, analisi con Claude AI e invio messaggi mirati dal tuo account Facebook.

## Architettura

```
FB Ad Library (Playwright) → Claude AI Analysis → Preset Message Selector → FB Messenger (Playwright)
```

- **FastAPI** — REST API + dashboard web su `http://localhost:8000`
- **Celery + Redis** — task asincroni per scraping e invio messaggi
- **Playwright** — scraping Ad Library (no login) + invio messaggi (con sessione salvata)
- **Claude claude-sonnet-4-6** — analisi inserzione + sito web → score 0-100 + selezione messaggio

## Setup rapido

### 1. Copia e configura `.env`
```bash
cp .env.example .env
# Modifica .env con la tua ANTHROPIC_API_KEY
```

### 2. Avvia con Docker Compose
```bash
docker-compose up -d
```

### 3. Accedi alla dashboard
- Dashboard: http://localhost:8000
- API docs: http://localhost:8000/docs
- Flower (monitor task): http://localhost:5555

### 4. Login Facebook (obbligatorio per inviare messaggi)
Vai su **Impostazioni** nella dashboard e clicca "Login Facebook".
Si aprirà un browser Chromium: effettua il login manualmente.
La sessione viene salvata in `fb_session.json` (non le credenziali).

## Setup manuale (senza Docker)

```bash
pip install -r requirements.txt
playwright install chromium

# Terminale 1 — Redis
redis-server

# Terminale 2 — API
uvicorn app.main:app --reload

# Terminale 3 — Worker Celery
celery -A app.tasks.celery_app worker --loglevel=info
```

## Utilizzo

### Avviare una ricerca
1. Vai su **Nuova Ricerca**
2. Inserisci una parola chiave (es. "fisioterapia", "e-commerce abbigliamento")
3. Scegli paese e impostazioni
4. Abilita "Invia automaticamente" se vuoi l'invio immediato ai lead qualificati
5. Clicca **Avvia Ricerca & Analisi**

### Flusso automatico
1. Playwright scrape le inserzioni attive in Ad Library
2. Per ogni inserzione, Claude analizza testo + sito web
3. Claude assegna uno **score 0-100** e seleziona il **messaggio più adatto** tra i 20 preimpostati
4. Se `auto_send=true` e score ≥ min_score, il messaggio viene inviato automaticamente
5. Altrimenti puoi inviarlo manualmente dalla tab **Lead**

### I 20 messaggi preimpostati
Ogni messaggio è ottimizzato per un settore specifico:
e-commerce, business locale, immobiliare, coaching, beauty/wellness, SaaS, food, eventi, educazione, travel, healthcare, automotive, fashion, finance, B2B, servizi casa, e altri.

Claude sceglie automaticamente il messaggio più adatto in base alla categoria del business.

## Note importanti

⚠️ **Rischi**: L'automazione dei messaggi via browser viola i Termini di Servizio di Facebook.
Usa con moderazione e a tuo rischio. Considera:
- Limita gli invii a pochi messaggi al giorno
- Non inviare messaggi identici in massa
- I messaggi preimpostati usano `{page_name}` per personalizzazione base

## API Reference

| Endpoint | Descrizione |
|----------|-------------|
| `POST /api/search` | Avvia nuova ricerca |
| `GET /api/search/{id}` | Stato di un job |
| `GET /api/leads` | Lista lead (filtrabili) |
| `POST /api/leads/{id}/send` | Invia messaggio a lead |
| `GET /api/messages` | Lista messaggi preimpostati |
| `POST /api/auth/fb-login` | Avvia login Facebook |
| `GET /api/auth/fb-status` | Stato sessione Facebook |

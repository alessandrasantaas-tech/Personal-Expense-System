# Sistema di Gestione delle Spese Personali e del Budget

Applicazione console sviluppata in Python con database relazionale SQLite per il monitoraggio delle spese giornaliere, la gestione delle categorie, la definizione dei budget mensili e la generazione di report.

## Requisiti per l'esecuzione
* **Interprete:** Python 3.10 o superiore (necessario per il supporto al costrutto `match/case`).
* **Librerie utilizzate:** Solo librerie standard integrate in Python (`sqlite3`, `os`). Non è richiesta l'installazione di pacchetti esterni.

## Struttura del Repository
* `src/main.py`: Codice sorgente dell'applicazione console.
* `sql/database.sql`: Script SQL completo di creazione delle tabelle, vincoli di integrità e dati di esempio.
* `demo/demo_video.mp4`: Video dimostrativo del funzionamento del software.

## Istruzioni per l'esecuzione
1. Aprire il terminale e posizionarsi nella cartella del progetto:
   ```bash
   cd PersonalExpenseSystem/src

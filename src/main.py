import sqlite3
import os

DB_NAME = "spese_personali.db"

def inizializza_database():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # Creazione tabelle con tutti i vincoli richiesti
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS categorie (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS spese (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        importo REAL NOT NULL CHECK (importo > 0),
        categoria_id INTEGER NOT NULL,
        descrizione TEXT,
        FOREIGN KEY (categoria_id) REFERENCES categorie(id)
    );

    CREATE TABLE IF NOT EXISTS budget (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mese TEXT NOT NULL,
        categoria_id INTEGER NOT NULL,
        limite REAL NOT NULL CHECK (limite > 0),
        UNIQUE (mese, categoria_id),
        FOREIGN KEY (categoria_id) REFERENCES categorie(id)
    );
    """)
    conn.commit()
    conn.close()

# MODULO 1: Gestione delle Categorie
def gestione_categorie():
    nome = input("\nInserisci il nome della nuova categoria: ").strip()
    if not nome:
        print("Errore: il nome della categoria non può essere vuoto.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM categorie WHERE LOWER(nome) = LOWER(?)", (nome,))
    if cursor.fetchone():
        print("La categoria esiste già.")
    else:
        cursor.execute("INSERT INTO categorie (nome) VALUES (?)", (nome,))
        conn.commit()
        print("Categoria inserita correttamente.")
    conn.close()

# MODULO 2: Inserimento di una Spesa
def inserisci_spesa():
    data = input("\nInserisci la data (YYYY-MM-DD): ").strip()
    try:
        importo = float(input("Inserisci l'importo: "))
    except ValueError:
        print("Errore: importo non valido.")
        return

    if importo <= 0:
        print("Errore: l'importo deve essere maggiore di zero.")
        return

    nome_categoria = input("Inserisci il nome della categoria: ").strip()
    descrizione = input("Inserisci una descrizione (facoltativa): ").strip()

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM categorie WHERE LOWER(nome) = LOWER(?)", (nome_categoria,))
    risultato = cursor.fetchone()

    if not risultato:
        print("Errore: la categoria non esiste.")
    else:
        categoria_id = risultato[0]
        cursor.execute(
            "INSERT INTO spese (data, importo, categoria_id, descrizione) VALUES (?, ?, ?, ?)",
            (data, importo, categoria_id, descrizione)
        )
        conn.commit()
        print("Spesa inserita correttamente.")
    conn.close()

# MODULO 3: Definizione del Budget Mensile
def definisci_budget():
    mese = input("\nInserisci il mese (YYYY-MM): ").strip()
    nome_categoria = input("Inserisci il nome della categoria: ").strip()
    try:
        limite = float(input("Inserisci l'importo del budget: "))
    except ValueError:
        print("Errore: importo non valido.")
        return

    if limite <= 0:
        print("Errore: il budget deve essere maggiore di zero.")
        return

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM categorie WHERE LOWER(nome) = LOWER(?)", (nome_categoria,))
    risultato = cursor.fetchone()

    if not risultato:
        print("Errore: la categoria non esiste.")
    else:
        categoria_id = risultato[0]
        cursor.execute("SELECT id FROM budget WHERE mese = ? AND categoria_id = ?", (mese, categoria_id))
        budget_esistente = cursor.fetchone()

        if budget_esistente:
            cursor.execute("UPDATE budget SET limite = ? WHERE id = ?", (limite, budget_esistente[0]))
        else:
            cursor.execute("INSERT INTO budget (mese, categoria_id, limite) VALUES (?, ?, ?)", (mese, categoria_id, limite))
        conn.commit()
        print("Budget mensile salvato correttamente.")
    conn.close()

# MODULO 4: Visualizzazione dei Report
def visualizza_report():
    while True:
        print("\n--- MENU DEI REPORT ---")
        print("1. Totale spese per categoria")
        print("2. Spese mensili vs budget")
        print("3. Elenco completo delle spese ordinate per data")
        print("4. Ritorna al menu principale")
        scelta = input("Inserisci la tua scelta: ").strip()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        match scelta:
            case "1":
                print("\nCategoria\t\tTotale Speso")
                print("-" * 35)
                cursor.execute("""
                    SELECT c.nome, COALESCE(SUM(s.importo), 0)
                    FROM categorie c
                    LEFT JOIN spese s ON c.id = s.categoria_id
                    GROUP BY c.id, c.nome
                """)
                for row in cursor.fetchall():
                    print(f"{row[0]:<15}\t{row[1]:.2f}")

            case "2":
                print("\n--- CONFRONTO SPESE MENSILI VS BUDGET ---")
                cursor.execute("""
                    SELECT b.mese, c.nome, b.limite, COALESCE(SUM(s.importo), 0)
                    FROM budget b
                    JOIN categorie c ON b.categoria_id = c.id
                    LEFT JOIN spese s ON s.categoria_id = b.categoria_id AND substr(s.data, 1, 7) = b.mese
                    GROUP BY b.mese, c.id, c.nome, b.limite
                """)
                righe = cursor.fetchall()
                if not righe:
                    print("Nessun budget definito.")
                for mese, cat, limite, speso in righe:
                    stato = "SUPERAMENTO BUDGET" if speso > limite else "DENTRO IL BUDGET"
                    print(f"\nMese: {mese}\nCategoria: {cat}\nBudget: {limite:.2f}\nSpeso: {speso:.2f}\nStato: {stato}")

            case "3":
                print("\nData\t\tCategoria\tImporto\t\tDescrizione")
                print("-" * 60)
                cursor.execute("""
                    SELECT s.data, c.nome, s.importo, s.descrizione
                    FROM spese s
                    JOIN categorie c ON s.categoria_id = c.id
                    ORDER BY s.data ASC
                """)
                for data, cat, imp, desc in cursor.fetchall():
                    print(f"{data}\t{cat:<12}\t{imp:<8.2f}\t{desc}")

            case "4":
                conn.close()
                break

            case _:
                print("Scelta non valida. Riprovare.")
        
        conn.close()

def main():
    inizializza_database()
    print("==========================================")
    print(" BENVENUTO NEL SISTEMA DI GESTIONE SPESE ")
    print("==========================================")

    while True:
        print("\nSISTEMA SPESE PERSONALI")
        print("1. Gestione Categorie")
        print("2. Inserisci Spesa")
        print("3. Definisci Budget Mensile")
        print("4. Visualizza Report")
        print("5. Esci")
        scelta = input("Inserisci la tua scelta: ").strip()

        match scelta:
            case "1":
                gestione_categorie()
            case "2":
                inserisci_spesa()
            case "3":
                definisci_budget()
            case "4":
                visualizza_report()
            case "5":
                print("Uscita dal programma. Arrivederci!")
                break
            case _:
                print("Scelta non valida. Riprovare.")

if __name__ == "__main__":
    main()

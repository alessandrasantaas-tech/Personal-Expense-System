import sqlite3
from datetime import datetime

DB_NAME = "database.sql"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL CHECK (amount > 0),
            category_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            limit_amount REAL NOT NULL CHECK (limit_amount > 0),
            UNIQUE (month, category_id),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    conn.commit()
    conn.close()

def manage_categories():
    print("\n--- GESTIONE CATEGORIE ---")
    name = input("Inserisci il nome della nuova categoria: ").strip()
    if not name:
        print("Errore: il nome della categoria non può essere vuoto.")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
        if cursor.fetchone():
            print("Errore: la categoria esiste già.")
        else:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
            print("Categoria inserita correttamente.")
    except sqlite3.Error as e:
        print(f"Errore durante l'inserimento: {e}")
    finally:
        conn.close()

def add_expense():
    print("\n--- INSERISCI SPESA ---")
    date_str = input("Inserisci la data (AAAA-MM-DD): ").strip()
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    else:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Formato data non valido. Uso la data odierna.")
            date_str = datetime.now().strftime("%Y-%m-%d")
            
    try:
        amount = float(input("Inserisci l'importo (€): "))
    except ValueError:
        print("Errore: inserisci un valore numerico valido per l'importo.")
        return
    
    if amount <= 0:
        print("Errore: l'importo deve essere maggiore di zero.")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()
    
    if not categories:
        print("Errore: nessuna categoria presente. Creane una prima.")
        conn.close()
        return
    
    print("\nCategorie disponibili:")
    for cat in categories:
        print(f"[{cat[0]}] {cat[1]}")
        
    try:
        cat_id = int(input("Seleziona l'ID della categoria: "))
    except ValueError:
        print("ID non valido.")
        conn.close()
        return
    
    cursor.execute("SELECT id FROM categories WHERE id = ?", (cat_id,))
    if not cursor.fetchone():
        print("Errore: la categoria non esiste.")
        conn.close()
        return
        
    description = input("Inserisci una descrizione facoltativa: ").strip()
    
    try:
        cursor.execute("INSERT INTO expenses (amount, category_id, date, description) VALUES (?, ?, ?, ?)",
                       (amount, cat_id, date_str, description))
        conn.commit()
        print("Spesa inserita correttamente.")
    except sqlite3.Error as e:
        print(f"Errore: {e}")
    finally:
        conn.close()

def set_budget():
    print("\n--- DEFINISCI BUDGET MENSILE ---")
    month = input("Inserisci il mese (YYYY-MM): ").strip()
    if len(month) != 7 or month[4] != '-':
        print("Formato mese non valido. Usa YYYY-MM (es. 2025-01).")
        return
        
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()
    
    if not categories:
        print("Errore: nessuna categoria presente. Creane una prima.")
        conn.close()
        return
        
    print("\nCategorie disponibili:")
    for cat in categories:
        print(f"[{cat[0]}] {cat[1]}")
        
    try:
        cat_id = int(input("Seleziona l'ID della categoria: "))
    except ValueError:
        print("ID non valido.")
        conn.close()
        return
        
    cursor.execute("SELECT id FROM categories WHERE id = ?", (cat_id,))
    if not cursor.fetchone():
        print("Errore: la categoria non esiste.")
        conn.close()
        return
        
    try:
        limit_amount = float(input("Inserisci l'importo del budget (€): "))
    except ValueError:
        print("Errore: importo non valido.")
        conn.close()
        return
        
    if limit_amount <= 0:
        print("Errore: il budget deve essere maggiore di zero.")
        conn.close()
        return
        
    try:
        cursor.execute('''
            INSERT INTO budgets (month, category_id, limit_amount) 
            VALUES (?, ?, ?)
            ON CONFLICT(month, category_id) 
            DO UPDATE SET limit_amount = ?
        ''', (month, cat_id, limit_amount, limit_amount))
        conn.commit()
        print("Budget mensile salvato correttamente.")
    except sqlite3.Error as e:
        print(f"Errore: {e}")
    finally:
        conn.close()

def view_reports():
    while True:
        print("\n--- MENU DEI REPORT ---")
        print("1. Totale spese per categoria")
        print("2. Spese mensili vs budget")
        print("3. Elenco completo delle spese ordinate per data")
        print("4. Ritorna al menu principale")
        
        choice = input("Inserisci la tua scelta: ").strip()
        
        conn = get_connection()
        cursor = conn.cursor()
        
        if choice == '1':
            cursor.execute('''
                SELECT c.name, SUM(e.amount) 
                FROM categories c 
                LEFT JOIN expenses e ON c.id = e.category_id 
                GROUP BY c.id, c.name
            ''')
            rows = cursor.fetchall()
            print("\n--- TOTALE SPESE PER CATEGORIA ---")
            print(f"{'Categoria':<20} | {'Totale Speso':<15}")
            print("-" * 40)
            for row in rows:
                total = row[1] if row[1] is not None else 0.0
                print(f"{row[0]:<20} | €{total:<14.2f}")
                
        elif choice == '2':
            month = input("Inserisci il mese da verificare (YYYY-MM): ").strip()
            cursor.execute('''
                SELECT c.id, c.name FROM categories c
            ''')
            cats = cursor.fetchall()
            print(f"\n--- SPESE MENSILI VS BUDGET ({month}) ---")
            for cat_id, cat_name in cats:
                cursor.execute('''
                    SELECT limit_amount FROM budgets WHERE month = ? AND category_id = ?
                ''', (month, cat_id))
                b_row = cursor.fetchone()
                budget_val = b_row[0] if b_row else 0.0
                
                cursor.execute('''
                    SELECT SUM(amount) FROM expenses 
                    WHERE category_id = ? AND strftime('%Y-%m', date) = ?
                ''', (cat_id, month))
                e_row = cursor.fetchone()
                spent_val = e_row[0] if e_row and e_row[0] else 0.0
                
                if budget_val > 0 or spent_val > 0:
                    print(f"\nMese: {month}")
                    print(f"Categoria: {cat_name}")
                    print(f"Budget: {budget_val:.2f}")
                    print(f"Speso: {spent_val:.2f}")
                    if budget_val > 0:
                        if spent_val > budget_val:
                            print("Stato: SUPERAMENTO BUDGET")
                        else:
                            print("Stato: RIENTRO NEL BUDGET")
                    else:
                        print("Stato: NESSUN BUDGET IMPOSTATO")
            print("-" * 40)
            
        elif choice == '3':
            cursor.execute('''
                SELECT e.date, c.name, e.amount, e.description
                FROM expenses e
                LEFT JOIN categories c ON e.category_id = c.id
                ORDER BY e.date DESC
            ''')
            rows = cursor.fetchall()
            print("\n--- ELENCO COMPLETO DELLE SPESE ---")
            print(f"{'Data':<12} | {'Categoria':<15} | {'Importo':<10} | {'Descrizione'}")
            print("-" * 60)
            for row in rows:
                desc = row[3] if row[3] else ""
                print(f"{row[0]:<12} | {row[1]:<15} | €{row[2]:<9.2f} | {desc}")
                
        elif choice == '4':
            conn.close()
            break
        else:
            print("Scelta non valida. Riprovare.")
        conn.close()

def main():
    init_db()
    while True:
        print("\nSISTEMA SPESE PERSONALI")
        print("1. Gestione Categorie")
        print("2. Inserisci Spesa")
        print("3. Definisci Budget Mensile")
        print("4. Visualizza Report")
        print("5. Esci")
        
        choice = input("Inserisci la tua scelta: ").strip()
        
        match choice:
            case '1':
                manage_categories()
            case '2':
                add_expense()
            case '3':
                set_budget()
            case '4':
                view_reports()
            case '5':
                print("Uscita dal programma. Arrivederci!")
                break
            case _:
                print("Scelta non valida. Riprovare.")

if __name__ == "__main__":
    main()

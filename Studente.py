import socket
import pickle

# Costanti per la configurazione
FORMAT = 'utf-8'  # Formato di codifica per le stringhe
DISCONNESSIONE = "Disconnessione"  # Messaggio di disconnessione
PORT = 5678  # Porta per la comunicazione con la segreteria
SERVER = socket.gethostbyname(socket.gethostname())  # Ottiene l'indirizzo IP del server
ADDR = (SERVER, PORT)  # Indirizzo della segreteria (IP, porta)

# Creazione del socket per la comunicazione con la segreteria
studente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Tentativo di connessione alla segreteria
try:
    studente_socket.connect(ADDR)
except socket.error as e:
    print(f"Errore di connessione: {e}")
    exit(1)

# Funzione per richiedere le date degli esami
def richiesta_esami():
    try:
        studente_socket.sendall("DATE_ESAMI".encode(FORMAT))
        nome_esame = input("Inserisci il nome dell'esame: ")
        nome_esame = nome_esame.upper()
        if not nome_esame:
            print("Il nome dell'esame non può essere vuoto.")
            return

        studente_socket.sendall(nome_esame.encode(FORMAT))

        date_disponibili = studente_socket.recv(1024).decode(FORMAT)
        print(f"Le date disponibili per {nome_esame} sono: {date_disponibili}")
    except socket.error as e:
        print(f"Errore durante la richiesta degli esami: {e}")

# Funzione per prenotare un esame
def prenotazione_esame():
    try:
        studente_socket.send("PRENOTAZIONE_ESAME".encode(FORMAT))
        studente_id = input("Inserisci il tuo id studente: ")
        nome_esame = input("Inserisci il nome dell'esame: ")
        nome_esame = nome_esame.upper()
        data_esame = input("Inserisci la data dell'esame (dd-mm-yyyy): ")

        if not studente_id or not nome_esame or not data_esame:
            print("Tutti i campi sono obbligatori.")
            return

        prenotazione = {
            'studente_id': studente_id,
            'nome_esame': nome_esame,
            'data_esame': data_esame
        }
        prenotazione_serializzata = pickle.dumps(prenotazione)
        studente_socket.send(prenotazione_serializzata)

        risposta = studente_socket.recv(5000).decode(FORMAT)
        print(f"Risposta dalla segreteria: {risposta}")
    except socket.error as e:
        print(f"Errore durante la prenotazione dell'esame: {e}")

# Funzione per chiudere la connessione
def chiudi_connessione():
    try:
        studente_socket.send(DISCONNESSIONE.encode(FORMAT))
    except socket.error as e:
        print(f"Errore durante la disconnessione: {e}")
    finally:
        studente_socket.close()

# Funzione per far scegliere all'utente un'opzione
if __name__ == "__main__":
    while True:
        print("1. Richiesta esami")
        print("2. Prenotazione esame")
        print("3. Disconnessione")
        scelta = input("Scegli un'opzione: ")

        if scelta == '1':
            richiesta_esami()
        elif scelta == '2':
            prenotazione_esame()
        elif scelta == '3':
            chiudi_connessione()
            break
        else:
            print("Opzione non valida. Riprova.")
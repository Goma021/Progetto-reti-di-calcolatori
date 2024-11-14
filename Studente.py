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

# Funzione per avviare la connessione alla segreteria
def avvia_connessione():
    try:
        studente_socket.connect(ADDR)
        # Attende la conferma della connessione dalla segreteria
        conferma = studente_socket.recv(1024).decode(FORMAT)
        if conferma != "CONNESSIONE_ACCETTATA":
            print("Connessione non accettata dalla segreteria.")
            exit(1)
    except socket.error as e:
        print(f"Errore di connessione: {e}")
        exit(1)

# Avvia la connessione all'avvio del file
avvia_connessione()

# Funzione per richiedere le date degli esami
def richiesta_esami():
    try:
        # Invia una richiesta per ottenere le date degli esami
        studente_socket.sendall("DATE_ESAMI".encode(FORMAT))
        
        # Richiede all'utente di inserire il nome dell'esame
        nome_esame = input("Inserisci il nome dell'esame: ")
        # Converte il nome dell'esame in maiuscolo
        nome_esame = nome_esame.upper()  
        
        # Verifica che il nome dell'esame non sia vuoto
        if not nome_esame:
            print("Il nome dell'esame non può essere vuoto.")
            return

        # Invia il nome dell'esame alla segreteria
        studente_socket.sendall(nome_esame.encode(FORMAT))

        # Riceve le date disponibili dalla segreteria
        date_disponibili = studente_socket.recv(1024)
        date_disponibili = date_disponibili.pickle.loads(date_disponibili)
        print(f"Le date disponibili per {nome_esame} sono:{date_disponibili.data_1}")
    except socket.error as e:
        print(f"Errore durante la richiesta degli esami: {e}")

# Funzione per prenotare un esame
def prenotazione_esame():
    try:
        # Invia una richiesta per prenotare un esame
        studente_socket.sendall("PRENOTAZIONE_ESAME".encode(FORMAT))
        
        # Richiede all'utente di inserire il proprio ID studente
        studente_id = input("Inserisci il tuo id studente: ")
        
        # Richiede all'utente di inserire il nome dell'esame
        nome_esame = input("Inserisci il nome dell'esame: ")
        # Converte il nome dell'esame in maiuscolo
        nome_esame = nome_esame.upper()  
        
        # Richiede all'utente di inserire la data dell'esame
        data_esame = input("Inserisci la data dell'esame (dd-mm-yyyy): ")

        # Verifica che tutti i campi siano stati compilati
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
        # Invia un messaggio di disconnessione al server
        studente_socket.send(DISCONNESSIONE.encode(FORMAT))
    except socket.error as e:
        # Stampa un messaggio di errore in caso di problemi durante la disconnessione
        print(f"Errore durante la disconnessione: {e}")
    finally:
        # Chiude il socket per terminare la connessione
        studente_socket.close()

# Funzione per far scegliere all'utente un'opzione
if __name__ == "__main__":
    while True:
        # Stampa il menu delle opzioni
        print("1. Richiesta esami")
        print("2. Prenotazione esame")
        print("3. Disconnessione")
        
        # Richiede all'utente di scegliere un'opzione
        scelta = input("Scegli un'opzione: ")

        if scelta == '1':
            # Esegue la funzione per richiedere le date degli esami
            richiesta_esami()
        elif scelta == '2':
            # Esegue la funzione per prenotare un esame
            prenotazione_esame()
        elif scelta == '3':
            # Esegue la funzione per chiudere la connessione e termina il ciclo
            chiudi_connessione()
            break
        else:
            # Stampa un messaggio di errore in caso di opzione non valida
            print("Opzione non valida. Riprova.")

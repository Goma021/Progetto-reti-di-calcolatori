import socket
import pickle
import threading
import os
from esame import Esame  # Importa la classe Esame dal modulo esame

# Costanti per la configurazione del server
FORMAT = 'utf-8'  # Formato di codifica per le stringhe
DISCONNESSIONE = "Disconnessione"  # Messaggio di disconnessione
PORT = 5677  # Porta su cui il server ascolta
SERVER = socket.gethostbyname(socket.gethostname())  # Ottiene l'indirizzo IP del server
ADDR = (SERVER, PORT)  # Indirizzo del server (IP, porta)
FILE_ESAMI = 'esami.pkl'  # Nome del file in cui sono salvati gli esami

# Creazione del socket del server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDR)  # Associa il socket all'indirizzo e alla porta specificati
server_socket.listen(5)  # Il server ascolta fino a 5 connessioni in coda

# Variabile globale per controllare lo stato del server
server_running = True

# Carica gli esami dal file se esiste, altrimenti crea una lista vuota
# Carica gli esami dal file se esiste, altrimenti crea una lista vuota
if os.path.exists(FILE_ESAMI):
    with open(FILE_ESAMI, 'rb') as f:
        Lista_esami = pickle.load(f)
else:
    Lista_esami = []

# Funzione per salvare gli esami nel file
def salva_esami():
    with open(FILE_ESAMI, 'wb') as f:
        pickle.dump(Lista_esami, f)

# Funzione per gestire le richieste dei client
def gestisci_client(conn, addr):
    print(f"Connessione tramite porta {addr}")
    try:
        while True:
            # Riceve la richiesta dal client
            richiesta = conn.recv(1024).decode(FORMAT)
            if richiesta == "DATE_ESAMI":
                # Gestisce la richiesta di date degli esami
                nome_esame = conn.recv(1024).decode(FORMAT)
                esame_trovato = None
                for esame in Lista_esami:
                    if esame.nome_esame == nome_esame:
                        esame_trovato = esame
                        break
                if esame_trovato:
                    # Se l'esame è trovato, invia i dettagli al client
                    conn.send(pickle.dumps(esame_trovato))
                else:
                    # Se l'esame non è trovato, invia un messaggio di errore
                    conn.send("Esame non trovato".encode(FORMAT))
            elif richiesta == DISCONNESSIONE:
                # Gestisce la richiesta di disconnessione
                print(f"Disconnessione da {addr}")
                break
    except Exception as e:
        print(f"Errore con {addr}: {e}")
    finally:
        conn.close()  # Chiude la connessione con il client

# Funzione per avviare il server
# Funzione per avviare il server
def avvia_server():
    global server_running
    print(f"[Avvio Server] in ascolto su {ADDR}")
    try:
        while server_running:
            try:
                # Accetta una nuova connessione
                conn, addr = server_socket.accept()
                # Crea un nuovo thread per gestire il client
                thread = threading.Thread(target=gestisci_client, args=(conn, addr))
                thread.start()
                # Stampa il numero di connessioni attive (escludendo il thread principale e il thread del server)
                print(f"[Connessioni Attive] {threading.active_count() - 2}")
            except socket.error as e:
                # Gestisce eventuali errori durante l'accettazione della connessione
                if server_running:
                    print(f"Errore durante l'accettazione della connessione: {e}")
    finally:
        # Chiude il socket del server quando il ciclo termina
        server_socket.close()
        print("Server chiuso.")

# Funzione per visualizzare gli esami
# Funzione per visualizzare gli esami
def visualizza_esami():
    # Controlla se il file degli esami esiste
    if os.path.exists(FILE_ESAMI):
        # Apre il file degli esami in modalità lettura binaria
        with open(FILE_ESAMI, 'rb') as f:
            # Carica la lista degli esami dal file
            Lista_esami = pickle.load(f)
            # Stampa i dettagli di ogni esame
            for esame in Lista_esami:
                print(f"Nome Esame: {esame.nome_esame}, Date Disponibili: {', '.join(esame.date_disponibili)}")
    else:
        # Stampa un messaggio se il file non esiste
        print("Il file esami.pkl non esiste.")

# Esegui il server in un thread separato per poterlo fermare da terminale
server_thread = threading.Thread(target=avvia_server)
server_thread.start()

# Visualizza gli esami caricati dal file
visualizza_esami()

# Loop principale per fermare il server da terminale
while server_running:
    # Attende l'input dell'utente per fermare il server
    chiudi = input("")
    if chiudi == "1":
        # Imposta la variabile per fermare il server
        server_running = False
        # Chiude il socket del server
        server_socket.close()
    else:
        # Continua il loop se l'input non è "1"
        pass
import socket
import pickle
import threading
import os
from esame import Esame

# Costanti per la configurazione del server
FORMAT = 'utf-8'  # Formato di codifica per le stringhe
DISCONNESSIONE = "Disconnessione"  # Messaggio di disconnessione
PORT = 5677  # Porta su cui il server ascolta
SERVER = socket.gethostbyname(socket.gethostname())  # Ottiene l'indirizzo IP del server
ADDR = (SERVER, PORT)  # Indirizzo del server (IP, porta)
FILE_ESAMI = 'esami.pkl'  # Nome del file in cui sono salvati gli esami

# Creazione del socket del server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDR)  # Associa il socket all'indirizzo e alla porta
server_socket.listen(5)  # Il server ascolta fino a 5 connessioni in coda

# Variabile globale per controllare lo stato del server
server_running = True

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
                    date_disponibili = ', '.join(esame_trovato.date_disponibili)
                    conn.sendall(date_disponibili.encode(FORMAT))
                else:
                    conn.sendall(f"Esame {nome_esame} non trovato.".encode(FORMAT))
            elif richiesta == "INSERISCI_ESAME":
                # Gestisce l'inserimento di un nuovo esame
                esame_serializzato = conn.recv(1024)
                esame = pickle.loads(esame_serializzato)
                Lista_esami.append(esame)
                salva_esami()
                conn.sendall(f"Esame {esame.nome_esame} aggiunto con successo.".encode(FORMAT))
            elif richiesta == "PRENOTAZIONE_ESAME":
                # Gestisce la prenotazione di un esame
                prenotazione_serializzata = conn.recv(1024)
                prenotazione = pickle.loads(prenotazione_serializzata)
                # Logica per gestire la prenotazione
                conn.sendall(f"Prenotazione per {prenotazione['nome_esame']} ricevuta.".encode(FORMAT))
            elif richiesta == DISCONNESSIONE:
                # Gestisce la disconnessione del client
                print(f"Disconnessione da {addr}")
                break
    except socket.error as e:
        print(f"Errore di connessione: {e}")
    finally:
        conn.close()
        print(f"Connessione chiusa con {addr}")

# Funzione per avviare il server
def avvia_server():
    global server_running
    print(f"[Avvio Server] in ascolto su {ADDR}")
    try:
        while server_running:
            try:
                conn, addr = server_socket.accept()
                thread = threading.Thread(target=gestisci_client, args=(conn, addr))
                thread.start()
                print(f"[Connessioni Attive] {threading.active_count() - 2}")
            except socket.error as e:
                if server_running:
                    print(f"Errore durante l'accettazione della connessione: {e}")
    finally:
        server_socket.close()
        print("Server chiuso.")

# Funzione per visualizzare gli esami
def visualizza_esami():
    if os.path.exists(FILE_ESAMI):
        with open(FILE_ESAMI, 'rb') as f:
            Lista_esami = pickle.load(f)
            for esame in Lista_esami:
                print(f"Nome Esame: {esame.nome_esame}, Date Disponibili: {', '.join(esame.date_disponibili)}")
    else:
        print("Il file esami.pkl non esiste.")

# Esegui il server in un thread separato per poterlo fermare da terminale
server_thread = threading.Thread(target=avvia_server)
server_thread.start()
visualizza_esami()

# Loop principale per fermare il server da terminale
while server_running:
    chiudi = input("")
    if chiudi == "1":
        server_running = False
        server_socket.close()
    else:
        pass
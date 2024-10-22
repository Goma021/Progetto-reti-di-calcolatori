import socket
import pickle
import threading
from esame import Esame

# Costanti per la configurazione
FORMAT = 'utf-8'  # Formato di codifica per le stringhe
DISCONNESSIONE = "Disconnessione"  # Messaggio di disconnessione
PORT = 5677  # Porta per la comunicazione con il server universitario
PORT_2 = 5678  # Porta per la comunicazione con gli studenti
SERVER = socket.gethostbyname(socket.gethostname())  # Ottiene l'indirizzo IP del server
ADDR = (SERVER, PORT)  # Indirizzo del server universitario (IP, porta)
ADDR_2 = (SERVER, PORT_2)  # Indirizzo per la comunicazione con gli studenti (IP, porta)

# Creazione del socket per la comunicazione con il server universitario
segreteria_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Creazione del socket per la comunicazione con gli studenti
segreteria_socket_studenti = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connessione al server universitario
segreteria_socket.connect(ADDR)
# Binding del socket per la comunicazione con gli studenti
segreteria_socket_studenti.bind(ADDR_2)
# Il socket ascolta fino a 5 connessioni in coda
segreteria_socket_studenti.listen(5)

# Contatore delle connessioni attive
connessioni_attive = 0

# Funzione per inserire un nuovo esame
def inserisci_esame():
    nome_esame = input("Inserisci il nome dell'esame: ")
    data_1 = input("Inserisci la prima data disponibile (dd/mm/yyyy): ")
    data_2 = input("Inserisci la seconda data disponibile (dd/mm/yyyy): ")
    data_3 = input("Inserisci la terza data disponibile (dd/mm/yyyy): ")
    nome_esame = nome_esame.upper()
    esame = Esame(nome_esame, data_1, data_2, data_3)
    esame_serializzato = pickle.dumps(esame)
    segreteria_socket.sendall("INSERISCI_ESAME".encode(FORMAT))
    segreteria_socket.sendall(esame_serializzato)
    print("Esame inviato al server")

# Funzione per gestire le richieste degli studenti
def gestisci_richieste_studenti(conn, addr):
    global connessioni_attive
    connessioni_attive += 1
    print(f"Connessione stabilita con {addr}. Connessioni attive: {connessioni_attive}")
    try:
        while True:
            richiesta = conn.recv(1024).decode(FORMAT)
            if richiesta == "PRENOTAZIONE_ESAME":
                # Gestisce la prenotazione di un esame
                prenotazione = conn.recv(5000)
                segreteria_socket.sendall("PRENOTAZIONE_ESAME".encode(FORMAT))
                segreteria_socket.sendall(prenotazione)
                risposta = segreteria_socket.recv(5000)
                conn.sendall(risposta)
                print(f"Prenotazione effettuata")
            elif richiesta == "DATE_ESAMI":
                # Gestisce la richiesta delle date degli esami
                nome_esame = conn.recv(1024).decode(FORMAT)
                print(f"Richiesta date esami per {nome_esame}")
                segreteria_socket.sendall("DATE_ESAMI".encode(FORMAT))
                segreteria_socket.sendall(nome_esame.encode(FORMAT))
                date_disponibili = segreteria_socket.recv(1024).decode(FORMAT)
                conn.sendall(date_disponibili.encode(FORMAT))
            elif richiesta == DISCONNESSIONE:
                # Gestisce la disconnessione del client
                print(f"Disconnessione da {addr}")
                break
    except socket.error as e:
        print(f"Errore di connessione: {e}")
    finally:
        conn.close()
        connessioni_attive -= 1
        print(f"Connessione chiusa con {addr}. Connessioni attive: {connessioni_attive}")

# Funzione per avviare la segreteria
def avvia_segreteria():
    while True:
        print("Seleziona la tua scelta:")
        scelta = input("1. Inserisci un esame\n2. Gestisci richieste\n3. Chiudi\n")
        match scelta:
            case '1':
                inserisci_esame()
            case '2':
                conn, addr = segreteria_socket_studenti.accept()
                thread = threading.Thread(target=gestisci_richieste_studenti, args=(conn, addr))
                thread.start()
            case '3':
                segreteria_socket.sendall(DISCONNESSIONE.encode(FORMAT))
                segreteria_socket.close()
                segreteria_socket_studenti.close()
                break
            case _:
                print("Scelta non valida, riprova.")

# Avvia la segreteria
avvia_segreteria()
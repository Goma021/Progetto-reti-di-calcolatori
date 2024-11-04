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
# AF_INET indica che si utilizza IPv4, SOCK_STREAM indica che si utilizza TCP
segreteria_socket_studenti = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connessione al server universitario
# Si connette al server utilizzando l'indirizzo e la porta specificati in ADDR
segreteria_socket.connect(ADDR)

# Binding del socket per la comunicazione con gli studenti
# Si associa il socket all'indirizzo e alla porta specificati in ADDR_2
segreteria_socket_studenti.bind(ADDR_2)

# Il socket ascolta fino a 5 connessioni in coda
# Il socket è ora pronto per accettare connessioni in entrata
segreteria_socket_studenti.listen(5)

# Contatore delle connessioni attive
# Tiene traccia del numero di connessioni attive con gli studenti
connessioni_attive = 0

# Funzione per inserire un nuovo esame
def inserisci_esame():
    # Richiede all'utente di inserire il nome dell'esame e tre date disponibili
    nome_esame = input("Inserisci il nome dell'esame: ")
    data_1 = input("Inserisci la prima data disponibile (dd/mm/yyyy): ")
    data_2 = input("Inserisci la seconda data disponibile (dd/mm/yyyy): ")
    data_3 = input("Inserisci la terza data disponibile (dd/mm/yyyy): ")
    
    # Converte il nome dell'esame in maiuscolo
    nome_esame = nome_esame.upper()
    
    # Crea un oggetto Esame con i dati inseriti
    esame = Esame(nome_esame, data_1, data_2, data_3)
    
    # Serializza l'oggetto Esame in un formato che può essere inviato tramite socket
    esame_serializzato = pickle.dumps(esame)
    
    # Invia un comando al server per indicare che si sta inserendo un nuovo esame
    segreteria_socket.sendall("INSERISCI_ESAME".encode(FORMAT))
    
    # Invia i dati dell'esame serializzati al server
    segreteria_socket.sendall(esame_serializzato)
    
    # Stampa un messaggio di conferma
    print("Esame inviato al server")

# Funzione per gestire le richieste degli studenti
# Gestisce le connessioni in entrata dagli studenti e le loro richieste
def gestisci_richieste_studenti(conn, addr):
    global connessioni_attive
    
    # Incrementa il contatore delle connessioni attive
    connessioni_attive += 1
    
    # Stampa un messaggio di conferma della connessione
    print(f"Connessione stabilita con {addr}. Connessioni attive: {connessioni_attive}")
    
    try:
        while True:
            # Riceve una richiesta dallo studente
            richiesta = conn.recv(1024).decode(FORMAT)
            
            if richiesta == "PRENOTAZIONE_ESAME":
                # Gestisce la prenotazione di un esame
                # Riceve i dati della prenotazione dallo studente
                prenotazione = conn.recv(5000)
                
                # Invia un comando al server per indicare che si sta effettuando una prenotazione
                segreteria_socket.sendall("PRENOTAZIONE_ESAME".encode(FORMAT))
                
                # Invia i dati della prenotazione al server
                segreteria_socket.sendall(prenotazione)
                
                # Riceve la risposta dal server
                risposta = segreteria_socket.recv(5000)
                
                # Invia la risposta allo studente
                conn.sendall(risposta)
                
                # Stampa un messaggio di conferma
                print(f"Prenotazione effettuata")
            
            elif richiesta == "DATE_ESAMI":
                # Gestisce la richiesta delle date degli esami
                # Riceve il nome dell'esame dallo studente
                nome_esame = conn.recv(1024).decode(FORMAT)
                
                # Stampa un messaggio di richiesta delle date degli esami
                print(f"Richiesta date esami per {nome_esame}")
                
                # Invia un comando al server per richiedere le date degli esami
                segreteria_socket.sendall("DATE_ESAMI".encode(FORMAT))
                
                # Invia il nome dell'esame al server
                segreteria_socket.sendall(nome_esame.encode(FORMAT))
                
                # Riceve le date disponibili dal server
                date_disponibili = segreteria_socket.recv(1024).decode(FORMAT)
                conn.sendall(date_disponibili.encode(FORMAT))
            elif richiesta == DISCONNESSIONE:
                # Gestisce la disconnessione del client
                print(f"Disconnessione da {addr}")
                break
    except socket.error as e:
        # Gestisce eventuali errori di connessione e stampa un messaggio di errore
        print(f"Errore di connessione: {e}")
    finally:
        # Chiude la connessione con lo studente
        conn.close()
        # Decrementa il contatore delle connessioni attive
        connessioni_attive -= 1
        # Stampa un messaggio di conferma della chiusura della connessione
        print(f"Connessione chiusa con {addr}. Connessioni attive: {connessioni_attive}")

# Funzione per avviare la segreteria
def avvia_segreteria():
    while True:
        # Mostra il menu di scelta all'utente
        print("Seleziona la tua scelta:")
        scelta = input("1. Inserisci un esame\n2. Gestisci richieste\n3. Chiudi\n")
        match scelta:
            case '1':
                # Chiama la funzione per inserire un nuovo esame
                inserisci_esame()
            case '2':
                # Accetta una nuova connessione in entrata dagli studenti
                conn, addr = segreteria_socket_studenti.accept()
                # Crea un nuovo thread per gestire la richiesta dello studente
                thread = threading.Thread(target=gestisci_richieste_studenti, args=(conn, addr))
                # Avvia il thread
                thread.start()
            case '3':
                # Invia un messaggio di disconnessione al server universitario
                segreteria_socket.sendall(DISCONNESSIONE.encode(FORMAT))
                # Chiude il socket per la comunicazione con il server universitario
                segreteria_socket.close()
                # Chiude il socket per la comunicazione con gli studenti
                segreteria_socket_studenti.close()
                # Esce dal ciclo e termina la funzione
                break
            case _:
                # Gestisce una scelta non valida
                print("Scelta non valida, riprova.")

# Avvia la segreteria
avvia_segreteria()
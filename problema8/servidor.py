#!/usr/bin/env python3
"""
Servidor Tic-Tac-Toe multijugador (problema8/servidor.py)

- TCP server, hilo por cliente
- Protocolo de texto simple, líneas terminadas en '\n'
- Comandos principales:
    CREATE_MATCH            -> crea una nueva partida y devuelve ID
    JOIN_MATCH <id>         -> se une como jugador (si hay espacio) o espectador
    LIST_MATCHES            -> lista partidas y estados
    MOVE <id> <pos>         -> hace movimiento en la partida (pos 0-8)
    SPECTATE <id>           -> unirse como espectador a la partida
    QUIT                    -> desconectar
- Notificaciones:
    Cuando algo cambia, el servidor envía mensajes a jugadores y espectadores.
"""
import socket
import threading
import uuid
import json

HOST = 'localhost'
PORT = 9401
BUFFER = 4096

# Estado global
matches = {}   # match_id -> match dict
clients = {}   # conn -> {"name": ..., "match": match_id or None, "role": "player"/"spectator"}
lock = threading.Lock()


# ------------------ UTILIDADES ------------------
def send_line(conn, text):
    """Enviar una línea terminada en \\n y manejar errores silenciosamente."""
    try:
        conn.sendall((text + "\n").encode())
    except Exception:
        # el receptor puede haber caído
        pass

def recv_line(conn):
    """Recibir hasta \\n y devolver string sin el \\n"""
    data = b""
    while True:
        chunk = conn.recv(1)
        if not chunk:
            raise ConnectionError("Conexión cerrada")
        data += chunk
        if data.endswith(b"\n"):
            return data[:-1].decode()

def new_match(creator_name):
    """Crea una partida nueva y devuelve su id."""
    mid = str(uuid.uuid4())[:8]
    match = {
        "id": mid,
        "board": [" "] * 9,      # posiciones 0..8
        "players": [],          # list of (conn, name, mark) where mark in 'X'/'O'
        "spectators": set(),    # set of conn
        "turn": 0,              # index in players list whose turn it is
        "status": "waiting",    # waiting | playing | finished
        "winner": None
    }
    matches[mid] = match
    print(f"[+] Created match {mid} by {creator_name}")
    return mid

def board_to_str(board):
    """Devuelve una representación simple del tablero."""
    rows = []
    for r in range(3):
        rows.append(" | ".join(board[r*3:(r+1)*3]))
    return "\n".join(rows)

def check_winner(board):
    """Devuelve 'X' o 'O' si hay ganador, 'draw' si empate, else None."""
    wins = [(0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)]
    for a,b,c in wins:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    if all(cell != " " for cell in board):
        return "draw"
    return None

def broadcast_match(match, message):
    """Enviar mensaje a todos los jugadores y espectadores de la partida."""
    # players is list of tuples (conn, name, mark)
    for (pconn, pname, mark) in match["players"]:
        send_line(pconn, message)
    for sconn in list(match["spectators"]):
        send_line(sconn, message)


# ------------------ LÓGICA DE COMANDOS ------------------
def cmd_create_match(conn, name):
    with lock:
        mid = new_match(name)
    send_line(conn, f"OK CREATED {mid}")

def cmd_list_matches(conn):
    with lock:
        if not matches:
            send_line(conn, "OK 0 no matches")
            return
        send_line(conn, f"OK {len(matches)} matches")
        for m in matches.values():
            send_line(conn, f"{m['id']} status={m['status']} players={len(m['players'])}")

def cmd_join_match(conn, name, args):
    # args: [match_id]
    if len(args) < 1:
        send_line(conn, "ERR missing match id")
        return
    mid = args[0]
    with lock:
        match = matches.get(mid)
        if not match:
            send_line(conn, "ERR no such match")
            return
        # If match waiting and has <2 players, join as player
        if match["status"] in ("waiting",) and len(match["players"]) < 2:
            # decide mark
            mark = "X" if not match["players"] else "O"
            match["players"].append((conn, name, mark))
            clients[conn]["match"] = mid
            clients[conn]["role"] = "player"
            if len(match["players"]) == 2:
                match["status"] = "playing"
                match["turn"] = 0
                broadcast_match(match, f"GAME_START {mid} players={match['players'][0][1]}(X) vs {match['players'][1][1]}(O)")
            else:
                send_line(conn, f"OK joined {mid} waiting_for_opponent")
                return
            # notify both players of board
            broadcast_match(match, f"BOARD\n{board_to_str(match['board'])}")
            return
        else:
            # join as spectator
            match["spectators"].add(conn)
            clients[conn]["match"] = mid
            clients[conn]["role"] = "spectator"
            send_line(conn, f"OK joined as spectator {mid}")
            send_line(conn, f"BOARD\n{board_to_str(match['board'])}")
            return

def cmd_move(conn, name, args):
    # args: [match_id, pos]
    if len(args) < 2:
        send_line(conn, "ERR missing args for MOVE")
        return
    mid, pos_s = args[0], args[1]
    try:
        pos = int(pos_s)
    except:
        send_line(conn, "ERR invalid position")
        return
    if pos < 0 or pos > 8:
        send_line(conn, "ERR position out of range")
        return
    with lock:
        match = matches.get(mid)
        if not match:
            send_line(conn, "ERR no such match")
            return
        # confirm conn is one of the players
        player_indices = [i for i,(pconn,pname,mark) in enumerate(match["players"]) if pconn==conn]
        if not player_indices:
            send_line(conn, "ERR you are not a player in this match")
            return
        player_index = player_indices[0]
        if match["status"] != "playing":
            send_line(conn, "ERR match not playing")
            return
        if match["turn"] != player_index:
            send_line(conn, "ERR not your turn")
            return
        if match["board"][pos] != " ":
            send_line(conn, "ERR cell occupied")
            return
        mark = match["players"][player_index][2]
        match["board"][pos] = mark
        # check winner
        result = check_winner(match["board"])
        if result == "draw":
            match["status"] = "finished"
            broadcast_match(match, f"BOARD\n{board_to_str(match['board'])}")
            broadcast_match(match, f"RESULT draw")
            return
        elif result in ("X","O"):
            match["status"] = "finished"
            match["winner"] = result
            broadcast_match(match, f"BOARD\n{board_to_str(match['board'])}")
            broadcast_match(match, f"RESULT winner={result}")
            return
        else:
            # continue game
            match["turn"] = (match["turn"] + 1) % len(match["players"])
            broadcast_match(match, f"BOARD\n{board_to_str(match['board'])}")
            next_player = match["players"][match["turn"]][1]
            broadcast_match(match, f"TURN {next_player}")
            return

def cmd_spectate(conn, name, args):
    if len(args) < 1:
        send_line(conn, "ERR missing match id")
        return
    mid = args[0]
    with lock:
        match = matches.get(mid)
        if not match:
            send_line(conn, "ERR no such match")
            return
        match["spectators"].add(conn)
        clients[conn]["match"] = mid
        clients[conn]["role"] = "spectator"
        send_line(conn, f"OK spectating {mid}")
        send_line(conn, f"BOARD\n{board_to_str(match['board'])}")

def cmd_quit(conn):
    with lock:
        info = clients.get(conn)
        if info and info["match"]:
            mid = info["match"]
            match = matches.get(mid)
            if match:
                # remove from players or spectators
                match["players"] = [p for p in match["players"] if p[0] != conn]
                if conn in match["spectators"]:
                    match["spectators"].discard(conn)
                # if no players left, delete match
                if not match["players"]:
                    del matches[mid]
                else:
                    broadcast_match(match, "NOTICE player_left")
        clients.pop(conn, None)
    send_line(conn, "OK bye")
    conn.close()

# ------------------ HILO POR CLIENTE ------------------
def handle_client(conn, addr):
    print(f"[+] Client connected {addr}")
    send_line(conn, "WELCOME to Tic-Tac-Toe. Send your name:")
    try:
        name = recv_line(conn).strip()
    except Exception:
        conn.close()
        return
    # register client
    with lock:
        clients[conn] = {"name": name, "match": None, "role": None}
    send_line(conn, f"HELLO {name}. Commands: CREATE_MATCH, JOIN_MATCH <id>, LIST_MATCHES, MOVE <id> <pos>, SPECTATE <id>, QUIT")
    try:
        while True:
            line = recv_line(conn).strip()
            if not line:
                continue
            parts = line.split()
            cmd = parts[0].upper()
            args = parts[1:]
            if cmd == "CREATE_MATCH":
                cmd_create_match(conn, name)
            elif cmd == "LIST_MATCHES":
                cmd_list_matches(conn)
            elif cmd == "JOIN_MATCH":
                cmd_join_match(conn, name, args)
            elif cmd == "MOVE":
                cmd_move(conn, name, args)
            elif cmd == "SPECTATE":
                cmd_spectate(conn, name, args)
            elif cmd == "QUIT":
                cmd_quit(conn)
                break
            else:
                send_line(conn, "ERR unknown command")
    except ConnectionError:
        # cliente desconectado
        cmd_quit(conn)
    except Exception as e:
        print(f"[!] Error handling client {addr}: {e}")
        cmd_quit(conn)

# ------------------ MAIN ------------------
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(8)
        print(f"Server listening on {HOST}:{PORT}")
        try:
            while True:
                conn, addr = srv.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("Shutting down server")

if __name__ == "__main__":
    main()
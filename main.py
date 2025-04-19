from dataclasses import dataclass
import json
from fastapi import FastAPI, Path
import socket
import re

with open("config/server_list.json", "r") as f:
    server_list = json.load(f)


def get_xonotic_server_status(host: str, port: int = 26000):
    request = b'\xFF\xFF\xFF\xFFgetstatus'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)

    try:
        sock.sendto(request, (host, port))
        data, _ = sock.recvfrom(4096)
        response = data.decode('utf-8', errors='ignore')

        max_players_match = re.search(r"sv_maxclients\\(\d+)", response)
        current_players_match = re.search(r"(?<!sv_)\\clients\\(\d+)", response)
        current_map = re.search(r"mapname//(\d+)", response)

        max_players = int(max_players_match.group(1))
        current_players = int(current_players_match.group(1))

        available_slots = max_players - current_players

        return {
            'players': current_players,
            'max_players': max_players,
            'available_slots': available_slots,
            "current_map": current_map
            }

    except socket.timeout:
        return {"error": "The server do not responding"}
    except Exception as e:
        return {"error": str(e)}
    
def monitor_server_for_end_of_game(host:str, port:str):
    map = None
    while True:
        status = get_xonotic_server_status(host, port)
        if status:
            players = status['players']
            if players <= 1:
                handle_end_of_game()
                break
        # time.sleep(5)

def handle_end_of_game():
    pass


@dataclass
class Server() :
    id: int
    port: int

app = FastAPI()

@app.get("/total_server")
def get_total_server() -> dict:
    return {"total":len(server_list)}

@app.get("/server")
def get_all_server() -> list[Server]:
    return server_list

@app.get("/server/{id}")
def get_server_by_id(id:int = Path(ge = 0)) -> Server :
    return server_list[id]

@app.get("/server_status/{id}")
def server_status (id:int = Path(ge = 0)):
    server =server_list[id]
    return get_xonotic_server_status("192.168.1.155", server["port"])
from dataclasses import dataclass
import json
from fastapi import FastAPI, Path, HTTPException
import socket
import re

wating_list = []
can_join:bool = False

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
    ip_address: str
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
    return get_xonotic_server_status(server["ip_address"], server["port"])

@app.post("/waiting_list/")
def add_user_to_waiting_list(name:str) -> str:
    if name in wating_list:
        raise HTTPException(status_code=404, detail=f"User {name} already in waiting list")
    wating_list.append(name)
    return name

@app.get("/waiting_list")
def get_waiting_list() -> list:
    return wating_list

@app.delete("/waiting_list/")
def remove_from_waiting_list(name):
    if name in wating_list:
        wating_list.remove(name)
    else:
        raise HTTPException(status_code=404, detail=f"User {name} no exist in waiting list")

@app.get("/waiting_list/player_can_join")
def player_can_join() -> dict:
    global can_join
    # server = server_list[1]
    if len(wating_list) >= 2:
        can_join = True
    # if get_xonotic_server_status(server["ip_address"], server["port"])["players"] == 2:
    #     can_join == False
    return {
        "can_join": can_join
        }
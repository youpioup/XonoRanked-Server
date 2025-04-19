from dataclasses import dataclass
from typing import Union
import json
from fastapi import FastAPI, Path

with open("config/server_list.json", "r") as f:
    server_list = json.load(f)

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
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .state import VotingSystem, SongStats

ROOT_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT_DIR / "app" / "static"
INDEX_HTML = STATIC_DIR / "index.html"

app = FastAPI(title="Music Voting")

# CORS - keep permissive for local dev; adjust for prod as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

voting = VotingSystem()


class AddSongRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class VoteRequest(BaseModel):
    selected: str = Field(min_length=1, max_length=200)
    other: str = Field(min_length=1, max_length=200)


class SongOut(BaseModel):
    name: str
    appearances: int
    wins: int
    winRate: float


@app.get("/")
def root() -> FileResponse:
    if not INDEX_HTML.exists():
        raise HTTPException(status_code=500, detail="Missing frontend index.html")
    return FileResponse(str(INDEX_HTML))


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/api/songs", response_model=List[SongOut])
def list_songs() -> List[SongOut]:
    names = voting.list_songs()
    result: List[SongOut] = []
    for name in names:
        stats: SongStats = voting._stats.get(name, SongStats())  # safe snapshot
        result.append(
            SongOut(
                name=name,
                appearances=stats.appearances,
                wins=stats.wins,
                winRate=stats.win_rate,
            )
        )
    return result


@app.post("/api/songs", status_code=201)
def add_song(payload: AddSongRequest):
    ok = voting.add_song(payload.name)
    if not ok:
        raise HTTPException(status_code=400, detail="Song exists or invalid name")
    return {"ok": True}


@app.delete("/api/songs/{name}")
def delete_song(name: str):
    ok = voting.remove_song(name)
    if not ok:
        raise HTTPException(status_code=404, detail="Song not found")
    return {"ok": True}


@app.get("/api/pair", response_model=Tuple[str, str])
def get_pair():
    try:
        left, right = voting.choose_pair()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return left, right


@app.post("/api/vote")
def vote(payload: VoteRequest):
    try:
        voting.record_vote(payload.selected, payload.other)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True}


@app.get("/api/leaderboard", response_model=List[SongOut])
def leaderboard() -> List[SongOut]:
    rows = voting.leaderboard()
    return [
        SongOut(
            name=name,
            appearances=stats.appearances,
            wins=stats.wins,
            winRate=stats.win_rate,
        )
        for name, stats in rows
    ]

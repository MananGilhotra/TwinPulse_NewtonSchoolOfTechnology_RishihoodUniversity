"""TwinPulse API. Run: .venv/bin/uvicorn api.main:app --reload --port 8000"""
from __future__ import annotations

import os
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from twinpulse import service  # noqa: E402

app = FastAPI(title="TwinPulse API", version="0.1.0",
              description="Digital twin that rehearses tonight to prevent night-time lows in children with T1D. "
                          "All patients served here are synthetic.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class WhatIf(BaseModel):
    snack_g: float = Field(0, ge=0, le=45, description="Bedtime snack at 22:30 (g carbohydrate)")
    dinner_rapid_pct: float = Field(0, ge=-50, le=30, description="Change to dinner-time rapid/regular insulin (%)")
    long_acting_pct: float = Field(0, ge=-50, le=30, description="Change to evening NPH/long-acting dose (%)")
    long_acting_shift_min: int = Field(0, ge=0, le=180, description="Move evening NPH/long-acting later (minutes)")
    skip_play: bool = Field(False, description="No evening play today")


def _check(pid: str):
    if pid not in service.cohort_meta():
        raise HTTPException(404, f"Unknown patient {pid}")


@app.get("/api/board")
def board():
    return {"tonight": service.TONIGHT.strftime("%Y-%m-%d"), "patients": service.board()}


@app.get("/api/patients/{pid}")
def patient(pid: str):
    _check(pid)
    return service.patient(pid)


@app.post("/api/patients/{pid}/whatif")
def whatif(pid: str, body: WhatIf):
    _check(pid)
    return service.whatif(pid, **body.model_dump())


@app.get("/api/validation")
def validation():
    return service.validation()


DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dashboard", "dist")
if os.path.isdir(DIST):
    app.mount("/", StaticFiles(directory=DIST, html=True), name="dashboard")

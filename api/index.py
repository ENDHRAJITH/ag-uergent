from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from statistics import mean

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

json_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "q-vercel-latency.json"
)

with open(json_path, "r") as f:
    DATA = json.load(f)


class RequestData(BaseModel):
    regions: list[str]
    threshold_ms: float


def percentile(values, p):
    values = sorted(values)
    k = (len(values) - 1) * p / 100

    f = int(k)
    c = min(f + 1, len(values) - 1)

    if f == c:
        return values[f]

    return values[f] + (values[c] - values[f]) * (k - f)


@app.get("/")
def home():
    return {"message": "Latency Analytics API Running"}


@app.post("/")
def analytics(req: RequestData):
    result = []

    for region in req.regions:
        records = [r for r in DATA if r["region"] == region]

        if not records:
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        result.append({
            "region": region,
            "avg_latency": round(mean(latencies), 2),
            "p95_latency": round(percentile(latencies, 95), 2),
            "avg_uptime": round(mean(uptimes), 3),
            "breaches": sum(
                1 for x in latencies
                if x > req.threshold_ms
            )
        })

    return result
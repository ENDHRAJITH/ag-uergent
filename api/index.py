from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from statistics import mean

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JSON file படிக்காம directly embed பண்ணிட்டோம்
DATA = [
  {"region":"apac","service":"checkout","latency_ms":202.99,"uptime_pct":98.473},
  {"region":"apac","service":"payments","latency_ms":159.03,"uptime_pct":98.59},
  {"region":"apac","service":"recommendations","latency_ms":198.03,"uptime_pct":99.167},
  {"region":"apac","service":"payments","latency_ms":196.2,"uptime_pct":97.237},
  {"region":"apac","service":"catalog","latency_ms":178.34,"uptime_pct":98.819},
  {"region":"apac","service":"support","latency_ms":158.09,"uptime_pct":97.505},
  {"region":"apac","service":"analytics","latency_ms":154.1,"uptime_pct":98.724},
  {"region":"apac","service":"analytics","latency_ms":115.65,"uptime_pct":98.563},
  {"region":"apac","service":"checkout","latency_ms":204.08,"uptime_pct":97.108},
  {"region":"apac","service":"payments","latency_ms":207.5,"uptime_pct":98.153},
  {"region":"apac","service":"recommendations","latency_ms":199.91,"uptime_pct":97.663},
  {"region":"apac","service":"catalog","latency_ms":206.95,"uptime_pct":97.856},
  {"region":"emea","service":"payments","latency_ms":174.98,"uptime_pct":97.298},
  {"region":"emea","service":"catalog","latency_ms":220.92,"uptime_pct":99.015},
  {"region":"emea","service":"recommendations","latency_ms":162.62,"uptime_pct":98.696},
  {"region":"emea","service":"checkout","latency_ms":164.96,"uptime_pct":99.037},
  {"region":"emea","service":"payments","latency_ms":230.55,"uptime_pct":99.079},
  {"region":"emea","service":"analytics","latency_ms":173.89,"uptime_pct":99.322},
  {"region":"emea","service":"catalog","latency_ms":173.65,"uptime_pct":98.938},
  {"region":"emea","service":"recommendations","latency_ms":156.61,"uptime_pct":97.22},
  {"region":"emea","service":"checkout","latency_ms":184.5,"uptime_pct":98.185},
  {"region":"emea","service":"catalog","latency_ms":178.06,"uptime_pct":98.38},
  {"region":"emea","service":"payments","latency_ms":166.2,"uptime_pct":98.595},
  {"region":"emea","service":"checkout","latency_ms":204.0,"uptime_pct":98.445},
  {"region":"amer","service":"analytics","latency_ms":221.79,"uptime_pct":97.984},
  {"region":"amer","service":"recommendations","latency_ms":135.76,"uptime_pct":99.092},
  {"region":"amer","service":"checkout","latency_ms":140.16,"uptime_pct":98.464},
  {"region":"amer","service":"recommendations","latency_ms":226.06,"uptime_pct":99.05},
  {"region":"amer","service":"payments","latency_ms":173.82,"uptime_pct":97.337},
  {"region":"amer","service":"payments","latency_ms":219.39,"uptime_pct":97.61},
  {"region":"amer","service":"analytics","latency_ms":178.47,"uptime_pct":99.485},
  {"region":"amer","service":"payments","latency_ms":125.51,"uptime_pct":98.903},
  {"region":"amer","service":"payments","latency_ms":189.58,"uptime_pct":98.148},
  {"region":"amer","service":"payments","latency_ms":221.43,"uptime_pct":97.757},
  {"region":"amer","service":"payments","latency_ms":173.01,"uptime_pct":97.674},
  {"region":"amer","service":"catalog","latency_ms":102.98,"uptime_pct":98.112},
]

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
            "breaches": sum(1 for x in latencies if x > req.threshold_ms)
        })
    return result
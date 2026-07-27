import os
import json
import numpy as np
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Dict, Any
from sklearn.ensemble import IsolationForest
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Biometrics Banking Security Engine")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define our Isolation Forest Model
# In a real scenario, this would be trained on historical clean data.
# For this prototype, we'll initialize it and "fit" it on some baseline data.
clf = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)

# Generate some dummy "normal" data to fit the model initially.
# Features: dwell_time (ms), flight_time (ms)
# Human typing typically has dwell times 50-150ms and flight times 100-300ms.
np.random.seed(42)
normal_dwell = np.random.normal(100, 20, 1000)
normal_flight = np.random.normal(200, 40, 1000)
X_train = np.column_stack((normal_dwell, normal_flight))
clf.fit(X_train)

class KeystrokeEvent(BaseModel):
    eventType: str
    targetId: str
    timestamp: float
    metadata: Dict[str, float]

class FraudCheckRequest(BaseModel):
    events: List[KeystrokeEvent]

@app.post("/api/v1/fraud-check")
async def check_fraud(payload: FraudCheckRequest):
    # Simple feature extraction: compute average dwell time and flight time from the batch
    dwell_times = []
    flight_times = []
    
    last_keydown_time = None
    
    for event in payload.events:
        if event.eventType == 'keydown':
            if last_keydown_time is not None:
                flight_time = event.timestamp - last_keydown_time
                if flight_time > 0 and flight_time < 2000: # Filter out anomalies
                    flight_times.append(flight_time)
            last_keydown_time = event.timestamp
        elif event.eventType == 'keyup':
            # We assume metadata contains dwellTime or we calculate it. 
            dwell_time = event.metadata.get('dwellTime')
            if dwell_time is not None:
                dwell_times.append(dwell_time)
                
    if not dwell_times or not flight_times:
        # Not enough data to score, return safe
        return {"status": "CLEAN", "score": 0.0}
        
    avg_dwell = np.mean(dwell_times)
    avg_flight = np.mean(flight_times)
    
    X_test = np.array([[avg_dwell, avg_flight]])
    score = clf.decision_function(X_test)[0]
    
    # Transform score: decision_function is roughly between -0.5 and 0.5. 
    # Negative scores are anomalies.
    # anomaly_score = 0.5 - score maps positive (inliers) to lower anomaly score
    anomaly_score = 0.5 - score
    
    # Clamp between 0 and 1
    anomaly_score = max(0.0, min(1.0, anomaly_score))
    
    status = "CLEAN"
    if anomaly_score >= 0.70:
        status = "LOCKED"
    elif anomaly_score >= 0.62:
        status = "FLAGGED"
        
    return {
        "status": status,
        "score": float(anomaly_score),
        "details": {
            "avg_dwell": float(avg_dwell),
            "avg_flight": float(avg_flight)
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

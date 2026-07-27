# Real-time ML-Powered Behavioral Biometrics Engine - Backend

This is the backend service for the **Behavioral Biometrics Engine**, built with Python and FastAPI. It serves as the decision-making brain of the system, utilizing an **Isolation Forest** model to detect typing anomalies in real-time.

## Key Features

- **Real-time Anomaly Detection:** Uses an **Isolation Forest** model to score streaming user behavior data (keystrokes) with sub-second latency.
- **Streaming-Optimized API:** Fast and efficient endpoints designed to receive continuous `(keydown, keyup)` events.
- **On-the-fly Feature Extraction:** Calculates vital biometric metrics like average dwell time, flight time, and inter-key intervals instantaneously.
- **Security State Evaluation:** Evaluates the telemetry against the trained model and returns immediate status codes: `CLEAN`, `FLAGGED`, or `LOCKED`.

## Technology Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Machine Learning:** `scikit-learn` (Isolation Forest), `NumPy`, `pandas`
- **Server:** `uvicorn`

## Getting Started

### Prerequisites

- **Python** 3.11 or higher
- **pip**

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Running the Server

Start the FastAPI development server:
```bash
uvicorn main:app --reload
```
The backend API will be available at `http://localhost:8000`. 
API documentation (Swagger UI) can be accessed at `http://localhost:8000/docs`.

## Model Training & Evaluation

The Isolation Forest model can be retrained on custom datasets to adapt to specific user behaviors.

**Usage:**
```bash
python scripts/train_model.py --dataset path/to/your/data.csv
```

This script will:
1. Train the `IsolationForest` on your provided telemetry data.
2. Generate a `model.pkl` file in the `data/` directory.
3. Evaluate the model's accuracy and output a performance report.

## License

MIT License

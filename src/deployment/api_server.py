"""
Production API Server

FastAPI-based REST API for racing predictions.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest
from pydantic import BaseModel, Field

from src.deployment.model_registry import ModelRegistry
from src.monitoring.alerting import AlertManager
from src.monitoring.performance_tracker import PerformanceTracker


# Pydantic models for request/response
class PredictionRequest(BaseModel):
    """Request model for predictions."""

    features: list[float] = Field(..., description="Feature vector for prediction")
    race_id: str | None = Field(None, description="Race identifier")


class PredictionResponse(BaseModel):
    """Response model for predictions."""

    prediction: int = Field(..., description="Predicted class (0 or 1)")
    probability: float = Field(..., description="Win probability")
    latency_ms: float = Field(..., description="Prediction latency in milliseconds")
    model_version: str = Field(..., description="Model version used")


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(..., description="Health status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    model_version: str | None = Field(None, description="Active model version")
    uptime_seconds: float = Field(..., description="API uptime in seconds")


class MetricsResponse(BaseModel):
    """Response model for metrics."""

    total_predictions: int
    mean_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    accuracy: float | None = None
    calibration_error: float | None = None


# Global state
model = None
model_metadata = None
model_registry = None
performance_tracker = None
alert_manager = None
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    global model, model_metadata, model_registry, performance_tracker, alert_manager

    model_registry = ModelRegistry()
    performance_tracker = PerformanceTracker()
    alert_manager = AlertManager()

    try:
        model, model_metadata = model_registry.get_active_model()
        print(f"Loaded model: {model_metadata['name']}:{model_metadata['version']}")
    except Exception as e:
        print(f"Warning: Could not load active model: {e}")

    yield

    # Shutdown
    print("Shutting down API server")


app = FastAPI(
    title="Racing Analysis API",
    description="Production API for horse racing predictions",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Racing Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "metrics": "/metrics",
            "prometheus": "/prometheus"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if model is not None else "degraded",
        model_loaded=model is not None,
        model_version=f"{model_metadata['name']}:{model_metadata['version']}" if model_metadata else None,
        uptime_seconds=time.time() - start_time
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(request: PredictionRequest):
    """
    Make a prediction.

    Args:
        request: Prediction request with features

    Returns:
        Prediction response with probability and metadata
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Convert features to numpy array
    features = np.array(request.features).reshape(1, -1)

    # Time prediction
    start = time.time()

    try:
        # Get prediction and probability
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features)[0, 1]
            prediction = int(proba > 0.5)
        else:
            prediction = int(model.predict(features)[0])
            proba = float(prediction)

        latency = time.time() - start

        # Track performance
        if performance_tracker:
            performance_tracker.track_prediction(
                prediction=prediction,
                probability=proba,
                latency=latency,
                features=features[0]
            )

        # Check for alerts
        if alert_manager and performance_tracker:
            metrics = performance_tracker.get_metrics()
            if 'p99_latency_ms' in metrics:
                alert_manager.check_and_alert(
                    "latency_p99",
                    metrics['p99_latency_ms'] / 1000,
                    higher_is_better=False
                )

        return PredictionResponse(
            prediction=prediction,
            probability=proba,
            latency_ms=latency * 1000,
            model_version=f"{model_metadata['name']}:{model_metadata['version']}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.get("/metrics", response_model=MetricsResponse, tags=["Monitoring"])
async def get_metrics():
    """
    Get performance metrics.

    Returns:
        Current performance metrics
    """
    if performance_tracker is None:
        raise HTTPException(status_code=503, detail="Performance tracker not initialized")

    metrics = performance_tracker.get_metrics()

    return MetricsResponse(
        total_predictions=metrics.get("total_predictions", 0),
        mean_latency_ms=metrics.get("mean_latency_ms", 0.0),
        p95_latency_ms=metrics.get("p95_latency_ms", 0.0),
        p99_latency_ms=metrics.get("p99_latency_ms", 0.0),
        accuracy=metrics.get("accuracy"),
        calibration_error=metrics.get("calibration_error")
    )


@app.get("/prometheus", response_class=PlainTextResponse, tags=["Monitoring"])
async def prometheus_metrics():
    """
    Export Prometheus metrics.

    Returns:
        Prometheus-formatted metrics
    """
    return generate_latest()


@app.post("/feedback", tags=["Feedback"])
async def submit_feedback(race_id: str, runner_id: str, actual_result: int):
    """
    Submit actual race results for model evaluation.

    Args:
        race_id: Race identifier
        runner_id: Runner identifier
        actual_result: Actual outcome (1 = win, 0 = loss)
    """
    # In production, this would update the tracking system
    # For now, just acknowledge
    return {
        "status": "received",
        "race_id": race_id,
        "runner_id": runner_id,
        "result": actual_result
    }


@app.post("/reload-model", tags=["Admin"])
async def reload_model():
    """
    Reload the active model from registry.

    Returns:
        New model information
    """
    global model, model_metadata

    if model_registry is None:
        raise HTTPException(status_code=503, detail="Model registry not initialized")

    try:
        model, model_metadata = model_registry.get_active_model()
        return {
            "status": "success",
            "model": f"{model_metadata['name']}:{model_metadata['version']}",
            "loaded_at": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload model: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

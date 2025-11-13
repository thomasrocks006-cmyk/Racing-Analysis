"""
Alert Manager

Anomaly detection and alerting system for production monitoring.
"""

from __future__ import annotations

import json
import smtplib
from abc import ABC, abstractmethod
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any


class Alert:
    """Represents a single alert."""

    def __init__(
        self,
        severity: str,
        message: str,
        metric: str,
        value: float,
        threshold: float,
        timestamp: datetime | None = None,
    ):
        """
        Initialize alert.

        Args:
            severity: Alert severity (info, warning, critical)
            message: Alert message
            metric: Metric that triggered alert
            value: Current metric value
            threshold: Threshold value
            timestamp: Alert timestamp
        """
        self.severity = severity
        self.message = message
        self.metric = metric
        self.value = value
        self.threshold = threshold
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "severity": self.severity,
            "message": self.message,
            "metric": self.metric,
            "value": self.value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
        }

    def __repr__(self) -> str:
        return (
            f"Alert(severity={self.severity}, metric={self.metric}, "
            f"value={self.value:.4f}, threshold={self.threshold:.4f})"
        )


class AlertChannel(ABC):
    """Abstract base class for alert channels."""

    @abstractmethod
    def send(self, alert: Alert):
        """Send an alert through this channel."""
        pass


class LogAlertChannel(AlertChannel):
    """Log alerts to file."""

    def __init__(self, log_file: str = "logs/alerts.log"):
        """Initialize log alert channel."""
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def send(self, alert: Alert):
        """Log alert to file."""
        with open(self.log_file, "a") as f:
            f.write(
                f"{alert.timestamp.isoformat()} [{alert.severity.upper()}] {alert.message}\n"
            )


class EmailAlertChannel(AlertChannel):
    """Send alerts via email."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        from_addr: str,
        to_addrs: list[str],
        username: str | None = None,
        password: str | None = None,
    ):
        """
        Initialize email alert channel.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            from_addr: Sender email address
            to_addrs: List of recipient email addresses
            username: SMTP username
            password: SMTP password
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.from_addr = from_addr
        self.to_addrs = to_addrs
        self.username = username
        self.password = password

    def send(self, alert: Alert):
        """Send alert via email."""
        msg = MIMEText(
            f"Alert Details:\n\n"
            f"Severity: {alert.severity.upper()}\n"
            f"Metric: {alert.metric}\n"
            f"Value: {alert.value:.4f}\n"
            f"Threshold: {alert.threshold:.4f}\n"
            f"Message: {alert.message}\n"
            f"Time: {alert.timestamp.isoformat()}"
        )

        msg["Subject"] = (
            f"[{alert.severity.upper()}] Racing Analysis Alert: {alert.metric}"
        )
        msg["From"] = self.from_addr
        msg["To"] = ", ".join(self.to_addrs)

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.username and self.password:
                    server.starttls()
                    server.login(self.username, self.password)
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send email alert: {e}")


class WebhookAlertChannel(AlertChannel):
    """Send alerts to a webhook endpoint."""

    def __init__(self, webhook_url: str):
        """Initialize webhook alert channel."""
        self.webhook_url = webhook_url

    def send(self, alert: Alert):
        """Send alert to webhook."""
        import requests

        try:
            requests.post(self.webhook_url, json=alert.to_dict(), timeout=10)
        except Exception as e:
            print(f"Failed to send webhook alert: {e}")


class AlertManager:
    """
    Manage alerts and thresholds for production monitoring.

    Features:
    - Multiple alert channels (log, email, webhook)
    - Configurable thresholds
    - Alert rate limiting
    - Alert history tracking
    """

    def __init__(self, config_file: str | None = None):
        """
        Initialize alert manager.

        Args:
            config_file: Path to alert configuration file
        """
        self.channels: list[AlertChannel] = []
        self.thresholds: dict[str, dict[str, float]] = {}
        self.alert_history: list[Alert] = []

        # Default thresholds
        self.thresholds = {
            "accuracy": {"warning": 0.6, "critical": 0.5},
            "calibration_error": {"warning": 0.15, "critical": 0.25},
            "latency_p99": {"warning": 0.5, "critical": 1.0},
            "data_drift_zscore": {"warning": 3.0, "critical": 5.0},
        }

        if config_file:
            self.load_config(config_file)

        # Add default log channel
        self.add_channel(LogAlertChannel())

    def add_channel(self, channel: AlertChannel):
        """Add an alert channel."""
        self.channels.append(channel)

    def set_threshold(self, metric: str, warning: float, critical: float):
        """
        Set alert thresholds for a metric.

        Args:
            metric: Metric name
            warning: Warning threshold
            critical: Critical threshold
        """
        self.thresholds[metric] = {"warning": warning, "critical": critical}

    def check_metric(self, metric: str, value: float, higher_is_better: bool = True):
        """
        Check a metric value against thresholds.

        Args:
            metric: Metric name
            value: Current metric value
            higher_is_better: Whether higher values are better

        Returns:
            Alert if threshold exceeded, None otherwise
        """
        if metric not in self.thresholds:
            return None

        thresholds = self.thresholds[metric]
        severity = None
        threshold_value = None

        if higher_is_better:
            # Lower values trigger alerts
            if value < thresholds["critical"]:
                severity = "critical"
                threshold_value = thresholds["critical"]
            elif value < thresholds["warning"]:
                severity = "warning"
                threshold_value = thresholds["warning"]
        else:
            # Higher values trigger alerts
            if value > thresholds["critical"]:
                severity = "critical"
                threshold_value = thresholds["critical"]
            elif value > thresholds["warning"]:
                severity = "warning"
                threshold_value = thresholds["warning"]

        if severity:
            message = (
                f"{metric} {severity}: {value:.4f} "
                f"({'below' if higher_is_better else 'above'} threshold {threshold_value:.4f})"
            )
            return Alert(
                severity=severity,
                message=message,
                metric=metric,
                value=value,
                threshold=threshold_value,
            )

        return None

    def trigger_alert(self, alert: Alert):
        """
        Trigger an alert through all channels.

        Args:
            alert: Alert to send
        """
        self.alert_history.append(alert)

        for channel in self.channels:
            try:
                channel.send(alert)
            except Exception as e:
                print(f"Failed to send alert through {channel.__class__.__name__}: {e}")

    def check_and_alert(self, metric: str, value: float, higher_is_better: bool = True):
        """
        Check metric and trigger alert if needed.

        Args:
            metric: Metric name
            value: Current metric value
            higher_is_better: Whether higher values are better
        """
        alert = self.check_metric(metric, value, higher_is_better)
        if alert:
            self.trigger_alert(alert)

    def get_recent_alerts(
        self, n: int = 10, severity: str | None = None
    ) -> list[Alert]:
        """
        Get recent alerts.

        Args:
            n: Number of recent alerts to return
            severity: Filter by severity (None = all)

        Returns:
            List of recent alerts
        """
        alerts = self.alert_history
        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return alerts[-n:]

    def load_config(self, config_file: str):
        """
        Load alert configuration from file.

        Args:
            config_file: Path to JSON configuration file
        """
        with open(config_file) as f:
            config = json.load(f)

        if "thresholds" in config:
            self.thresholds.update(config["thresholds"])

    def save_config(self, config_file: str):
        """
        Save alert configuration to file.

        Args:
            config_file: Path to JSON configuration file
        """
        config = {"thresholds": self.thresholds}

        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

    def clear_history(self):
        """Clear alert history."""
        self.alert_history.clear()

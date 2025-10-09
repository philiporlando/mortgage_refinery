import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RateHistory(BaseModel):
    """Store the history of rate checks and alerts."""

    last_checked_rate: Optional[float] = None
    last_alerted_rate: Optional[float] = None
    last_alert_time: Optional[datetime] = None
    last_check_time: Optional[datetime] = None
    alert_count: int = 0

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
        }


class RateTracker:
    """Manage rate tracking and alert decisions."""

    def __init__(self, state_file: Path = Path("/tmp/mortgage_rate_state.json")):
        self.state_file = state_file
        self.history = self._load_history()

    def _load_history(self) -> RateHistory:
        """Load rate history from state file."""
        if not self.state_file.exists():
            logger.info("No existing reate history found, starting fresh.")
            return RateHistory()

        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)
                # Convert ISO format strings back to datetime
                if data.get("last_alert_time"):
                    data["last_alert_time"] = datetime.fromisoformat(data["last_alert_time"])
                if data.get("last_check_time"):
                    data["last_check_time"] = datetime.fromisoformat(data["last_check_time"])
                return RateHistory(**data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error loading rate history: {e}")
            raise RuntimeError("Failed to load rate history.") from e

    def _save_history(self) -> None:
        """Persist rate history to state file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self.history.model_dump(), f, indent=2, default=str)
            logger.info(f"Saved rate history to {self.state_file}")

    def should_send_alert(self, current_rate: float, threshold: float) -> bool:
        """Determine if an alert should be sent based on the current rate and history."""
        if current_rate >= threshold:
            logger.info(
                f"Current rate {current_rate}% is above threshold {threshold}%, no alert needed."
            )
            return False

        if self.history.last_alerted_rate is None:
            logger.info(f"Rate {current_rate}% is below threshold {threshold}% for the first time!")
            return True

        if current_rate < self.history.last_alerted_rate:
            logger.info(
                f"Rate dropped from {self.history.last_alerted_rate}% to {current_rate}%, sending alert."
            )
            return True

        logger.info(
            f"Rate {current_rate}% is below threshold but not lower than last alert "
            f"({self.history.last_alerted_rate}), no alert needed."
        )
        return False

    def record_check(self, current_rate: float) -> None:
        """Record that we checked the rate."""
        self.history.last_checked_rate = current_rate
        self.history.last_check_time = datetime.now()
        self._save_history()
        logger.debug(f"Recorded rate check: {current_rate}%")

    def record_alert(self, alerted_rate: float) -> None:
        """Record that we sent an alert for this rate."""
        self.history.last_alerted_rate = alerted_rate
        self.history.last_alert_time = datetime.now()
        self.history.alert_count += 1
        self._save_history()
        logger.info(f"Recorded alert #{self.history.alert_count} for rate: {alerted_rate}%")

    def get_summary(self) -> str:
        """Get a human-readable summary of the tracking history."""
        if self.history.last_check_time is None:
            return "No rate checks performed yet."

        summary = [
            f"Last checked: {self.history.last_check_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Latest rate: {self.history.last_checked_rate}%",
        ]

        if self.history.last_alerted_rate is not None:
            summary.extend(
                [
                    f"Last alerted rate: {self.history.last_alerted_rate}%",
                    f"Last alert time: {self.history.last_alert_time.strftime('%Y-%m-%d %H:%M:%S')}",
                    f"Total alerts sent: {self.history.alert_count}",
                ]
            )
        else:
            summary.append("No alerts sent yet")

        return "\n".join(summary)

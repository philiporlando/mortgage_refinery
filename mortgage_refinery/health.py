import time
from typing import Any, Dict, Optional

from mortgage_refinery.email import send_email
from mortgage_refinery.logging import logger

ALERT_COOLDOWN_SECONDS = 3600  # re-alert at most once per hour while still unhealthy


class HealthMonitor:
    """Tracks consecutive check failures and emails the admin when the app is unhealthy."""

    def __init__(self):
        self.consecutive_failures = 0
        self.last_alert_time: Optional[float] = None

    def record_failure(self, config: Dict[str, Any], error: Exception) -> None:
        """Record a failed check, alerting immediately and then at most once per cooldown."""
        self.consecutive_failures += 1
        now = time.monotonic()
        should_alert = self.last_alert_time is None or (
            now - self.last_alert_time >= ALERT_COOLDOWN_SECONDS
        )

        if should_alert:
            self._send_alert(config, error)
            self.last_alert_time = now

    def record_success(self, config: Dict[str, Any]) -> None:
        """Record a successful check, sending a recovery email if we were previously failing."""
        if self.consecutive_failures > 0:
            self._send_recovery(config)
        self.consecutive_failures = 0
        self.last_alert_time = None

    def _send_alert(self, config: Dict[str, Any], error: Exception) -> None:
        try:
            send_email(
                config,
                subject="Mortgage Refinery: app is unhealthy",
                body=(
                    f"The mortgage-refinery health check has failed "
                    f"{self.consecutive_failures} time(s) in a row.\n\n"
                    f"Latest error:\n{error}\n\n"
                    f"Check the container logs for the full traceback."
                ),
            )
            logger.info("Health alert email sent.")
        except Exception as e:
            logger.error(f"Failed to send health alert email: {e}", exc_info=True)

    def _send_recovery(self, config: Dict[str, Any]) -> None:
        try:
            send_email(
                config,
                subject="Mortgage Refinery: app has recovered",
                body=(
                    f"The mortgage-refinery health check succeeded again after "
                    f"{self.consecutive_failures} consecutive failure(s)."
                ),
            )
            logger.info("Health recovery email sent.")
        except Exception as e:
            logger.error(f"Failed to send health recovery email: {e}", exc_info=True)

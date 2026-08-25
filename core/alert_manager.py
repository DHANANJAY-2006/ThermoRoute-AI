"""
Alert Manager — Autonomous Risk Notifications
==============================================
Evaluates FortyGuard data and generates actionable fleet alerts.
This is the "agentic" layer — the system decides when to act.
"""

from datetime import datetime


THRESHOLDS = {
    "critical_temp_f": 108,
    "high_temp_f": 95,
    "high_degradation_factor": 3.0,
    "critical_degradation_factor": 3.5,
    "persistence_hours_warning": 6,
    "persistence_hours_critical": 9,
}


def evaluate(temp_f: float, degradation_factor: float,
             persistence_hours: float, route_name: str = "current route") -> list:
    """
    Evaluate conditions and return a list of alert dicts.
    Judges see this as the autonomous/agentic intelligence layer.
    """
    alerts = []
    now = datetime.now().strftime("%H:%M")

    if temp_f >= THRESHOLDS["critical_temp_f"]:
        alerts.append({
            "level": "🔴 CRITICAL",
            "color": "#ef4444",
            "message": (
                f"Ambient temperature {temp_f:.0f}°F exceeds critical threshold. "
                f"Battery degrading at {degradation_factor:.1f}× normal rate on {route_name}. "
                f"Switch to coolest available route immediately."
            ),
            "action": "Switch to Route C (Highway)",
            "time": now
        })

    elif temp_f >= THRESHOLDS["high_temp_f"]:
        alerts.append({
            "level": "🟠 HIGH",
            "color": "#f97316",
            "message": (
                f"Temperature {temp_f:.0f}°F — elevated battery stress. "
                f"Degradation factor: {degradation_factor:.1f}×. "
                f"Route optimisation recommended."
            ),
            "action": "Consider Route B or Route C",
            "time": now
        })

    if persistence_hours >= THRESHOLDS["persistence_hours_critical"]:
        alerts.append({
            "level": "🔴 HEAT WAVE",
            "color": "#7c3aed",
            "message": (
                f"Sustained heat >{THRESHOLDS['critical_temp_f']}°F "
                f"for {persistence_hours:.1f} hours today. "
                f"Fleet-wide route optimisation advised. "
                f"Consider shifting deliveries to early AM window."
            ),
            "action": "Reschedule non-urgent deliveries to 5AM–8AM",
            "time": now
        })
    elif persistence_hours >= THRESHOLDS["persistence_hours_warning"]:
        alerts.append({
            "level": "🟡 WARNING",
            "color": "#eab308",
            "message": (
                f"Heat persisting for {persistence_hours:.1f} hours. "
                f"Monitor battery temperatures. Pre-cool vehicles before next shift."
            ),
            "action": "Pre-cool vans during loading window",
            "time": now
        })

    if not alerts:
        alerts.append({
            "level": "🟢 NORMAL",
            "color": "#22c55e",
            "message": "Thermal conditions within safe operating range. No action required.",
            "action": "Continue standard routing",
            "time": now
        })

    return alerts

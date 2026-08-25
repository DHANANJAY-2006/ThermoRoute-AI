"""
Alert Manager — Autonomous Risk Notifications
==============================================
Evaluates FortyGuard data and generates actionable fleet alerts.
Provides automated decision support for dispatch and route management.
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
    """
    alerts = []
    now = datetime.now().strftime("%H:%M")

    if temp_f >= THRESHOLDS["critical_temp_f"]:
        alerts.append({
            "level": "CRITICAL RISK",
            "color": "#ef4444",
            "message": (
                f"Ambient temperature {temp_f:.0f}°F exceeds operational safety threshold. "
                f"Battery degradation rate is {degradation_factor:.1f}x nominal on {route_name}. "
                f"Immediate diversion to lowest thermal exposure corridor advised."
            ),
            "action": "Divert fleet to Highway Corridor (Route C)",
            "time": now
        })

    elif temp_f >= THRESHOLDS["high_temp_f"]:
        alerts.append({
            "level": "ELEVATED RISK",
            "color": "#f97316",
            "message": (
                f"Ambient temperature {temp_f:.0f}°F presents accelerated cell degradation risk. "
                f"Degradation factor: {degradation_factor:.1f}x nominal. "
                f"Route optimization recommended."
            ),
            "action": "Assess Route B or Route C alternatives",
            "time": now
        })

    if persistence_hours >= THRESHOLDS["persistence_hours_critical"]:
        alerts.append({
            "level": "SUSTAINED HEATWAVE",
            "color": "#7c3aed",
            "message": (
                f"Continuous thermal exposure >{THRESHOLDS['critical_temp_f']}°F "
                f"persisting for {persistence_hours:.1f} hours. "
                f"System-wide dispatch adjustment indicated."
            ),
            "action": "Reschedule high-draw transit cycles to early morning window (05:00–08:00)",
            "time": now
        })
    elif persistence_hours >= THRESHOLDS["persistence_hours_warning"]:
        alerts.append({
            "level": "THERMAL ADVISORY",
            "color": "#eab308",
            "message": (
                f"Thermal persistence threshold reached ({persistence_hours:.1f} continuous hours). "
                f"Initiate pre-conditioning protocol during depot staging."
            ),
            "action": "Pre-condition battery packs during dock charging",
            "time": now
        })

    if not alerts:
        alerts.append({
            "level": "NOMINAL STATUS",
            "color": "#22c55e",
            "message": "Thermal conditions within standard operational tolerance. No intervention required.",
            "action": "Maintain active dispatch plan",
            "time": now
        })

    return alerts

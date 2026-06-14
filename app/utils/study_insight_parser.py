"""
Rule-based study insight generator as fallback when Ollama is unavailable.
"""
from datetime import datetime
from typing import Any


def generate_study_insights(sessions: list[dict[str, Any]], tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate study insights based on session data using rule-based analysis."""
    insights: list[str] = []
    recommendations: list[str] = []

    if not sessions:
        insights.append("No study sessions recorded yet. Start a pomodoro to begin tracking!")
        recommendations.append("Begin with 25-minute focus sessions to build a study habit.")
        return {"insights": insights, "recommendations": recommendations}

    # Analyze total study time
    total_minutes = sum(s.get("actualMinutes", 0) or s.get("actual_minutes", 0) for s in sessions)
    total_hours = total_minutes / 60

    if total_hours > 4:
        insights.append(f"You've studied {total_hours:.1f} hours. Great dedication!")
    elif total_hours > 1:
        insights.append(f"You've studied {total_hours:.1f} hours. Keep it up!")
    else:
        insights.append(f"You've studied {total_minutes} minutes. Try to increase your study time.")

    # Analyze completion rate
    completed = sum(1 for s in sessions if (s.get("status") or s.get("Status")) == "completed")
    total = len(sessions)
    completion_rate = (completed / total * 100) if total > 0 else 0

    if completion_rate >= 80:
        insights.append(f"Your completion rate is {completion_rate:.0f}%. Excellent focus!")
    elif completion_rate >= 50:
        insights.append(f"Your completion rate is {completion_rate:.0f}%. Try to finish more sessions.")
        recommendations.append("Minimize distractions during focus time.")
    else:
        insights.append(f"Your completion rate is {completion_rate:.0f}%. Consider shorter sessions.")
        recommendations.append("Try 15-minute sessions to build focus stamina.")

    # Analyze time of day patterns
    morning = sum(1 for s in sessions if _get_hour(s) < 12)
    afternoon = sum(1 for s in sessions if 12 <= _get_hour(s) < 18)
    evening = sum(1 for s in sessions if _get_hour(s) >= 18)

    best_period = "morning" if morning >= afternoon and morning >= evening else \
                  "afternoon" if afternoon >= evening else "evening"
    insights.append(f"You are most productive in the {best_period}.")
    recommendations.append(f"Schedule important study tasks in the {best_period}.")

    # Analyze task completion
    if tasks:
        completed_tasks = sum(1 for t in tasks if (t.get("status") or t.get("Status")) == "completed")
        total_tasks = len(tasks)
        if total_tasks > 0:
            task_rate = completed_tasks / total_tasks * 100
            if task_rate < 50:
                recommendations.append("Focus on completing existing tasks before starting new ones.")

    return {"insights": insights, "recommendations": recommendations}


def _get_hour(session: dict[str, Any]) -> int:
    """Extract hour from session start time."""
    start = session.get("startTime") or session.get("start_time", "")
    if isinstance(start, str) and len(start) >= 11:
        try:
            return int(start[11:13])
        except (ValueError, IndexError):
            pass
    return 12  # default to noon

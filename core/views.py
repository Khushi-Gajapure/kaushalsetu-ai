from django.shortcuts import render, get_object_or_404

from .models import Employee
from .services.skill_gap import calculate_skill_gaps


def dashboard(request):
    employee = get_object_or_404(
        Employee,
        user__username="rahul"
    )

    gaps = calculate_skill_gaps(employee)

    high_count = sum(
        1 for gap in gaps
        if gap["priority"] == "High"
    )

    medium_count = sum(
        1 for gap in gaps
        if gap["priority"] == "Medium"
    )

    low_count = sum(
        1 for gap in gaps
        if gap["priority"] == "Low"
    )

    return render(
        request,
        "core/dashboard.html",
        {
            "employee": employee,
            "gaps": gaps,
            "high_count": high_count,
            "medium_count": medium_count,
            "low_count": low_count,
        },
    )
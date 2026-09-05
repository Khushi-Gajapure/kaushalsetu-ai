from django.shortcuts import render, get_object_or_404

from .models import Employee
from .services.skill_gap import calculate_skill_gaps


def dashboard(request):
    employee = get_object_or_404(
        Employee,
        user__username="rahul"
    )

    gaps = calculate_skill_gaps(employee)

    return render(
        request,
        "core/dashboard.html",
        {
            "employee": employee,
            "gaps": gaps,
        },
    )
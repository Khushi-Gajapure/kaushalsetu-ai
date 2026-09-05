from core.models import EmployeeCompetency


def calculate_skill_gaps(employee):
    """
    Calculate competency gaps for an employee.

    Gap = Required Level - Current Level

    Returns the competencies with their gap and priority.
    """

    employee_competencies = EmployeeCompetency.objects.filter(
        employee=employee
    ).select_related("competency")

    results = []

    for item in employee_competencies:
        gap = max(item.required_level - item.current_level, 0)

        if gap >= 2:
            priority = "High"
        elif gap == 1:
            priority = "Medium"
        else:
            priority = "Low"

        results.append({
            "competency": item.competency.name,
            "current_level": item.current_level,
            "required_level": item.required_level,
            "gap": gap,
            "priority": priority,
        })

    # Highest gap first
    results.sort(
        key=lambda item: item["gap"],
        reverse=True
    )

    return results
from core.models import (
    Course,
    Employee,
    EmployeeCompetency,
    LearningRecommendation,
)


def generate_recommendations(employee):
    """
    Generate learning recommendations based on
    the employee's competency gaps.
    """

    # Remove old incomplete recommendations
    LearningRecommendation.objects.filter(
        employee=employee,
        completed=False
    ).delete()

    recommendations = []

    employee_competencies = (
        EmployeeCompetency.objects
        .filter(employee=employee)
        .select_related("competency")
    )

    courses = Course.objects.all()

    for item in employee_competencies:

        gap = item.gap

        if gap == 0:
            continue

        if gap >= 2:
            priority = "High"
        else:
            priority = "Medium"

        competency_name = item.competency.name.lower()

        for course in courses:

            course_skills = course.skills.lower()

            if competency_name in course_skills:

                reason = (
                    f"Your current level in "
                    f"{item.competency.name} is "
                    f"{item.current_level}, while the "
                    f"required level is "
                    f"{item.required_level}. "
                    f"This course can help reduce "
                    f"your competency gap."
                )

                recommendation = LearningRecommendation.objects.create(
                    employee=employee,
                    course=course,
                    competency=item.competency,
                    priority=priority,
                    reason=reason,
                )

                recommendations.append(recommendation)

    return recommendations
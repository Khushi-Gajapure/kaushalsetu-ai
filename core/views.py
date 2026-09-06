from django.shortcuts import render, get_object_or_404, redirect
from .services.recommendations import generate_recommendations
from .models import (
    Employee,
    LearningRecommendation,
    LearningMaterial,
    Quiz,
    Assessment,
    EmployeeCompetency,
)
from .services.skill_gap import calculate_skill_gaps


def dashboard(request):
    employee = get_object_or_404(
        Employee,
        user__username="rahul"
    )

    gaps = calculate_skill_gaps(employee)

    assessments = Assessment.objects.filter(
        employee=employee
    ).select_related(
        "quiz"
    ).order_by(
        "-completed_at"
    )

    if assessments:
        total_score = sum(
            assessment.score
            for assessment in assessments
            if assessment.quiz
        )

        total_possible = sum(
            assessment.quiz.questions.count()
            for assessment in assessments
            if assessment.quiz
        )

        learning_progress = (
            round((total_score / total_possible) * 100)
            if total_possible
            else 0
        )
    else:
        learning_progress = 0

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
            "assessments": assessments,
            "learning_progress": learning_progress,
        },
    )
def recommendations(request):
    employee = get_object_or_404(
        Employee,
        user__username="rahul"
    )

    recommendations = LearningRecommendation.objects.filter(
        employee=employee
    ).select_related(
        "course",
        "competency"
    )

    if request.method == "POST":
        recommendation_id = request.POST.get("recommendation_id")

        recommendation = get_object_or_404(
            LearningRecommendation,
            id=recommendation_id,
            employee=employee
        )

        recommendation.completed = True
        recommendation.save()

        return redirect("recommendations")

    return render(
        request,
        "core/recommendations.html",
        {
            "employee": employee,
            "recommendations": recommendations,
        },
    )
def upload_material(request):
    employee = get_object_or_404(
        Employee,
        user__username="rahul"
    )

    if request.method == "POST":
        title = request.POST.get("title")
        uploaded_file = request.FILES.get("file")

        if title and uploaded_file:
            LearningMaterial.objects.create(
                title=title,
                file=uploaded_file,
            )

            return render(
                request,
                "core/upload_material.html",
                {
                    "employee": employee,
                    "success": True,
                },
            )

    return render(
        request,
        "core/upload_material.html",
        {
            "employee": employee,
        },
    )
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(
        Quiz.objects.prefetch_related(
            "questions__competency"
        ),
        id=quiz_id,
    )

    questions = quiz.questions.all()

    if request.method == "POST":

        score = 0

        # Track competency performance
        competency_results = {}

        for question in questions:

            selected_answer = request.POST.get(
                f"question_{question.id}"
            )

            is_correct = (
                selected_answer == question.correct_answer
            )

            if is_correct:
                score += 1

            # Only track questions that have a competency
            if question.competency:

                competency_id = question.competency.id

                if competency_id not in competency_results:
                    competency_results[competency_id] = {
                        "correct": 0,
                        "total": 0,
                    }

                competency_results[competency_id]["total"] += 1

                if is_correct:
                    competency_results[competency_id]["correct"] += 1

        # -----------------------------
        # Find Employee
        # -----------------------------

        employee = get_object_or_404(
            Employee,
            user__username="rahul"
        )

        # -----------------------------
        # Save Assessment
        # -----------------------------

        Assessment.objects.create(
            employee=employee,
            quiz=quiz,
            score=score,
        )

        # -----------------------------
        # Update Competency Levels
        # -----------------------------

        for competency_id, result in competency_results.items():

            percentage = (
                result["correct"] / result["total"]
            ) * 100

            employee_competency = EmployeeCompetency.objects.filter(
                employee=employee,
                competency_id=competency_id
            ).first()

            if employee_competency:

                if percentage >= 80:
                    increase = 1
                else:
                    increase = 0

                employee_competency.current_level = min(
                    employee_competency.current_level + increase,
                    employee_competency.required_level
                )

                employee_competency.save()

        # -----------------------------
        # Regenerate Recommendations
        # -----------------------------

        generate_recommendations(employee)

        return render(
            request,
            "core/quiz_result.html",
            {
                "quiz": quiz,
                "score": score,
                "total": questions.count(),
            },
        )

    return render(
        request,
        "core/take_quiz.html",
        {
            "quiz": quiz,
            "questions": questions,
        },
    )
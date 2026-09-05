from django.shortcuts import render, get_object_or_404

from .models import (
    Employee,
    LearningRecommendation,
    LearningMaterial,
    Quiz,
)
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
def recommendations(request):
    employee = get_object_or_404(
        Employee,
        user__username="rahul"
    )

    recommendations = LearningRecommendation.objects.filter(
        employee=employee,
        completed=False
    ).select_related(
        "course",
        "competency"
    )

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
        Quiz.objects.prefetch_related("questions"),
        id=quiz_id,
    )

    questions = quiz.questions.all()

    if request.method == "POST":
        score = 0

        for question in questions:
            selected_answer = request.POST.get(
                f"question_{question.id}"
            )

            if selected_answer == question.correct_answer:
                score += 1

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
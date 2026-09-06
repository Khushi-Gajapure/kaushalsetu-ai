from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from .models import (
    Employee,
    LearningRecommendation,
    LearningMaterial,
    Quiz,
    QuizQuestion,
    Assessment,
    EmployeeCompetency,
    Competency,
)

from .services.skill_gap import calculate_skill_gaps
from .services.recommendations import generate_recommendations
from .services.pdf_extractor import extract_text_from_pdf
from .services.quiz_generator import generate_quiz_questions


def get_or_create_employee(user):
    employee, _ = Employee.objects.get_or_create(
        user=user,
        defaults={
            "role": "Employee",
            "department": "General",
            "experience_years": 0,
        },
    )
    return employee


# ============================================================
# LOGOUT
# ============================================================

def kaushalsetu_logout(request):
    logout(request)
    return redirect("landing")


# ============================================================
# EMPLOYEE PROFILE
# ============================================================

@login_required
def profile(request):

    employee = get_or_create_employee(request.user)

    competencies = (
        EmployeeCompetency.objects
        .filter(employee=employee)
        .select_related("competency")
    )

    assessments = (
        Assessment.objects
        .filter(employee=employee)
        .select_related("quiz")
        .order_by("-completed_at")
    )

    completed_recommendations = (
        LearningRecommendation.objects
        .filter(employee=employee, completed=True)
        .select_related("course")
    )

    return render(
        request,
        "core/profile.html",
        {
            "employee": employee,
            "competencies": competencies,
            "assessments": assessments,
            "completed_recommendations": completed_recommendations,
        },
    )


# ============================================================
# LANDING PAGE
# ============================================================

def landing(request):
    return render(request, "core/landing.html")


# ============================================================
# LOGIN
# ============================================================

class KaushalSetuLoginView(LoginView):
    template_name = "core/login.html"
    redirect_authenticated_user = True


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def dashboard(request):

    employee = get_or_create_employee(request.user)

    gaps = calculate_skill_gaps(employee)

    assessments = (
        Assessment.objects
        .filter(employee=employee)
        .select_related("quiz")
        .order_by("-completed_at")
    )

    if assessments:
        total_score = sum(a.score for a in assessments if a.quiz)
        total_possible = sum(a.quiz.questions.count() for a in assessments if a.quiz)
        learning_progress = round((total_score / total_possible) * 100) if total_possible else 0
    else:
        learning_progress = 0

    high_count = sum(1 for gap in gaps if gap["priority"] == "High")
    medium_count = sum(1 for gap in gaps if gap["priority"] == "Medium")
    low_count = sum(1 for gap in gaps if gap["priority"] == "Low")

    baseline_quiz = Quiz.objects.filter(title="Baseline Competency Assessment").first()

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
            "baseline_quiz": baseline_quiz,
        },
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

@login_required
def recommendations(request):

    employee = get_or_create_employee(request.user)

    if request.method == "POST":
        recommendation_id = request.POST.get("recommendation_id")
        recommendation = get_object_or_404(
            LearningRecommendation, id=recommendation_id, employee=employee
        )
        recommendation.completed = True
        recommendation.save()
        return redirect("recommendations")

    recommendations = (
        LearningRecommendation.objects
        .filter(employee=employee, completed=False)
        .select_related("course", "competency")
    )

    return render(
        request,
        "core/recommendations.html",
        {"employee": employee, "recommendations": recommendations},
    )


# ============================================================
# UPLOAD LEARNING MATERIAL
# ============================================================

@login_required
def upload_material(request):

    employee = get_or_create_employee(request.user)

    if request.method == "POST":

        title = request.POST.get("title")
        uploaded_file = request.FILES.get("file")

        if not title or not uploaded_file:
            return render(
                request,
                "core/upload_material.html",
                {"employee": employee, "error": "Please provide both a title and a file."},
            )

        material = LearningMaterial.objects.create(title=title, file=uploaded_file)

        quiz = None
        generation_error = None

        try:
            text = extract_text_from_pdf(material.file.path)

            if not text.strip():
                raise ValueError("No extractable text found in this file.")

            quiz_data = generate_quiz_questions(text, number_of_questions=5)

            quiz = Quiz.objects.create(material=material, title=f"Quiz: {title}")

            for question in quiz_data.get("questions", []):
                competency = None
                competency_name = question.get("competency")
                if competency_name:
                    competency, _ = Competency.objects.get_or_create(name=competency_name)

                QuizQuestion.objects.create(
                    quiz=quiz,
                    question=question.get("question", ""),
                    option_a=question.get("option_a", ""),
                    option_b=question.get("option_b", ""),
                    option_c=question.get("option_c", ""),
                    option_d=question.get("option_d", ""),
                    correct_answer=question.get("correct_answer", "A"),
                    explanation=question.get("explanation", ""),
                    difficulty=question.get("difficulty", "Medium"),
                    competency=competency,
                )

        except Exception as exc:
            generation_error = str(exc)

        return render(
            request,
            "core/upload_material.html",
            {"employee": employee, "success": True, "quiz": quiz, "generation_error": generation_error},
        )

    return render(request, "core/upload_material.html", {"employee": employee})


# ============================================================
# TAKE QUIZ
# ============================================================

@login_required
def take_quiz(request, quiz_id):

    quiz = get_object_or_404(
        Quiz.objects.prefetch_related("questions__competency"), id=quiz_id
    )

    questions = quiz.questions.all()

    if request.method == "POST":

        score = 0
        competency_results = {}

        for question in questions:
            selected_answer = request.POST.get(f"question_{question.id}")
            is_correct = selected_answer == question.correct_answer

            if is_correct:
                score += 1

            if question.competency:
                cid = question.competency.id
                if cid not in competency_results:
                    competency_results[cid] = {"correct": 0, "total": 0}
                competency_results[cid]["total"] += 1
                if is_correct:
                    competency_results[cid]["correct"] += 1

        employee = get_or_create_employee(request.user)

        Assessment.objects.create(employee=employee, quiz=quiz, score=score)

        weak_topics = []

        for competency_id, result in competency_results.items():
            if result["total"] == 0:
                continue

            percentage = (result["correct"] / result["total"]) * 100

            employee_competency, _ = EmployeeCompetency.objects.get_or_create(
                employee=employee,
                competency_id=competency_id,
                defaults={"current_level": 1, "required_level": 3},
            )

            increase = 1 if percentage >= 80 else 0
            employee_competency.current_level = min(
                employee_competency.current_level + increase,
                employee_competency.required_level,
            )
            employee_competency.save()

            if percentage < 60:
                weak_topics.append(employee_competency.competency.name)

        generate_recommendations(employee)

        return render(
            request,
            "core/quiz_result.html",
            {"quiz": quiz, "score": score, "total": questions.count(), "weak_topics": weak_topics},
        )

    return render(request, "core/take_quiz.html", {"quiz": quiz, "questions": questions})
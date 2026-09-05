from django.contrib.auth.models import User
from django.db import models


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)
    department = models.CharField(max_length=150)
    experience_years = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Competency(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class EmployeeCompetency(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE)

    current_level = models.PositiveIntegerField(default=1)
    required_level = models.PositiveIntegerField(default=1)

    @property
    def gap(self):
        return max(self.required_level - self.current_level, 0)

    def __str__(self):
        return f"{self.employee} - {self.competency}"


class Assessment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    quiz = models.ForeignKey(
        "Quiz",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    score = models.FloatField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.quiz} - {self.score}"


class AssessmentQuestion(models.Model):
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_answer = models.CharField(max_length=1)

    competency = models.ForeignKey(
        Competency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )


class Course(models.Model):
    course_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    skills = models.CharField(max_length=500, blank=True)
    level = models.CharField(max_length=50, default="Beginner")
    duration_hours = models.FloatField(default=0)
    source = models.CharField(
        max_length=100,
        default="iGOT Karmayogi"
    )

    def __str__(self):
        return self.title


class LearningRecommendation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    competency = models.ForeignKey(
        Competency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    priority = models.CharField(
        max_length=20,
        default="Medium"
    )

    reason = models.TextField(blank=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.employee} - {self.course}"


class LearningMaterial(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(
        upload_to="learning_materials/"
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class Quiz(models.Model):
    material = models.ForeignKey(
        LearningMaterial,
        on_delete=models.CASCADE,
        related_name="quizzes"
    )

    title = models.CharField(max_length=200)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)

    correct_answer = models.CharField(max_length=1)

    explanation = models.TextField(blank=True)

    difficulty = models.CharField(
        max_length=30,
        default="Medium"
    )

    competency = models.ForeignKey(
        Competency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
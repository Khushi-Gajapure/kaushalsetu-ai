from django.contrib import admin

from .models import (
    Employee,
    Competency,
    EmployeeCompetency,
    Assessment,
    AssessmentQuestion,
    Course,
    LearningRecommendation,
    LearningMaterial,
    Quiz,
    QuizQuestion,
)


admin.site.register(Employee)
admin.site.register(Competency)
admin.site.register(EmployeeCompetency)
admin.site.register(Assessment)
admin.site.register(AssessmentQuestion)
admin.site.register(Course)
admin.site.register(LearningRecommendation)
admin.site.register(LearningMaterial)
admin.site.register(Quiz)
admin.site.register(QuizQuestion)
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from core.models import (
    Employee,
    Competency,
    EmployeeCompetency,
    Course,
)


class Command(BaseCommand):
    help = "Creates demo data for KaushalSetu AI"

    def handle(self, *args, **kwargs):

        # -------------------------------------------------
        # 1. Create Competencies
        # -------------------------------------------------

        competencies_data = [
            ("Statistical Analysis", "Data analysis and statistical methods", "Statistics"),
            ("Python", "Python programming for data analysis", "Technical"),
            ("SQL", "Database querying and data management", "Technical"),
            ("Data Visualization", "Creating charts and statistical dashboards", "Technical"),
            ("Survey & Sampling", "Survey design and sampling techniques", "Statistics"),
            ("Machine Learning", "Machine learning concepts and applications", "AI"),
            ("Official Statistics", "Concepts and practices of official statistics", "Domain"),
        ]

        competencies = {}

        for name, description, category in competencies_data:
            competency, _ = Competency.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "category": category,
                },
            )
            competencies[name] = competency

        # -------------------------------------------------
        # 2. Create Demo Employee
        # -------------------------------------------------

        user, created = User.objects.get_or_create(
            username="rahul",
            defaults={
                "first_name": "Rahul",
                "last_name": "Sharma",
                "email": "rahul@example.com",
            },
        )

        if created:
            user.set_password("Rahul@12345")
            user.save()

        employee, _ = Employee.objects.get_or_create(
            user=user,
            defaults={
                "role": "Statistical Officer",
                "department": "National Statistical Office",
                "experience_years": 3,
            },
        )

        # -------------------------------------------------
        # 3. Create Skill Levels
        # -------------------------------------------------

        skill_levels = {
            "Python": (2, 4),
            "SQL": (3, 4),
            "Statistical Analysis": (4, 4),
            "Data Visualization": (2, 4),
            "Survey & Sampling": (3, 4),
            "Machine Learning": (1, 3),
            "Official Statistics": (4, 4),
        }

        for skill_name, (current, required) in skill_levels.items():

            EmployeeCompetency.objects.update_or_create(
                employee=employee,
                competency=competencies[skill_name],
                defaults={
                    "current_level": current,
                    "required_level": required,
                },
            )

        # -------------------------------------------------
        # 4. Create Demo Courses
        # -------------------------------------------------

        courses_data = [
            (
                "IGOT-PY-101",
                "Python for Data Analysis",
                "Learn Python programming for statistical and data analysis.",
                "Python,Data Analysis",
                "Intermediate",
                12,
            ),
            (
                "IGOT-SQL-101",
                "SQL for Data Management",
                "Learn SQL for querying and managing statistical databases.",
                "SQL,Database",
                "Intermediate",
                8,
            ),
            (
                "IGOT-DV-101",
                "Data Visualization for Statistics",
                "Create effective statistical charts and dashboards.",
                "Data Visualization,Statistics",
                "Intermediate",
                10,
            ),
            (
                "IGOT-ML-101",
                "Introduction to Machine Learning",
                "Understand machine learning concepts and applications.",
                "Machine Learning,Python",
                "Beginner",
                15,
            ),
            (
                "IGOT-SS-101",
                "Survey and Sampling Methods",
                "Learn survey design and sampling techniques.",
                "Survey & Sampling,Statistics",
                "Intermediate",
                10,
            ),
            (
                "IGOT-OS-101",
                "Fundamentals of Official Statistics",
                "Understand principles and practices of official statistics.",
                "Official Statistics",
                "Beginner",
                6,
            ),
        ]

        for (
            course_id,
            title,
            description,
            skills,
            level,
            duration,
        ) in courses_data:

            Course.objects.update_or_create(
                course_id=course_id,
                defaults={
                    "title": title,
                    "description": description,
                    "skills": skills,
                    "level": level,
                    "duration_hours": duration,
                    "source": "iGOT Karmayogi",
                },
            )

        # -------------------------------------------------
        # Finished
        # -------------------------------------------------

        self.stdout.write(
            self.style.SUCCESS(
                "KaushalSetu demo data created successfully!"
            )
        )
import factory
from factory.django import DjangoModelFactory

from apps.accounts.models import Company, User
from apps.applications.models import Application
from apps.interviews.models import Interview
from apps.vacancies.models import Vacancy


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Faker("company")
    industry = factory.Faker("bs")
    size = Company.Size.SMALL
    country = factory.Faker("country")


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.django.Password("testpass123")
    role = User.Role.HR
    company = factory.SubFactory(CompanyFactory)
    is_active = True
    email_verified = True


class VacancyFactory(DjangoModelFactory):
    class Meta:
        model = Vacancy

    company = factory.SubFactory(CompanyFactory)
    created_by = factory.SubFactory(UserFactory, company=factory.SelfAttribute("..company"))
    title = factory.Faker("job")
    description = factory.Faker("paragraph", nb_sentences=3)
    status = Vacancy.Status.PUBLISHED


class ApplicationFactory(DjangoModelFactory):
    class Meta:
        model = Application

    vacancy = factory.SubFactory(VacancyFactory)
    candidate_name = factory.Faker("name")
    candidate_email = factory.Faker("email")
    status = Application.Status.APPLIED


class InterviewFactory(DjangoModelFactory):
    class Meta:
        model = Interview

    application = factory.SubFactory(ApplicationFactory)
    session_type = Interview.SessionType.PRESCANNING
    screening_mode = Interview.ScreeningMode.CHAT
    status = Interview.Status.PENDING

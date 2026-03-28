from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.common.messages import MSG_CRITERIA_NOT_FOUND, MSG_QUESTION_NOT_FOUND, MSG_VACANCY_NOT_FOUND
from apps.vacancies.models import ScreeningStep
from apps.vacancies.selectors import get_vacancy_by_id, get_vacancy_criteria, get_vacancy_questions
from apps.vacancies.serializers import InterviewQuestionOutputSerializer, VacancyCriteriaOutputSerializer
from apps.vacancies.services import (
    add_interview_question,
    add_vacancy_criteria,
    delete_interview_question,
    delete_vacancy_criteria,
    generate_interview_questions,
    update_interview_question,
    update_vacancy_criteria,
)


class VacancyCriteriaListCreateApi(APIView):
    """
    GET  /api/hr/vacancies/{id}/criteria/?step=prescanning — list criteria
    POST /api/hr/vacancies/{id}/criteria/ — add criteria
    """

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255)
        description = serializers.CharField(required=False, allow_blank=True, default="")
        weight = serializers.IntegerField(required=False, default=1, min_value=1, max_value=5)
        step = serializers.ChoiceField(
            choices=ScreeningStep.choices,
            required=False,
            default=ScreeningStep.PRESCANNING,
        )

    def get(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        step = request.query_params.get("step")
        criteria = get_vacancy_criteria(vacancy=vacancy, step=step)
        return Response(
            VacancyCriteriaOutputSerializer(criteria, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        criteria = add_vacancy_criteria(vacancy=vacancy, **serializer.validated_data)
        return Response(
            VacancyCriteriaOutputSerializer(criteria).data,
            status=status.HTTP_201_CREATED,
        )


class VacancyCriteriaDetailApi(APIView):
    """
    PUT    /api/hr/vacancies/{id}/criteria/{criteria_id}/ — update
    DELETE /api/hr/vacancies/{id}/criteria/{criteria_id}/ — delete
    """

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255, required=False)
        description = serializers.CharField(required=False, allow_blank=True)
        weight = serializers.IntegerField(required=False, min_value=1, max_value=5)
        order = serializers.IntegerField(required=False)

    def put(self, request: Request, vacancy_id: str, criteria_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        criteria = vacancy.criteria.filter(id=criteria_id).first()
        if criteria is None:
            return Response({"detail": str(MSG_CRITERIA_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        criteria = update_vacancy_criteria(criteria=criteria, **serializer.validated_data)
        return Response(
            VacancyCriteriaOutputSerializer(criteria).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request, vacancy_id: str, criteria_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        criteria = vacancy.criteria.filter(id=criteria_id).first()
        if criteria is None:
            return Response({"detail": str(MSG_CRITERIA_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        delete_vacancy_criteria(criteria=criteria)
        return Response(status=status.HTTP_204_NO_CONTENT)


class VacancyQuestionListCreateApi(APIView):
    """
    GET  /api/hr/vacancies/{id}/questions/?step=prescanning — list questions
    POST /api/hr/vacancies/{id}/questions/ — add question
    """

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class InputSerializer(serializers.Serializer):
        text = serializers.CharField()
        category = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
        step = serializers.ChoiceField(
            choices=ScreeningStep.choices,
            required=False,
            default=ScreeningStep.PRESCANNING,
        )

    def get(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        step = request.query_params.get("step")
        questions = get_vacancy_questions(vacancy=vacancy, active_only=False, step=step)
        return Response(
            InterviewQuestionOutputSerializer(questions, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = add_interview_question(vacancy=vacancy, **serializer.validated_data)
        return Response(
            InterviewQuestionOutputSerializer(question).data,
            status=status.HTTP_201_CREATED,
        )


class VacancyQuestionDetailApi(APIView):
    """
    PUT    /api/hr/vacancies/{id}/questions/{question_id}/ — update
    DELETE /api/hr/vacancies/{id}/questions/{question_id}/ — delete
    """

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class InputSerializer(serializers.Serializer):
        text = serializers.CharField(required=False)
        category = serializers.CharField(max_length=100, required=False, allow_blank=True)
        order = serializers.IntegerField(required=False)
        is_active = serializers.BooleanField(required=False)

    def put(self, request: Request, vacancy_id: str, question_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        question = vacancy.questions.filter(id=question_id).first()
        if question is None:
            return Response({"detail": str(MSG_QUESTION_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = update_interview_question(question=question, **serializer.validated_data)
        return Response(
            InterviewQuestionOutputSerializer(question).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request, vacancy_id: str, question_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        question = vacancy.questions.filter(id=question_id).first()
        if question is None:
            return Response({"detail": str(MSG_QUESTION_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        delete_interview_question(question=question)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenerateQuestionsApi(APIView):
    """POST /api/hr/vacancies/{id}/questions/generate/ — AI-generate questions."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class InputSerializer(serializers.Serializer):
        step = serializers.ChoiceField(
            choices=ScreeningStep.choices,
            required=False,
            default=ScreeningStep.PRESCANNING,
        )

    def post(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        step = serializer.validated_data.get("step", ScreeningStep.PRESCANNING)
        questions = generate_interview_questions(vacancy=vacancy, step=step)
        return Response(
            InterviewQuestionOutputSerializer(questions, many=True).data,
            status=status.HTTP_201_CREATED,
        )

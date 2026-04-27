from datetime import timedelta

from django.utils import timezone

from apps.accounts.apis.candidate_profile import MIN_CANDIDATE_AGE, CandidateProfileApi


def _years_ago(years: int):
    today = timezone.localdate()
    try:
        return today.replace(year=today.year - years)
    except ValueError:
        return today.replace(year=today.year - years, day=28)


def test_candidate_profile_accepts_fourteen_year_old_date_of_birth():
    serializer = CandidateProfileApi.InputSerializer(data={"date_of_birth": _years_ago(MIN_CANDIDATE_AGE)})

    assert serializer.is_valid(), serializer.errors


def test_candidate_profile_rejects_under_fourteen_date_of_birth():
    too_young = _years_ago(MIN_CANDIDATE_AGE) + timedelta(days=1)
    serializer = CandidateProfileApi.InputSerializer(data={"date_of_birth": too_young})

    assert not serializer.is_valid()
    assert "at least 14 years old" in str(serializer.errors["date_of_birth"][0])

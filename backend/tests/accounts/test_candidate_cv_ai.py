from apps.accounts.apis.candidate_cv_ai import CvImproveSectionApi


def test_cv_improve_section_serializer_accepts_headline():
    serializer = CvImproveSectionApi.InputSerializer(
        data={
            "section": "headline",
            "content": "Frontend developer",
        }
    )

    assert serializer.is_valid(), serializer.errors

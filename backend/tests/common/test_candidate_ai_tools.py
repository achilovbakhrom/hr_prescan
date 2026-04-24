from apps.common.candidate_ai_assistant.tools import build_langchain_tools


def test_build_my_cv_array_fields_have_item_schemas():
    tool = next(item for item in build_langchain_tools(user=None) if item.name == "build_my_cv")
    schema = tool.args_schema.model_json_schema()

    assert schema["properties"]["skills"]["items"]["type"] == "string"

    for field in [
        "work_experiences",
        "educations",
        "languages",
        "certifications",
    ]:
        assert schema["properties"][field]["type"] == "array"
        assert schema["properties"][field]["items"]["type"] == "object"

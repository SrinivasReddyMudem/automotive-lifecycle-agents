"""Copy export must preserve complete engineering answers, including hidden fields."""
from pydantic import BaseModel

from sdk_agents.core.response_copy import response_markdown
from sdk_agents.tests.integrator.test_can_bus_analyst import make_valid_output


def test_can_export_contains_tools_causes_calculations_and_attribution():
    output = make_valid_output()
    text = response_markdown("CAN bus-off after 3 minutes", "CAN Bus Analyst", output)
    assert "CAN bus-off after 3 minutes" in text
    assert "CAN Bus Analyst" in text
    assert output.tool_selection.primary in text
    assert output.tool_selection.fallback in text
    for cause in output.probable_causes:
        assert cause.description in text
        assert cause.test in text
        assert cause.pass_criteria in text
        assert cause.fail_criteria in text
    for line in output.tec_math:
        assert line in text
    for question in output.narrowing_questions:
        assert question.question in text
        assert question.yes_consequence in text
        assert question.no_consequence in text
    assert "Srinivas Reddy Mudem" in text


def test_export_preserves_code_unicode_and_untrusted_text_as_data():
    class Output(BaseModel):
        test_code: list[str]
        input_analysis: dict
        optional_value: str | None = None

    output = Output(
        test_code=["/* ``` */", "return elapsed >= 100;"],
        input_analysis={"facts": ["<script>alert('α')</script>", "CAN — 500 kbit/s"],
                        "assumptions": []},
    )
    text = response_markdown("Question", "Agent", output)
    assert "````\n/* ``` */\nreturn elapsed >= 100;\n````" in text
    assert "<script>alert('α')</script>" in text
    assert "CAN — 500 kbit/s" in text
    assert "None listed." in text
    assert "Not provided." in text

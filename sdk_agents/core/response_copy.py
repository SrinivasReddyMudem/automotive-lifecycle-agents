"""Complete Markdown export and a browser-local clipboard button."""

import re
from pathlib import Path


_ACRONYMS = {word.lower(): word for word in (
    "CAN", "AUTOSAR", "OSI", "TEC", "REC", "UDS", "DTC", "NRC", "RTOS",
    "CFSR", "MISRA", "ASPICE", "ASIL", "SIL", "HIL", "CPU", "MC/DC",
)}
_CODE_FIELDS = {"code_pattern", "test_code", "compliant_fix", "compliant_rewrite",
                "arxml", "arxml_example", "decision_flow"}


def _label(key):
    return " ".join(_ACRONYMS.get(word.lower(), word.capitalize())
                    for word in key.split("_"))


def _fenced(text):
    # Preserve source code even when the response itself contains Markdown fences.
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}\n{text}\n{fence}"


def _sections(data, depth=2):
    parts = []
    for key, value in data.items():
        parts.append(f"{'#' * min(depth, 6)} {_label(key)}")
        if key in _CODE_FIELDS and isinstance(value, (str, list)):
            text = value if isinstance(value, str) else "\n".join(map(str, value))
            parts.append(_fenced(text))
        elif isinstance(value, dict):
            parts.append(_sections(value, depth + 1))
        elif isinstance(value, list):
            if not value:
                parts.append("None listed.")
            for index, item in enumerate(value, 1):
                if isinstance(item, dict):
                    parts.append(f"{'#' * min(depth + 1, 6)} Item {index}")
                    parts.append(_sections(item, depth + 2))
                else:
                    parts.append("- " + str(item).replace("\n", "\n  "))
        elif value is None:
            parts.append("Not provided.")
        elif isinstance(value, bool):
            parts.append("Yes" if value else "No")
        else:
            parts.append(str(value))
    return "\n\n".join(parts)


def response_markdown(prompt, agent_name, output):
    """Export every structured field, independent of collapsed UI sections."""
    data = output.model_dump(mode="json")
    return (f"# Engineering response\n\n**Agent:** {agent_name}\n\n"
            f"## Question\n\n{prompt}\n\n{_sections(data)}\n\n"
            "---\n\nGenerated with Domain-Specific AI Agents — "
            "a personal project by Srinivas Reddy Mudem.\n")


def render_copy_button(prompt, agent_name, output, key):
    """Copy only on a user click; no model calls or clipboard reads."""
    from streamlit.components.v1 import declare_component

    component = declare_component(
        "copy_full_response", path=str(Path(__file__).with_name("copy_component"))
    )
    component(text=response_markdown(prompt, agent_name, output), key=key, default=None)

"""
Loads skill content from the shared skills/ folder.
Both md_agents (via Claude Code) and sdk_agents (via this loader) use the same skills.
"""

from pathlib import Path

# skills/ is two levels up from sdk_agents/core/
SKILLS_ROOT = Path(__file__).parents[2] / "skills"


def load_skill(skill_name: str) -> str:
    """
    Load SKILL.md + all reference files for a given skill.
    Returns combined content as a single string for injection into system prompt.
    """
    skill_dir = SKILLS_ROOT / skill_name
    if not skill_dir.exists():
        raise FileNotFoundError(
            f"Skill '{skill_name}' not found at {skill_dir}. "
            f"Available: {[d.name for d in SKILLS_ROOT.iterdir() if d.is_dir()]}"
        )

    parts = []

    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        parts.append(skill_md.read_text(encoding="utf-8"))

    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        for ref_file in sorted(refs_dir.glob("*.md")):
            parts.append(ref_file.read_text(encoding="utf-8"))

    return "\n\n".join(parts)


def load_skills(*skill_names: str) -> str:
    """Load multiple skills and combine them."""
    return "\n\n---\n\n".join(load_skill(name) for name in skill_names)

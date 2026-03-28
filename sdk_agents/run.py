"""
CLI entry point for sdk_agents — secondary interface for testing and automation.
Primary interface is: streamlit run sdk_agents/app.py

Usage:
  python sdk_agents/run.py --agent can-bus-analyst --prompt "CAN node goes bus-off..."
  python sdk_agents/run.py --agent can-bus-analyst   (interactive mode)
"""

import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))  # noqa: E402

from dotenv import load_dotenv  # noqa: E402
load_dotenv(Path(__file__).parent / ".env")

from sdk_agents.core.registry import get_agent, AGENT_NAMES  # noqa: E402
from sdk_agents.core.base_agent import AgentError  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Automotive Lifecycle Agents — SDK CLI"
    )
    parser.add_argument(
        "--agent",
        required=True,
        help=f"Agent name. Available: {AGENT_NAMES}",
    )
    parser.add_argument(
        "--prompt",
        help="User message. Omit for interactive mode.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted text.",
    )
    args = parser.parse_args()

    try:
        agent = get_agent(args.agent)
    except KeyError as e:
        print(str(e))
        sys.exit(1)

    def run_prompt(prompt: str):
        result = agent.run(prompt)
        if isinstance(result, AgentError):
            print(f"\n[ERROR] {result.error_type}: {result.message}")
            if result.raw_response:
                print(f"Raw response: {result.raw_response[:500]}")
        else:
            if args.json:
                print(json.dumps(result.model_dump(), indent=2))
            else:
                _print_result(result, args.agent)

    if args.prompt:
        run_prompt(args.prompt)
    else:
        print(f"Agent: {args.agent} (interactive — type 'exit' to quit)")
        while True:
            try:
                prompt = input("\nPrompt: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if prompt.lower() in ("exit", "quit", "q"):
                break
            if prompt:
                run_prompt(prompt)


def _print_result(result, agent_name: str):
    """Minimal terminal formatting for CLI output."""
    from rich.console import Console
    from rich.panel import Panel

    console = Console(highlight=False, emoji=False)
    # Force ASCII-safe output on Windows terminals that don't support UTF-8
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ("cp1252", "cp850", "ascii"):
        console = Console(highlight=False, emoji=False, force_terminal=True, legacy_windows=False)

    if agent_name in ("can-bus-analyst", "can_bus_analyst", "can-bus"):
        console.print(Panel(result.expert_diagnosis, title="Expert Diagnosis", style="bold blue"))
        console.print(f"OSI Layer: [bold]{result.osi_layer}[/bold]  |  "
                      f"AUTOSAR: [bold]{result.autosar_layer}[/bold]  |  "
                      f"Tool: [bold]{result.recommended_tool}[/bold]")
        console.print("\n[bold]TEC Math:[/bold]")
        console.print(result.tec_math)

        console.print("\n[bold]Probable Causes:[/bold]")
        for i, cause in enumerate(result.probable_causes, 1):
            console.print(f"\n  {i}. [{cause.rank}] {cause.description}")
            console.print(f"     Test: {cause.test}")
            console.print(f"     Pass: {cause.pass_criteria}")
            console.print(f"     Fail: {cause.fail_criteria}")

        console.print("\n[bold]Decision Flow:[/bold]")
        console.print(result.decision_flow)

        console.print("\n[bold]Narrowing Questions:[/bold]")
        for i, q in enumerate(result.narrowing_questions, 1):
            console.print(f"\n  Q{i}: {q.question}")
            console.print(f"    Yes: {q.yes_consequence}")
            console.print(f"    No : {q.no_consequence}")
    else:
        # Fallback — dump JSON for agents without a dedicated formatter yet
        console.print_json(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    main()

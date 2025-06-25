# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "google-genai==1.7.0",
#     "pyyaml",
#     "requests",
#     "tiktoken",
# ]
# ///
"""Check quality scale for an integration."""

import argparse
import datetime
import json
import ast
import subprocess
import sys
import time
import yaml
from pathlib import Path

from google import genai
import requests
import tiktoken

FREE_MODEL = "gemini-2.5-flash"
PAID_MODEL = "gemini-2.5-pro"
QUALITY_SCALE_RULE_RAW_URL = "https://raw.githubusercontent.com/home-assistant/developers.home-assistant/refs/heads/master/docs/core/integration-quality-scale/rules/{}.md"
QUALITY_SCALE_RULE_DOCS_URL = (
    "https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/{}"
)
DOCS_URL = "https://www.home-assistant.io/integrations/{}/"

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "generated"

HA_FILES = {
    "manifest.json",
    "strings.json",
    "services.yaml",
    "icons.json",
}

IGNORE_FILES = {
    "open_epaper_link": {
        "image_decompressor.py",
        "imagegen.py",
    }
}

RULE_REVIEW_PROMPT = """
You are an expert Home Assistant code reviewer specializing in the Integration Quality Scale. Your task is to meticulously analyze a given Home Assistant integration's code against a specific quality scale rule.

**Goal:**
Generate a Markdown report assessing if the `{integration}` follows the rule `{rule}`.

**Input You Will Receive:**
1.  The name of the integration: {integration}.
2.  The name of the rule being checked: {rule}.
3.  The full text and requirements of the rule.
4.  The code for the integration

**Output Requirements:**

The report must be in Markdown format and determine one of three statuses:
*   **"todo"**: The rule applies to this integration, AND the integration currently does NOT follow it.
*   **"done"**: The rule applies to this integration, AND the integration fully follows it.
*   **"exempt"**: The rule does NOT apply to this integration.

**Report Structure:**

1.  **Title:**
    ```markdown
    # {integration}: {rule}
    ```

2.  **Information Table:**
    ```markdown
    | Info   | Value                                                                    |
    |--------|--------------------------------------------------------------------------|
    | Name   | [{integration}](https://www.home-assistant.io/integrations/{integration}/) |
    | Rule   | [{rule}]({rule_url})                                                     |
    | Status | **todo** OR **done** OR **exempt**                                       |
    | Reason | (Only include if Status is "exempt". Explain why the rule does not apply.) |
    ```

3.  **Overview Section:**
    *   **Heading:** `## Overview`
    *   **Content:**
        *   Start by clearly stating if the rule applies to the integration and why.
        *   If it applies, explain in detail whether the integration follows the rule or not.
        *   **Crucially, reference specific parts of the provided code or identify missing components/patterns to justify your assessment.**
        *   If the rule does not apply (status "exempt"), expand on the "Reason" from the table, providing more context if necessary.

4.  **Suggestions Section (Conditional):**
    *   **Heading:** `## Suggestions`
    *   **Content:**
        *   **Only include this section if the Status is "todo".**
        *   Provide clear, actionable, and specific steps the developer can take to make the integration compliant with the rule.
        *   If possible, include examples of code changes or additions.
        *   Explain *why* these changes would satisfy the rule.
        *   If Status is "done" or "exempt", omit this entire section or state "No suggestions needed."

**Analysis Process for You (the AI):**

1.  **Understand the Rule:** Carefully read and interpret rule content to understand its purpose, requirements, and scope.
2.  **Applicability Check:** Based on rule content and your knowledge of Home Assistant integrations, determine if this specific rule is relevant and applicable to the provided `{integration}` code.
3.  **Code Review (if applicable):** If the rule applies, thoroughly examine the provided integration code.
    *   Look for specific patterns, functions, configurations, or architectural choices mentioned or implied by the rule.
    *   Identify if the integration implements these requirements correctly.
    *   Note any deviations, omissions, or incorrect implementations.
4.  **Determine Status:** Based on your analysis, assign "todo", "done", or "exempt".
5.  **Formulate Report:** Construct the report according to the specified structure, ensuring your reasoning is clear, evidence-based (referencing code), and constructive.

--- START OF ATTACHED FILES ---

--- FILE: rule-{rule}-description.md ---
{rule_content}
--- END FILE ---

{files}

--- END OF ATTACHED FILES ---
""".strip()

IGNORED_RULES = (
    # Has to verify docs repo
    "docs-",
    # Has to verify brands repo
    "brands",
    # Has to verify PyPI
    "dependency-transparency",
    # Has to verify tests
    "config-flow-test-coverage",
    "test-coverage",
)


def get_quality_scale_rules(core_path: Path) -> dict[str, list[str]]:
    """
    Get quality scale rules from the core repository.
    """
    rules_file = core_path / "script" / "hassfest" / "quality_scale.py"
    module = ast.parse(rules_file.read_text(encoding="utf-8"))
    rules = {
        "BRONZE": [],
        "SILVER": [],
        "GOLD": [],
        "PLATINUM": [],
    }
    for node in module.body:
        if not isinstance(node, ast.Assign) or node.targets[0].id != "ALL_RULES":
            continue

        for rule in node.value.elts:
            if not isinstance(rule, ast.Call) or rule.func.id != "Rule":
                continue

            rule_name = rule.args[0].value
            rule_tier = rule.args[1].attr
            rules[rule_tier].append(rule_name)

        break
    return rules


def get_integration_files_for_prompt(integration_path: Path) -> str:
    """
    Get all files for the integration to be used in the prompt.
    """
    name = integration_path.name
    ignored_files = IGNORE_FILES.get(name, set())
    integration_files = []
    priority_extensions = {
        "manifest.json": 1,
        "__init__.py": 2,
        "coordinator.py": 3,
        "api.py": 3,
        "entity.py": 3,
        "application_credentials.py": 3,
        "config_flow.py": 4,
        ".py": 5,
        ".yaml": 8,
        ".json": 10,
    }
    for file_path in sorted(
        integration_path.rglob("*"),
        key=lambda x: (
            # Try by name first
            priority_extensions.get(
                x.name,
                # Then by extension
                priority_extensions.get(x.suffix, 0),
            ),
        ),
    ):
        if (
            "__pycache__" in file_path.parts
            or not file_path.is_file()
            or file_path.name in ignored_files
            or (
                # Exclude non HA system files
                file_path.name not in HA_FILES
                and
                # and non Python files
                file_path.suffix not in (".py",)
            )
        ):
            continue

        integration_files.append(
            f"\n\n--- FILE: homeassistant/components/{name}/{file_path.relative_to(integration_path)} ---\n\n"
        )
        integration_files.append(file_path.read_text(encoding="utf-8"))
        integration_files.append(f"\n--- END FILE ---")

    return "".join(integration_files).strip()


def estimate_tokens(prompt: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(prompt)
    return len(tokens)


def get_args() -> tuple:
    """
    Get command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Check quality scale for an integration."
    )
    parser.add_argument(
        "integration",
        help="The integration domain to check. Optional if --integration-path is provided.",
        type=str,
        nargs="?",
        default=None,
    )
    parser.add_argument(
        "--core-path",
        help="Path to Home Assistant core.",
        type=str,
        default="../core",
    )
    parser.add_argument(
        "--integration-path",
        help="Path to the integration directory. Overrides constructing path from --core-path and integration domain.",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--target-scale",
        help="Quality scale to target.",
        choices=["bronze", "silver", "gold", "platinum"],
    )
    parser.add_argument(
        "--force-update",
        help="Will also update existing reports.",
        action="store_true",
    )
    parser.add_argument(
        "--dry-run",
        help="Do not generate reports.",
        action="store_true",
    )
    parser.add_argument(
        "--free-model",
        help="Use less powered but free model.",
        action="store_true",
    )
    parser.add_argument(
        "--include-done",
        help="Generate reports for rules marked done or exempt.",
        action="store_true",
    )
    parser.add_argument(
        "--single-rule",
        help="Only run the first applicable rule.",
        action="store_true",
    )
    parser.add_argument(
        "--publish",
        help="Commit and push changes in generated/INTEGRATION_NAME directory after generating reports.",
        action="store_true",
    )
    return parser.parse_args()


def main(token: str, args) -> None:
    """
    Main function to run the script.
    """
    core_path = Path(args.core_path).resolve()

    if not args.integration and not args.integration_path:
        print(
            "Error: Either an integration domain or --integration-path must be provided."
        )
        sys.exit(1)

    core_commit_sha = None

    if args.integration_path:
        integration_path = Path(args.integration_path).resolve()
        args.integration = integration_path.name
    elif not core_path.is_dir():
        print(f"Error: Core path {core_path} does not exist.")
        sys.exit(1)
    else:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=core_path,
                capture_output=True,
                text=True,
                check=True,
            )
            core_commit_sha = result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error: Could not get commit SHA from {core_path}: {e}")
            sys.exit(1)

        integration_path = core_path / "homeassistant" / "components" / args.integration

    if not integration_path.is_dir():
        print(f"Error: Integration path {integration_path} does not exist.")
        sys.exit(1)

    rules = get_quality_scale_rules(core_path)

    manifest = json.loads(
        (integration_path / "manifest.json").read_text(encoding="utf-8")
    )
    integration_quality_scale = manifest.get("quality_scale", "unknown").upper()
    if (
        integration_quality_scale not in ("LEGACY", "UNKNOWN")
        and integration_quality_scale not in rules
    ):
        print(
            f"Error: Integration quality scale {integration_quality_scale} is not supported."
        )
        sys.exit(1)

    rules_report = {
        rule: {"status": "todo"} for scale in rules for rule in rules[scale]
    }
    rules_report_path = integration_path / "quality_scale.yaml"
    if rules_report_path.exists():
        with open(rules_report_path, "r", encoding="utf-8") as file:
            rules_report.update(
                {
                    rule: {"status": info} if isinstance(info, str) else info
                    for rule, info in yaml.safe_load(file)["rules"].items()
                }
            )

    output_dir = OUTPUT_DIR / args.integration
    rules_to_check = {}
    printed_something = False
    for quality_scale, rules in rules.items():
        for rule in rules:
            if rule.startswith(IGNORED_RULES):
                continue

            info = rules_report[rule]

            if info["status"] != "todo" and not args.include_done:
                continue

            report_path = output_dir / f"{rule}.md"

            if report_path.exists() and not args.force_update:
                print(f"Report for {rule} already exists. Skipping.")
                printed_something = True
                continue

            rules_to_check[rule] = report_path

        # Stop if we reached the target scale or found some rules to check
        # in the current scale
        if args.target_scale:
            if quality_scale == args.target_scale.upper():
                break
        elif rules_to_check:
            break

    if printed_something:
        print()

    if not rules_to_check:
        print(f"No rules to check for {args.integration}.")
        sys.exit(0)

    print("Generating report for rules:")
    for idx, rule in enumerate(rules_to_check):
        print(f"  {rule}")
        if idx == 0 and args.single_rule:
            print()
            print("Ignoring next rules due to --single-rule flag:")
    print()

    integration_files = get_integration_files_for_prompt(integration_path)

    if args.dry_run:
        prompt = RULE_REVIEW_PROMPT.format(
            integration=args.integration,
            rule=rule,
            rule_url=QUALITY_SCALE_RULE_DOCS_URL.format(rule),
            rule_content=requests.get(QUALITY_SCALE_RULE_RAW_URL.format(rule)).text,
            files=integration_files,
        )
        print("Dry run enabled. Not generating reports.")
        print(f"Prompt token estimate: {estimate_tokens(prompt)}")
        return

    client = genai.Client(api_key=token)
    output_dir.mkdir(parents=True, exist_ok=True)

    model = FREE_MODEL if args.free_model else PAID_MODEL

    total = len(rules_to_check)
    current = 0

    for rule, report_path in rules_to_check.items():
        current += 1
        print(f"Generating report {current}/{total} for {rule}...")
        start_time = time.time()
        report = "bla"
        response = client.models.generate_content(
            model=model,
            contents=RULE_REVIEW_PROMPT.format(
                integration=args.integration,
                rule=rule,
                rule_url=QUALITY_SCALE_RULE_DOCS_URL.format(rule),
                rule_content=requests.get(QUALITY_SCALE_RULE_RAW_URL.format(rule)).text,
                files=integration_files,
            ),
        )

        report = response.text

        footer = [
            "Created at {datetime} using {model}. Prompt tokens: {prompt_tokens}, Output tokens: {output_tokens}, Total tokens: {total_tokens}.".format(
                datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                model=model,
                prompt_tokens=response.usage_metadata.prompt_token_count,
                output_tokens=response.usage_metadata.candidates_token_count,
                total_tokens=response.usage_metadata.total_token_count,
            )
        ]
        if core_commit_sha:
            footer.append(
                "Report based on [`{commit_sha_short}`](https://github.com/home-assistant/core/tree/{commit_sha}).".format(
                    commit_sha=core_commit_sha,
                    commit_sha_short=core_commit_sha[:7],
                )
            )

        footer.append(
            "AI can be wrong. Always verify the report and the code against the rule."
        )
        report += "\n\n---\n\n" + "\n\n".join(f"_{s}_" for s in footer) + "\n"

        duration = time.time() - start_time
        report_path.write_text(report, encoding="utf-8")
        print(
            f"Report generated at {report_path.relative_to(SCRIPT_DIR)} in {duration:.1f}s"
        )
        print(
            "Prompt tokens: {prompt_tokens}, Output tokens: {output_tokens}, Total tokens: {total_tokens}".format(
                prompt_tokens=response.usage_metadata.prompt_token_count,
                output_tokens=response.usage_metadata.candidates_token_count,
                total_tokens=response.usage_metadata.total_token_count,
            )
        )
        print()
        if args.single_rule:
            break

    if not args.publish:
        return

    subprocess.run(
        ["git", "add", str(output_dir)],
        check=True,
        cwd=SCRIPT_DIR,
    )
    subprocess.run(
        ["git", "commit", "-m", f"Update reports for {args.integration}"],
        check=True,
        cwd=SCRIPT_DIR,
    )
    subprocess.run(
        ["git", "push"],
        check=True,
        cwd=SCRIPT_DIR,
    )
    print(f"Successfully published changes for {args.integration}:")
    print(f"https://github.com/balloob/home-assistant-quality-checker/tree/main/generated/{args.integration}")


if __name__ == "__main__":
    token_path = Path(".token")
    if not token_path.exists():
        print("No token file found. Please create a .token file with your API key.")
        sys.exit(1)
    token = token_path.read_text(encoding="utf-8").strip()
    main(token, get_args())

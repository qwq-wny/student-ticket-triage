"""Generate deterministic toy datasets for the ticket triage project.

The data is synthetic and contains no customer information. Keeping the generator in
Git while DVC tracks the generated CSV files makes the small datasets reproducible.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from random import Random

REPO_ROOT = Path(__file__).resolve().parents[2]
LABELS = ("urgent", "high", "normal", "low")

TEMPLATES: dict[str, tuple[str, ...]] = {
    "urgent": (
        "Production is down for every customer",
        "Users cannot sign in after the latest release",
        "Payments are failing across the checkout service",
        "Security alert: possible account takeover",
        "Data loss reported in the production workspace",
    ),
    "high": (
        "API integration returns errors intermittently",
        "Dashboard performance degraded after the update",
        "Invoice amount is incorrect for this account",
        "Webhooks stopped delivering events",
        "Export job fails before completion",
    ),
    "normal": (
        "How do I invite a teammate to the project",
        "Please reset my password",
        "I have a question about the billing plan",
        "Need help configuring SSO metadata",
        "Where can I download the audit log",
    ),
    "low": (
        "Feature request: add dark mode",
        "Documentation typo on the settings page",
        "Feedback about roadmap notification preferences",
        "Suggestion for a new report filter",
        "Question about future API version",
    ),
}

CONTEXT_PREFIXES = (
    "Customer reported:",
    "Support ticket:",
    "After reviewing the account:",
)
CONTEXT_SUFFIXES = (
    "please investigate",
    "this happens in the browser and API",
    "we need an update",
    "thank you",
)


def make_rows(version: str, seed: int) -> list[dict[str, object]]:
    rng = Random(seed)  # noqa: S311 - deterministic dataset generation, not cryptography
    counts = (
        {"urgent": 30, "high": 40, "normal": 55, "low": 25}
        if version == "v1"
        else {"urgent": 60, "high": 60, "normal": 60, "low": 60}
    )
    rows: list[dict[str, object]] = []

    for priority, count in counts.items():
        for index in range(count):
            base_text = TEMPLATES[priority][index % len(TEMPLATES[priority])]
            text = base_text
            if version == "v2":
                text = f"{rng.choice(CONTEXT_PREFIXES)} {text}"
                if index % 3 == 0:
                    text = f"{text}, {rng.choice(CONTEXT_SUFFIXES)}"
                if index % 7 == 0:
                    text = f"{text} (case {1000 + index})"
            elif rng.random() < 0.10:
                # v1 intentionally includes noisy filler that is removed in v2.
                text = f"{text} maybe asap unknown"

            recorded_priority = priority
            if version == "v1" and rng.random() < 0.12:
                # v1 contains realistic annotation noise; v2 corrects and balances these labels.
                recorded_priority = rng.choice([label for label in LABELS if label != priority])

            rows.append(
                {
                    "ticket_id": f"{version}-{index:04d}",
                    "text": text,
                    "customer_tier": rng.choices(
                        ["free", "standard", "premium"], weights=[45, 35, 20]
                    )[0],
                    "monthly_revenue": round(rng.uniform(0, 250_000), 2),
                    "priority": recorded_priority,
                }
            )

    rng.shuffle(rows)
    return rows


def write_dataset(version: str, output: Path, seed: int) -> None:
    rows = make_rows(version, seed)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["ticket_id", "text", "customer_tier", "monthly_revenue", "priority"]
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", choices=["v1", "v2"])
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path. Defaults to data/tickets_<version>.csv.",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    output = args.output or REPO_ROOT / "data" / f"tickets_{args.version}.csv"
    write_dataset(args.version, output, args.seed)


if __name__ == "__main__":
    main()

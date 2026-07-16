"""CLI scaffold for the ServiceNow pipeline plugin."""

from __future__ import annotations

import argparse


def register_cli(subparser: argparse.ArgumentParser) -> None:
    """Register placeholder CLI verbs for the ServiceNow pipeline."""
    subparser.set_defaults(func=servicenow_pipeline_command)


def servicenow_pipeline_command(args: argparse.Namespace) -> int:
    """Handle the placeholder ServiceNow pipeline CLI command."""
    _ = args
    print("ServiceNow pipeline scaffold is installed, but execution is not implemented yet.")
    return 0

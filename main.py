#!/usr/bin/env python3
"""
Main entry point for the Habit Tracker CLI application.

This is a simple wrapper that imports and runs the CLI from the package.
"""

from habit_tracker.cli.commands import cli

if __name__ == '__main__':
    cli()
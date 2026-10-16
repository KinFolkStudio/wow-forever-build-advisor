"""Shared helpers: load the skill's scripts by file path and run them as CLIs."""
import importlib.util
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "wow-forever-build-advisor", "scripts")


def script_path(name):
    return os.path.join(SCRIPTS, name)


def load(name):
    path = script_path(name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(name, *args, cwd=None):
    """Run a script and return (exit code, stdout + stderr)."""
    proc = subprocess.run(
        [sys.executable, script_path(name + ".py"), *args],
        capture_output=True, text=True, cwd=cwd,
    )
    return proc.returncode, proc.stdout + proc.stderr

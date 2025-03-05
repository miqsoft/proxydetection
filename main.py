#!/usr/bin/env python3
import sys
import subprocess
import argparse
from pathlib import Path
from dotenv import load_dotenv

def load_env():
    """Load environment variables from .env file located in the script's directory."""
    script_dir = Path(__file__).resolve().parent
    dotenv_path = script_dir / ".env"

    if dotenv_path.exists():
        load_dotenv(dotenv_path, override=True)
    else:
        print(f"Warning: .env file not found at {dotenv_path}", file=sys.stderr)

def run_ansible_playbook(args):
    """Run ansible-playbook with the provided arguments and stream output."""
    cmd = ["ansible-playbook"] + args

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Stream output in real-time
        for line in process.stdout:
            print(line, end="")

        process.wait()

        # Exit with the same return code as ansible-playbook
        sys.exit(process.returncode)

    except FileNotFoundError:
        print("Error: ansible-playbook command not found. Ensure Ansible is installed.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Python wrapper for running ansible-playbook with environment variables from .env")
    parser.add_argument("playbook_args", nargs=argparse.REMAINDER, help="Arguments to pass to ansible-playbook")

    args = parser.parse_args()

    if not args.playbook_args:
        print("Usage: ansible_wrapper.py <ansible-playbook arguments>", file=sys.stderr)
        sys.exit(1)

    # Load .env variables
    load_env()

    # Run ansible-playbook with passed arguments
    run_ansible_playbook(args.playbook_args)

if __name__ == "__main__":
    main()

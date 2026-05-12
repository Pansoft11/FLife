from __future__ import annotations

import argparse
import json
import sys

from .store import activate, status


def main() -> int:
    parser = argparse.ArgumentParser(description="FLIFE Lite local licensing")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status")
    activate_parser = subparsers.add_parser("activate")
    activate_parser.add_argument("--email", required=True)
    activate_parser.add_argument("--license-key", required=True)

    args = parser.parse_args()
    if args.command == "status":
        print(json.dumps(status()))
    elif args.command == "activate":
        print(json.dumps(activate(args.email, args.license_key)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

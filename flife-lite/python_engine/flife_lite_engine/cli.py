import argparse
import json
import sys

from .api import run_fatigue_analysis


def main() -> int:
    parser = argparse.ArgumentParser(description="FLIFE Lite fatigue engine")
    parser.add_argument("--request-json", help="Analysis request as JSON")
    args = parser.parse_args()

    payload = json.loads(args.request_json or "{}")
    response = run_fatigue_analysis(payload)
    print(response.model_dump_json())
    return 0


if __name__ == "__main__":
    sys.exit(main())

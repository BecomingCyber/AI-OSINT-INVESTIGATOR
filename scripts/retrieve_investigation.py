from pathlib import Path
import sys
import json

# Allow imports from the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.database_manager import get_investigation


if __name__ == "__main__":
    investigation_id = input(
        "Enter investigation ID to retrieve: "
    ).strip()

    if not investigation_id.isdigit():
        print("Investigation ID must be a number.")
        raise SystemExit(1)

    result = get_investigation(int(investigation_id))

    if result is None:
        print(
            f"No investigation found with ID {investigation_id}."
        )
        raise SystemExit(1)

    print("\nINVESTIGATION RETRIEVED")
    print("=" * 60)

    print(f"ID: {result['id']}")
    print(f"Target: {result['target']}")
    print(f"Status: {result['status']}")
    print(f"Created At: {result['created_at']}")

    print("\nCOLLECTED OSINT DATA")
    print("=" * 60)
    print(
        json.dumps(
            result["collected_data"],
            indent=4,
            default=str,
        )
    )

    print("\nAI ANALYSIS")
    print("=" * 60)

    if result["ai_analysis"]:
        print(result["ai_analysis"])
    else:
        print("No AI analysis was saved.")

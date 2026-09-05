from pathlib import Path
import sys
import json

# Allow imports from the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from collectors.dns_collector import collect_dns
from collectors.whois_collector import collect_whois
from collectors.ip_collector import collect_ip_info
from collectors.subdomain_collector import collect_subdomains
from collectors.technology_collector import collect_technology_info

from analyzer.ai_analyzer import analyze_osint

from database.database_manager import (
    initialize_database,
    save_investigation,
)


def investigate(domain):
    """
    Run all OSINT collectors for a target domain.
    """

    results = {
        "target": domain,
        "dns": collect_dns(domain),
        "whois": collect_whois(domain),
        "ip_information": collect_ip_info(domain),
        "subdomains": collect_subdomains(domain),
        "technology": collect_technology_info(domain),
    }

    return results


if __name__ == "__main__":
    # Make sure the database exists and has the required table.
    initialize_database()

    target = input("Enter a domain to investigate: ").strip()

    print(f"\nInvestigating {target}...")
    print("=" * 60)

    # Step 1: Collect OSINT evidence
    osint_results = investigate(target)

    print("\nCOLLECTED OSINT DATA")
    print("=" * 60)
    print(json.dumps(osint_results, indent=4, default=str))

    # Step 2: Analyze the collected evidence
    print("\nAI ANALYSIS")
    print("=" * 60)

    analysis_result = analyze_osint(osint_results)

    if analysis_result["status"] == "success":
        print(f"Status: {analysis_result['status']}")
        print(f"Target: {analysis_result['target']}")

        print("\nINVESTIGATION FINDINGS")
        print("-" * 60)
        print(analysis_result["analysis"])

    else:
        print("Status: error")
        print(analysis_result["error"])

    # Step 3: Save the investigation
    investigation_id = save_investigation(
        target,
        osint_results,
        analysis_result,
    )

    print("\nDATABASE")
    print("=" * 60)
    print(f"Investigation saved successfully.")
    print(f"Investigation ID: {investigation_id}")

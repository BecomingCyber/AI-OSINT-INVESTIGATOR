import dns.resolver


def collect_dns(domain):
    """
    Collect common DNS records for a domain.
    """

    record_types = ["A", "AAAA", "MX", "NS", "TXT"]

    results = {}

    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain, record_type)

            results[record_type] = [
                answer.to_text() for answer in answers
            ]

        except Exception:
            results[record_type] = []

    return results


if __name__ == "__main__":
    target = input("Enter a domain to investigate: ")

    dns_results = collect_dns(target)

    print(f"\nDNS Results for {target}")
    print("-" * 50)

    for record_type, records in dns_results.items():

        print(f"\n{record_type} Records:")

        if records:
            for record in records:
                print(f"  {record}")
        else:
            print("  No records found")

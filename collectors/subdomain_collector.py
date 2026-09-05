import requests


def collect_subdomains(domain):
    """
    Collect passive subdomains from Certificate Transparency logs.

    This function queries crt.sh for certificates associated with the
    supplied domain and extracts valid domain/subdomain names.

    No brute forcing or active scanning is performed.
    """

    domain = domain.strip().lower()

    url = f"https://crt.sh/?q=%25.{domain}&output=json"

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "AI-OSINT-Investigator/1.0"
            },
        )

        response.raise_for_status()

        data = response.json()

        subdomains = set()

        for certificate in data:
            names = certificate.get("name_value", "").splitlines()

            for name in names:
                name = name.strip().lower()

                # Remove wildcard prefix
                if name.startswith("*."):
                    name = name[2:]

                # Only keep the target domain or true subdomains
                if (
                    (name == domain or name.endswith("." + domain))
                    and "@" not in name
                    and " " not in name
                ):
                    subdomains.add(name)

        return sorted(subdomains)

    except requests.RequestException as error:
        return {
            "error": f"Subdomain collection failed: {error}"
        }

    except ValueError:
        return {
            "error": "The certificate transparency service returned invalid data."
        }


if __name__ == "__main__":
    target = input("Enter a domain to investigate: ").strip()

    results = collect_subdomains(target)

    print(f"\nPassive Subdomain Results for {target}")
    print("-" * 50)

    if isinstance(results, dict) and "error" in results:
        print(results["error"])
    else:
        print(f"Found {len(results)} unique subdomain(s):\n")

        for subdomain in results:
            print(f"  {subdomain}")

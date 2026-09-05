import whois


def collect_whois(domain):
    """
    Collect WHOIS information for a domain.
    """

    try:
        data = whois.whois(domain)

        return {
            "domain_name": data.domain_name,
            "registrar": data.registrar,
            "creation_date": str(data.creation_date),
            "expiration_date": str(data.expiration_date),
            "updated_date": str(data.updated_date),
            "name_servers": data.name_servers,
            "status": data.status,
        }

    except Exception as error:
        return {
            "error": str(error)
        }


if __name__ == "__main__":
    target = input("Enter a domain to investigate: ")

    results = collect_whois(target)

    print(f"\nWHOIS Results for {target}")
    print("-" * 50)

    for key, value in results.items():
        print(f"{key}: {value}")

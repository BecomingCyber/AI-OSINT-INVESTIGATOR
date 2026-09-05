import socket
import requests


def collect_ip_info(domain):
    """
    Resolve a domain to an IP address and collect
    basic public IP information.
    """

    try:
        ip_address = socket.gethostbyname(domain)

        response = requests.get(
            f"https://ipinfo.io/{ip_address}/json",
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        return {
            "domain": domain,
            "ip_address": ip_address,
            "hostname": data.get("hostname"),
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "organization": data.get("org"),
            "timezone": data.get("timezone"),
        }

    except socket.gaierror:
        return {
            "error": "Unable to resolve the domain to an IP address."
        }

    except requests.RequestException as error:
        return {
            "error": f"IP information request failed: {error}"
        }


if __name__ == "__main__":
    target = input("Enter a domain to investigate: ")

    results = collect_ip_info(target)

    print(f"\nIP Information for {target}")
    print("-" * 50)

    for key, value in results.items():
        print(f"{key}: {value}")

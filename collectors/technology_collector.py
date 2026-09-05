import requests


def collect_technology_info(domain):
    """
    Collect passive web technology indicators from publicly
    available HTTP response information.

    No vulnerability scanning or exploitation is performed.
    """

    domain = domain.strip().lower()

    results = {
        "url": None,
        "status_code": None,
        "final_url": None,
        "server": None,
        "powered_by": None,
        "content_type": None,
        "security_headers": {},
        "technology_indicators": [],
    }

    headers = {
        "User-Agent": "AI-OSINT-Investigator/1.0"
    }

    # Try HTTPS first, then HTTP if HTTPS fails.
    for scheme in ["https", "http"]:
        url = f"{scheme}://{domain}"

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=10,
                allow_redirects=True,
            )

            results["url"] = url
            results["status_code"] = response.status_code
            results["final_url"] = response.url
            results["server"] = response.headers.get("Server")
            results["powered_by"] = response.headers.get("X-Powered-By")
            results["content_type"] = response.headers.get("Content-Type")

            security_header_names = [
                "Strict-Transport-Security",
                "Content-Security-Policy",
                "X-Content-Type-Options",
                "X-Frame-Options",
                "Referrer-Policy",
                "Permissions-Policy",
            ]

            for header_name in security_header_names:
                results["security_headers"][header_name] = (
                    response.headers.get(header_name)
                )

            # Evidence-based technology indicators
            server = response.headers.get("Server")

            if server:
                results["technology_indicators"].append(
                    f"Server header: {server}"
                )

            powered_by = response.headers.get("X-Powered-By")

            if powered_by:
                results["technology_indicators"].append(
                    f"X-Powered-By header: {powered_by}"
                )

            if "cf-ray" in response.headers:
                results["technology_indicators"].append(
                    "Cloudflare response header detected"
                )

            if "x-amz-cf-id" in response.headers:
                results["technology_indicators"].append(
                    "Amazon CloudFront response header detected"
                )

            if "x-vercel-id" in response.headers:
                results["technology_indicators"].append(
                    "Vercel response header detected"
                )

            return results

        except requests.RequestException:
            continue

    return {
        "error": "Unable to retrieve an HTTP or HTTPS response from the domain."
    }


if __name__ == "__main__":
    target = input("Enter a domain to investigate: ").strip()

    results = collect_technology_info(target)

    print(f"\nTechnology Results for {target}")
    print("-" * 60)

    if "error" in results:
        print(results["error"])

    else:
        print(f"Requested URL: {results['url']}")
        print(f"Status Code: {results['status_code']}")
        print(f"Final URL: {results['final_url']}")
        print(f"Server: {results['server']}")
        print(f"X-Powered-By: {results['powered_by']}")
        print(f"Content-Type: {results['content_type']}")

        print("\nSecurity Headers:")

        for header, value in results["security_headers"].items():
            print(f"  {header}: {value}")

        print("\nTechnology Indicators:")

        if results["technology_indicators"]:
            for indicator in results["technology_indicators"]:
                print(f"  {indicator}")
        else:
            print("  No technology indicators detected")

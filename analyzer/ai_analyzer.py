import json
import os

import bleach
import markdown
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

ALLOWED_ANALYSIS_TAGS = [
    "blockquote",
    "br",
    "code",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "li",
    "ol",
    "p",
    "pre",
    "strong",
    "ul",
]


def render_analysis_markdown(analysis):
    """
    Convert AI-generated Markdown to a sanitized HTML fragment.
    """

    rendered_analysis = markdown.markdown(
        analysis or "",
        extensions=["fenced_code", "sane_lists"],
    )

    return bleach.clean(
        rendered_analysis,
        tags=ALLOWED_ANALYSIS_TAGS,
        attributes={},
        strip=True,
    )


def build_analysis_prompt(osint_data):
    """
    Convert collected OSINT data into a structured prompt
    for AI-assisted analysis.
    """

    formatted_data = json.dumps(
        osint_data,
        indent=4,
        default=str
    )

    prompt = f"""
You are assisting a cybersecurity analyst with an OSINT investigation.

Analyze only the evidence provided below.

Your tasks:

1. Summarize the collected information.
2. Identify notable relationships between the findings.
3. Identify observations that may require further investigation.
4. Identify possible risks only when supported by evidence.
5. Clearly distinguish facts from assumptions.
6. Do not label anything malicious without supporting evidence.
7. Recommend reasonable next investigative steps.

OSINT DATA:

{formatted_data}
"""

    return prompt.strip()


def analyze_osint(osint_data):
    """
    Send collected OSINT data to the OpenAI Responses API
    and return an evidence-grounded analysis.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "error": "OPENAI_API_KEY is missing from the .env file."
        }

    prompt = build_analysis_prompt(osint_data)

    client = OpenAI(api_key=api_key)

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            input=prompt
        )

        return {
            "status": "success",
            "target": osint_data.get("target"),
            "analysis": response.output_text,
            "analysis_html": render_analysis_markdown(
                response.output_text
            ),
        }

    except Exception as error:
        return {
            "status": "error",
            "error": str(error)
        }


if __name__ == "__main__":
    sample_data = {
        "target": "example.com",
        "dns": {
            "A": [
                "104.20.23.154",
                "172.66.147.243"
            ],
            "NS": [
                "elliott.ns.cloudflare.com.",
                "hera.ns.cloudflare.com."
            ]
        },
        "whois": {
            "registrar": "RESERVED-Internet Assigned Numbers Authority"
        },
        "ip_information": {
            "organization": "AS13335 Cloudflare, Inc."
        },
        "subdomains": [
            "dev.example.com",
            "example.com",
            "m.example.com",
            "products.example.com",
            "support.example.com",
            "www.example.com"
        ]
    }

    result = analyze_osint(sample_data)

    print("\nAI Analysis Test")
    print("=" * 60)

    if result["status"] == "success":
        print(f"Status: {result['status']}")
        print(f"Target: {result['target']}")

        print("\nAI Analysis")
        print("-" * 60)
        print(result["analysis"])

    else:
        print("Status: error")
        print(result["error"])

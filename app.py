from flask import (
    Flask,
    render_template,
    request,
    send_file,
)

from collectors.dns_collector import collect_dns
from collectors.whois_collector import collect_whois
from collectors.ip_collector import collect_ip_info
from collectors.subdomain_collector import collect_subdomains
from collectors.technology_collector import collect_technology_info

from analyzer.ai_analyzer import analyze_osint

from database.database_manager import (
    initialize_database,
    save_investigation,
    get_investigation,
    get_all_investigations,
)

from reporting.pdf_report import generate_pdf_report


app = Flask(__name__)

initialize_database()


def collect_osint(domain):
    """
    Run all OSINT collectors for a target domain.
    """

    return {
        "target": domain,
        "dns": collect_dns(domain),
        "whois": collect_whois(domain),
        "ip_information": collect_ip_info(domain),
        "subdomains": collect_subdomains(domain),
        "technology": collect_technology_info(domain),
    }


@app.route("/")
def home():
    """
    Display the AI OSINT Investigator homepage.
    """

    return render_template("index.html")


@app.route("/investigate", methods=["POST"])
def investigate():
    """
    Collect, analyze, save, and display an investigation.
    """

    domain = request.form.get("domain", "").strip().lower()

    if not domain:
        return render_template(
            "index.html",
            error="Please enter a domain."
        )

    osint_results = collect_osint(domain)

    analysis_result = analyze_osint(osint_results)

    investigation_id = save_investigation(
        domain,
        osint_results,
        analysis_result,
    )

    return render_template(
        "results.html",
        investigation_id=investigation_id,
        target=domain,
        osint=osint_results,
        analysis=analysis_result,
    )


@app.route("/history")
def history():
    """
    Display all saved investigations.
    """

    investigations = get_all_investigations()

    return render_template(
        "history.html",
        investigations=investigations,
    )


@app.route("/investigation/<int:investigation_id>")
def view_investigation(investigation_id):
    """
    Display one previously saved investigation.
    """

    investigation = get_investigation(
        investigation_id
    )

    if investigation is None:
        return "Investigation not found.", 404

    analysis_result = {
        "status": investigation["status"],
        "analysis": investigation["ai_analysis"],
    }

    return render_template(
        "results.html",
        investigation_id=investigation["id"],
        target=investigation["target"],
        osint=investigation["collected_data"],
        analysis=analysis_result,
    )


@app.route("/report/<int:investigation_id>")
def generate_report(investigation_id):
    """
    Generate and return a PDF report for a saved investigation.
    """

    investigation = get_investigation(
        investigation_id
    )

    if investigation is None:
        return "Investigation not found.", 404

    pdf_path = generate_pdf_report(
        investigation
    )

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=pdf_path.name,
    )


if __name__ == "__main__":
    app.run(debug=True)

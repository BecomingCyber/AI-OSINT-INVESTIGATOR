import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def safe_text(value):
    """
    Convert values to safe text for ReportLab paragraphs.
    """
    if value is None:
        return "Not available"

    return escape(str(value))


def add_list(story, items, style):
    """
    Add a Python list to the PDF as bullet points.
    """
    if not items:
        story.append(Paragraph("No data collected.", style))
        return

    for item in items:
        story.append(
            Paragraph(
                f"• {safe_text(item)}",
                style,
            )
        )


def generate_pdf_report(investigation):
    """
    Generate a PDF report from a saved investigation.

    Expected investigation fields:
        id
        target
        collected_data
        ai_analysis
        status
        created_at
    """

    investigation_id = investigation["id"]
    target = investigation["target"]

    safe_target = (
        target.replace(".", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )

    output_path = (
        REPORTS_DIR
        / f"investigation_{investigation_id}_{safe_target}.pdf"
    )

    collected_data = investigation.get("collected_data", {})

    if isinstance(collected_data, str):
        collected_data = json.loads(collected_data)

    ai_analysis = investigation.get(
        "ai_analysis",
        "No AI analysis available.",
    )

    status = investigation.get("status", "Unknown")
    created_at = investigation.get("created_at", "Unknown")

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=f"AI OSINT Investigation Report - {target}",
        author="AI OSINT Investigator",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
        spaceAfter=24,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        spaceAfter=6,
    )

    analysis_style = ParagraphStyle(
        "AnalysisBody",
        parent=body_style,
        fontName="Courier",
        fontSize=8.5,
        leading=12,
    )

    story = []

    # --------------------------------------------------
    # REPORT HEADER
    # --------------------------------------------------

    story.append(
        Paragraph(
            "AI OSINT Investigation Report",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Evidence-first, AI-assisted open-source intelligence analysis",
            subtitle_style,
        )
    )

    summary_data = [
        ["Investigation ID", safe_text(investigation_id)],
        ["Target", safe_text(target)],
        ["Status", safe_text(status)],
        ["Created", safe_text(created_at)],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[1.6 * inch, 5.1 * inch],
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#0B1F3A"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (0, -1),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CCCCCC"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(summary_table)
    story.append(Spacer(1, 18))

    # --------------------------------------------------
    # DNS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "1. DNS Evidence",
            heading_style,
        )
    )

    dns_data = collected_data.get("dns", {})

    if dns_data:
        for record_type, records in dns_data.items():
            story.append(
                Paragraph(
                    f"<b>{safe_text(record_type)} Records</b>",
                    body_style,
                )
            )

            add_list(
                story,
                records,
                body_style,
            )
    else:
        story.append(
            Paragraph(
                "No DNS evidence collected.",
                body_style,
            )
        )

    # --------------------------------------------------
    # WHOIS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "2. WHOIS Evidence",
            heading_style,
        )
    )

    whois_data = collected_data.get("whois", {})

    if whois_data:
        for key, value in whois_data.items():

            if isinstance(value, list):
                formatted_value = ", ".join(
                    str(item) for item in value
                )
            else:
                formatted_value = value

            story.append(
                Paragraph(
                    f"<b>{safe_text(key.replace('_', ' ').title())}:</b> "
                    f"{safe_text(formatted_value)}",
                    body_style,
                )
            )
    else:
        story.append(
            Paragraph(
                "No WHOIS evidence collected.",
                body_style,
            )
        )

    # --------------------------------------------------
    # IP INFORMATION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "3. IP Information",
            heading_style,
        )
    )

    ip_data = collected_data.get("ip_information", {})

    if ip_data:
        for key, value in ip_data.items():
            story.append(
                Paragraph(
                    f"<b>{safe_text(key.replace('_', ' ').title())}:</b> "
                    f"{safe_text(value)}",
                    body_style,
                )
            )
    else:
        story.append(
            Paragraph(
                "No IP information collected.",
                body_style,
            )
        )

    # --------------------------------------------------
    # SUBDOMAINS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "4. Discovered Subdomains",
            heading_style,
        )
    )

    add_list(
        story,
        collected_data.get("subdomains", []),
        body_style,
    )

    # --------------------------------------------------
    # TECHNOLOGY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "5. Web Technology Evidence",
            heading_style,
        )
    )

    technology = collected_data.get("technology", {})

    if technology:
        for key, value in technology.items():

            if isinstance(value, dict):

                story.append(
                    Paragraph(
                        f"<b>{safe_text(key.replace('_', ' ').title())}</b>",
                        body_style,
                    )
                )

                for nested_key, nested_value in value.items():
                    story.append(
                        Paragraph(
                            f"&nbsp;&nbsp;"
                            f"<b>{safe_text(nested_key)}:</b> "
                            f"{safe_text(nested_value)}",
                            body_style,
                        )
                    )

            elif isinstance(value, list):

                story.append(
                    Paragraph(
                        f"<b>{safe_text(key.replace('_', ' ').title())}</b>",
                        body_style,
                    )
                )

                add_list(
                    story,
                    value,
                    body_style,
                )

            else:

                story.append(
                    Paragraph(
                        f"<b>{safe_text(key.replace('_', ' ').title())}:</b> "
                        f"{safe_text(value)}",
                        body_style,
                    )
                )
    else:
        story.append(
            Paragraph(
                "No web technology evidence collected.",
                body_style,
            )
        )

    # --------------------------------------------------
    # AI ANALYSIS
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "6. AI-Assisted Analysis",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "The following analysis was generated from the collected "
            "OSINT evidence and should be validated by a human analyst.",
            body_style,
        )
    )

    for line in str(ai_analysis).splitlines():

        stripped = line.strip()

        if not stripped:
            story.append(Spacer(1, 5))
            continue

        # Remove basic Markdown heading characters
        cleaned = stripped.lstrip("#").strip()

        story.append(
            Paragraph(
                safe_text(cleaned),
                analysis_style,
            )
        )

    # --------------------------------------------------
    # VALIDATION NOTICE
    # --------------------------------------------------

    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            "7. Analyst Validation Notice",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "This report combines publicly available OSINT evidence "
            "with AI-assisted analysis. AI-generated observations are "
            "not independent proof of malicious activity, compromise, "
            "ownership, attribution, or vulnerability. Findings should "
            "be corroborated with authoritative sources and reviewed "
            "by a human analyst before investigative conclusions are made.",
            body_style,
        )
    )

    doc.build(story)

    return output_path


if __name__ == "__main__":
    print(
        "PDF report generator loaded successfully."
    )

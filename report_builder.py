import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER


def build_purple_report(red_data: dict, blue_data: dict, output_path: str) -> str:
    """
    Builds a professional PDF purple team report combining red and blue team findings.
    """

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Title'],
        fontSize=22, textColor=colors.HexColor('#1a1a2e'), spaceAfter=6)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
        fontSize=11, textColor=colors.HexColor('#666666'), spaceAfter=20)
    h1_style = ParagraphStyle('H1', parent=styles['Heading1'],
        fontSize=14, textColor=colors.HexColor('#1a1a2e'),
        spaceBefore=16, spaceAfter=8,
        borderPad=4, backColor=colors.HexColor('#f0f4ff'),
        leftIndent=8)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
        fontSize=11, textColor=colors.HexColor('#2d3748'), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor('#333333'), spaceAfter=6, leading=14)
    code_style = ParagraphStyle('Code', parent=styles['Code'],
        fontSize=8, backColor=colors.HexColor('#f7f7f7'),
        textColor=colors.HexColor('#c7254e'), leftIndent=12, spaceAfter=8)
    label_style = ParagraphStyle('Label', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#666666'), spaceAfter=2)

    story = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    score = blue_data.get('detection_coverage', {}).get('score', 0)

    # Header
    story.append(Paragraph("Purple Team Assessment Report", title_style))
    story.append(Paragraph(
        f"Technique: {red_data.get('technique_id')} — {red_data.get('technique_name')} | "
        f"Generated: {now} | Classification: CONFIDENTIAL", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#4a6cf7')))
    story.append(Spacer(1, 12))

    # Executive Summary Table
    story.append(Paragraph("Executive Summary", h1_style))

    score_color = colors.HexColor('#22c55e') if score >= 80 else \
                  colors.HexColor('#f59e0b') if score >= 60 else \
                  colors.HexColor('#ef4444')

    summary_data = [
        ['Technique ID', red_data.get('technique_id', 'N/A'),
         'Detection Score', f"{score}/100"],
        ['Tactic', red_data.get('tactic', 'N/A'),
         'Coverage Rating', blue_data.get('detection_coverage', {}).get('rating', 'N/A')],
        ['Severity', red_data.get('severity', 'N/A'),
         'False Positive Rate', blue_data.get('false_positive_rate', 'N/A')],
        ['Stealth Level', red_data.get('stealth_level', 'N/A'),
         'Detection Gaps', str(len(blue_data.get('detection_gaps', [])))],
    ]

    summary_table = Table(summary_data, colWidths=[1.3*inch, 2.2*inch, 1.4*inch, 2.0*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eef2ff')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#eef2ff')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#6366f1')),
        ('TEXTCOLOR', (3, 0), (3, 0), score_color),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # Attack Description
    story.append(Paragraph("Attack Description", h2_style))
    story.append(Paragraph(red_data.get('attack_description', ''), body_style))
    story.append(Paragraph(
        f"<b>Real-world Usage:</b> {red_data.get('real_world_examples', 'N/A')}", body_style))
    story.append(Spacer(1, 8))

    # RED TEAM SECTION
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ef4444')))
    story.append(Paragraph("🔴 Red Team — Attack Simulation", h1_style))

    # Simulation Commands
    story.append(Paragraph("Simulation Commands", h2_style))
    for i, cmd in enumerate(red_data.get('simulation_commands', []), 1):
        story.append(Paragraph(
            f"<b>Command {i} ({cmd.get('platform')} / {cmd.get('shell')})</b> — {cmd.get('description')}",
            body_style))
        story.append(Paragraph(cmd.get('command', ''), code_style))
        if cmd.get('cleanup'):
            story.append(Paragraph(f"<i>Cleanup: {cmd.get('cleanup')}</i>", label_style))

    # Expected Log Evidence
    story.append(Paragraph("Expected Log Evidence", h2_style))
    evidence_data = [['Log Source', 'Event ID', 'Field', 'Expected Value', 'Significance']]
    for ev in red_data.get('expected_log_evidence', []):
        evidence_data.append([
            ev.get('log_source', ''), ev.get('event_id', ''),
            ev.get('field', ''), ev.get('value', ''), ev.get('significance', '')
        ])

    evidence_table = Table(evidence_data,
        colWidths=[1.2*inch, 0.7*inch, 1.0*inch, 1.5*inch, 2.5*inch])
    evidence_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5f5')]),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(evidence_table)
    story.append(Spacer(1, 12))

    # BLUE TEAM SECTION
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3b82f6')))
    story.append(Paragraph("🔵 Blue Team — Detection Engineering", h1_style))

    # Detection Coverage
    story.append(Paragraph("Detection Coverage", h2_style))
    story.append(Paragraph(
        f"<b>Score: {score}/100 — {blue_data.get('detection_coverage', {}).get('rating', 'N/A')}</b>",
        body_style))
    story.append(Paragraph(
        blue_data.get('detection_coverage', {}).get('explanation', ''), body_style))

    # Detection Gaps
    story.append(Paragraph("Detection Gaps", h2_style))
    gaps_data = [['Gap', 'Risk', 'Recommendation']]
    for gap in blue_data.get('detection_gaps', []):
        gaps_data.append([
            gap.get('gap', ''), gap.get('risk', ''), gap.get('recommendation', '')
        ])

    gaps_table = Table(gaps_data, colWidths=[2.3*inch, 0.8*inch, 3.8*inch])
    gaps_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eff6ff')]),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(gaps_table)
    story.append(Spacer(1, 8))

    # Detection Rules
    story.append(Paragraph("Detection Rules", h2_style))
    for rule_name, rule_key in [("Sigma", "sigma"), ("Splunk SPL", "splunk_spl"),
                                  ("KQL (Microsoft Sentinel)", "kql"), ("Wazuh XML", "wazuh_xml")]:
        story.append(Paragraph(f"<b>{rule_name}</b>", body_style))
        rule_content = blue_data.get(rule_key, 'Not generated')
        # Truncate very long rules for PDF readability
        if len(rule_content) > 800:
            rule_content = rule_content[:800] + "\n... [truncated — see full rule in web UI]"
        story.append(Paragraph(rule_content.replace('\n', '<br/>'), code_style))

    # Mitigations
    story.append(Paragraph("MITRE ATT&CK Mitigations", h2_style))
    for mit in blue_data.get('mitigations', []):
        story.append(Paragraph(
            f"<b>{mit.get('mitre_mitigation_id')} — {mit.get('mitigation_name')}</b>: "
            f"{mit.get('description')}",
            body_style))

    # Footer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#d1d5db')))
    story.append(Paragraph(
        f"Generated by AI Purple Team Platform | {now} | CONFIDENTIAL",
        ParagraphStyle('Footer', parent=styles['Normal'],
            fontSize=8, textColor=colors.HexColor('#9ca3af'), alignment=TA_CENTER)))

    doc.build(story)
    return output_path
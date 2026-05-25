import anthropic
import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_blue_team(technique_id: str, technique_name: str, red_team_data: dict) -> dict:
    log_evidence = json.dumps(red_team_data.get("expected_log_evidence", []), indent=2)
    commands = json.dumps(red_team_data.get("simulation_commands", []), indent=2)

    prompt = f"""You are a senior detection engineer. Generate detection rules for the following MITRE ATT&CK technique.

Technique ID: {technique_id}
Technique Name: {technique_name}
Tactic: {red_team_data.get('tactic', '')}

Attack Commands Used:
{commands}

Expected Log Evidence:
{log_evidence}

Return ONLY a valid JSON object. For the sigma, splunk_spl, kql, and wazuh_xml fields, return them as plain single-line strings with no line breaks. Use spaces instead of newlines in the rule content.

{{
  "detection_coverage": {{
    "score": 85,
    "rating": "Good | Moderate | Poor | Excellent",
    "explanation": "Why this coverage score was assigned"
  }},
  "detection_gaps": [
    {{
      "gap": "What this detection misses",
      "risk": "High | Medium | Low",
      "recommendation": "How to close this gap"
    }}
  ],
  "sigma": "title: X | status: production | logsource: category: process_creation product: windows | detection: selection: Image: x condition: selection | level: high",
  "splunk_spl": "index=windows sourcetype=WinEventLog EventCode=4688 | where Image like ...",
  "kql": "SecurityEvent | where EventID == 4688 | where ...",
  "wazuh_xml": "<group name=x><rule id=100500 level=12><description>X</description></rule></group>",
  "false_positive_rate": "High | Medium | Low",
  "false_positive_notes": "What legitimate activity might trigger this",
  "hunt_queries": [
    {{
      "platform": "Splunk | KQL | Sigma",
      "query": "Single line query here",
      "description": "What this hunt looks for"
    }}
  ],
  "mitigations": [
    {{
      "mitre_mitigation_id": "M1XXX",
      "mitigation_name": "Name",
      "description": "How this mitigation prevents the attack"
    }}
  ]
}}

CRITICAL: The entire response must be valid JSON. No raw newlines inside any string value. No unescaped quotes inside strings. Keep all rule content on a single line."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    # Character-level fix for newlines inside strings
    def fix_json_strings(s):
        result = []
        in_string = False
        escape = False
        for char in s:
            if escape:
                result.append(char)
                escape = False
            elif char == '\\':
                result.append(char)
                escape = True
            elif char == '"':
                in_string = not in_string
                result.append(char)
            elif in_string and char in '\n\r':
                result.append(' ')
            else:
                result.append(char)
        return ''.join(result)

    raw = fix_json_strings(raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find('{')
        end = raw.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(fix_json_strings(raw[start:end]))
        raise
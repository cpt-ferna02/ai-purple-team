import anthropic
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_red_team(technique_id: str, technique_name: str, description: str) -> dict:
    prompt = f"""You are a senior red team operator. Generate a detailed attack simulation for the following MITRE ATT&CK technique.

Technique ID: {technique_id}
Technique Name: {technique_name}
Description: {description}

Return ONLY a valid JSON object with this exact structure (no markdown, no text outside JSON):

{{
  "technique_id": "{technique_id}",
  "technique_name": "{technique_name}",
  "tactic": "The MITRE tactic this technique belongs to",
  "attack_description": "2-3 sentence description of how this attack works in the real world",
  "prerequisites": ["prerequisite 1", "prerequisite 2"],
  "simulation_commands": [
    {{
      "platform": "Windows | Linux | macOS",
      "shell": "PowerShell | CMD | Bash",
      "command": "The actual command to simulate this technique",
      "description": "What this command does",
      "cleanup": "Command to clean up after simulation"
    }}
  ],
  "expected_log_evidence": [
    {{
      "log_source": "Windows Security | Sysmon | Linux Auditd | etc",
      "event_id": "Event ID number",
      "field": "Field name to look for",
      "value": "Expected value in that field",
      "significance": "Why this log entry matters"
    }}
  ],
  "attack_tools": ["tool1", "tool2"],
  "iocs": ["IOC1", "IOC2"],
  "severity": "Critical | High | Medium | Low",
  "stealth_level": "High | Medium | Low",
  "real_world_examples": "Brief mention of real APT groups or malware that use this technique"
}}

Be technically precise. Use real commands that actually work. Include at least 3 simulation commands and 4 expected log evidence entries.
IMPORTANT: Return only valid JSON. Escape all backslashes as \\\\ and double quotes inside strings as \\". Do not use raw newlines inside string values."""

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

    # Remove newlines inside JSON string values
    import re
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
            elif in_string and char == '\n':
                result.append('\\n')
            elif in_string and char == '\r':
                result.append('\\r')
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
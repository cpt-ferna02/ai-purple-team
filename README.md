# ⚔️ AI Purple Team Automation Platform

> Enter a MITRE ATT&CK technique — get attack simulation commands, detection rules, coverage scoring, and a full exportable PDF report.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask)
![Anthropic](https://img.shields.io/badge/Claude-API-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📸 Screenshots

### Full Platform — Red/Blue Split View
![Platform Overview](screenshots/platform-overview.png)

### Detection Rules (Sigma / Splunk SPL / KQL / Wazuh)
![Detection Rules](screenshots/detection-rules.png)

### Exported PDF Report
![PDF Report](screenshots/pdf-report.png)

### Live GitHub Repository
![GitHub Repo](screenshots/github-repo.png)

> 📄 **[Download Sample PDF Report](exports/sample-purple-report.pdf)**

---

## 📌 What It Does

This platform automates purple team exercises by simultaneously generating:

| Side | Output |
|------|--------|
| 🔴 **Red Team** | Attack simulation commands with expected log evidence |
| 🔵 **Blue Team** | Detection rules in Sigma, Splunk SPL, KQL, and Wazuh XML |
| 🟣 **Purple Report** | Detection coverage score, gap analysis, hunt queries, and exportable PDF |

---

## 🗂️ Project Structure

```
ai-purple-team/
├── app.py                ← Flask backend (routes: /, /analyze, /export-pdf)
├── red_team.py           ← Attack simulation generator (Claude API)
├── blue_team.py          ← Detection rule generator (Claude API)
├── report_builder.py     ← PDF report builder (ReportLab)
├── templates/
│   └── index.html        ← Web UI (vanilla JS, tabbed detection rules)
├── static/
│   ├── style.css         ← Dark-themed styling
│   └── heatmap.js        ← MITRE ATT&CK heatmap renderer
├── screenshots/          ← Demo screenshots for README
├── exports/              ← Generated PDF reports (git-ignored)
├── .env                  ← API key (git-ignored)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/cpt-ferna02/ai-purple-team.git
cd ai-purple-team
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install flask anthropic python-dotenv reportlab
```

### 4. Add your API key

Create a `.env` file in the root folder:

```
ANTHROPIC_API_KEY=your_api_key_here
```

Get your key at [console.anthropic.com](https://console.anthropic.com).

### 5. Run the app

```bash
python app.py
```

Open your browser at **http://127.0.0.1:5000**

---

## 🧪 Usage

1. Enter a **MITRE ATT&CK Technique ID** (e.g. `T1059.001`) and **Technique Name** (e.g. `PowerShell`)
2. Optionally add context (e.g. *"attacker using encoded PowerShell to download a remote payload"*)
3. Click **⚔️ Run Purple Team Analysis**
4. Review the red/blue split view, detection gaps, and rules across all four platforms
5. Click **📄 Export PDF Report** to download a full assessment report

### Quick-select examples

| Technique ID | Name |
|---|---|
| T1059.001 | PowerShell |
| T1003.001 | LSASS Memory |
| T1053.005 | Scheduled Task |
| T1078 | Valid Accounts |
| T1566.001 | Spearphishing Attachment |

---

## 🔧 Tech Stack

- **Backend:** Python 3.10+, Flask
- **AI:** Anthropic Claude API (`claude-opus-4-5`)
- **PDF Generation:** ReportLab
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Config:** python-dotenv

---

## 📄 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/` | Web UI |
| `POST` | `/analyze` | Runs red + blue team generation, returns JSON |
| `POST` | `/export-pdf` | Generates and downloads PDF report |

---

## 🧠 Challenges & How I Solved Them

These are real problems I ran into building and shipping this project. Each one taught me something I couldn't have learned just by reading documentation.

---

### 🔴 Challenge 1 — Virtual Environment Not Active

**What happened:** After creating all the project files and running `python app.py`, the app crashed immediately:

```
ModuleNotFoundError: No module named 'anthropic'
```

I had already run `pip install flask anthropic python-dotenv reportlab`, so I didn't understand why the module wasn't found.

**Root cause:** I had opened a new terminal window, which launched without the virtual environment active. All the packages I installed were inside the `venv/` folder — not the system Python — so they were invisible to any terminal that hadn't activated the venv first.

**How I solved it:**
```bash
venv\Scripts\activate
python app.py
```

The `(venv)` prefix in the terminal prompt is the indicator the environment is active. No `(venv)` = packages won't be found.

**What I learned:** Every time you open a new terminal, you must reactivate the virtual environment before running the app. This is one of the most common Python pitfalls and easy to miss.

---

### 🟡 Challenge 2 — JSON Parsing Failures from Claude API Responses (4 iterations)

This was the biggest technical challenge of the project and took multiple debugging cycles to fully resolve.

**What happened:** The app would start, the analysis would run, but then crash with a `json.JSONDecodeError`. The blue team generator was returning malformed JSON from the Claude API.

**Iteration 1 — Unterminated string:**
```
json.JSONDecodeError: Unterminated string starting at: line 44 column 16
```
Claude was returning a response where a special character inside a string value was terminating the JSON string early. I added a fallback parser that tried to extract the JSON object by finding the outermost `{` and `}` characters.

**Iteration 2 — Raw newlines inside strings:**
The error changed position but the same type — Claude was putting literal newline characters inside JSON string values (like inside a multi-line Sigma rule), which is invalid JSON. I added a regex to strip them:
```python
raw = re.sub(r'(?<!\\)\n(?!["\s*\}\]\{])', ' ', raw)
```
This helped but wasn't complete — the regex missed some edge cases.

**Iteration 3 — Unescaped quotes breaking the delimiter:**
```
json.JSONDecodeError: Expecting ',' delimiter: line 32 column 6
```
The detection rules (Sigma YAML, KQL, Wazuh XML) contain double quotes and backslashes in their syntax. Claude was including these literally inside JSON strings instead of escaping them, which broke the parser entirely.

I wrote a character-level state machine parser that walked through the raw response character by character, tracking whether each character was inside a JSON string or not, and replacing any raw newlines it found with `\n`:

```python
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
```

**Iteration 4 — Prompt engineering the root cause:**
Rather than only fixing the parser, I also updated the prompt itself to instruct Claude to return all detection rules as single-line escaped strings. Fixing both the output format and the parser made the solution robust.

**What I learned:** When an LLM returns structured data, you cannot assume the output will be perfectly formatted even when you ask for JSON. The right approach is to sanitize the response defensively before parsing, and also engineer the prompt to minimize the problem at the source. State machines are more reliable than regex for parsing nested structured text.

---

### 🔴 Challenge 3 — Accidentally Committed API Key to GitHub

**What happened:** On the first push to GitHub, the entire push was blocked:

```
remote: - GITHUB PUSH PROTECTION
remote:   Push cannot contain secrets
remote:   —— Anthropic API Key ————————————————
remote:     path: .env:1
```

My `.env` file had been committed to the repository and was visible in the git history.

**What I tried first:** I deleted the `.env` file and pushed again — still blocked. Removing a file from the working directory doesn't remove it from git history. GitHub scans every past commit, not just the current state.

**How I solved it:** Wiped the entire git history by deleting the `.git` folder and reinitializing from scratch. I also immediately rotated the exposed API key since it was already visible.

```powershell
Remove-Item -Recurse -Force .git
git init
```

Then verified `.env` was absent from `git status` before committing anything.

**What I learned:** Secret exposure is permanent in git history unless you rewrite it. The `.gitignore` must be created and committed before any `git add .` is ever run. Rotating the compromised key is mandatory — deleting the file is not enough on its own.

---

### 🟡 Challenge 4 — `.gitignore` Not Taking Effect

**What happened:** After reinitializing git, running `git status` still showed `.env` as an untracked file ready to be staged, even though `.gitignore` existed.

**Root cause:** The `.gitignore` file had been created but was either empty or hadn't been saved correctly. In one case it existed as a 0-byte file.

**How I solved it:** Recreated it explicitly in PowerShell with the correct contents:

```powershell
New-Item -Name ".gitignore" -ItemType File -Force
Set-Content .gitignore ".env`nvenv/`n__pycache__/`n*.pyc`nexports/"
```

Then confirmed with `git status` that `.env` was no longer listed before proceeding.

**What I learned:** Always run `git status` and visually verify the file list before every `git add .`. A `.gitignore` that looks correct may not be saving properly depending on the editor or how it was created.

---

### 🟡 Challenge 5 — PowerShell vs CMD Syntax

**What happened:** Following standard instructions to delete the `.git` folder:

```
Remove-Item: A positional parameter cannot be found that accepts argument '/q'.
```

**Root cause:** VS Code was running PowerShell, not Command Prompt. The `rmdir /s /q` syntax is CMD-only and doesn't work in PowerShell.

**How I solved it:** Used the PowerShell equivalent:

```powershell
# CMD only — doesn't work in PowerShell
rmdir /s /q .git

# PowerShell equivalent
Remove-Item -Recurse -Force .git
```

**What I learned:** Windows has two separate terminal environments with different command syntax. Tutorials often assume CMD. When a command fails unexpectedly in PowerShell, the first thing to check is whether it's a CMD-style command that needs a PowerShell equivalent.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: anthropic` | Run `venv\Scripts\activate` first, then retry |
| `ModuleNotFoundError: reportlab` | Run `pip install reportlab` |
| PDF export is blank | Ensure the `exports/` folder exists |
| API key error | Check your `.env` file is saved and formatted correctly |
| Layout looks broken | Use a full browser window — responsive at 900px+ |
| Analysis is slow | Normal — red team and blue team API calls run sequentially |

---

## 🔒 Security Notes

- Never commit your `.env` file — it is listed in `.gitignore`
- The `exports/` folder is also git-ignored to avoid leaking generated reports
- This tool is intended for **authorized security testing and research only**

---

## 📜 License

MIT License — free to use, modify, and distribute with attribution.

---

*Built with Python, Flask, and the Anthropic Claude API.*

import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
WATSONX_URL = os.getenv("WATSONX_URL")
IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"


def get_iam_token():
    """Exchange the IBM Cloud API key for a short-lived IAM bearer token."""
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": WATSONX_API_KEY,
    }
    response = requests.post(IAM_TOKEN_URL, headers=headers, data=data, timeout=30)
    response.raise_for_status()
    return response.json()["access_token"]


def build_blueprint_prompt(idea: str) -> str:
    """
    Construct a detailed RAG-style business consultant prompt that instructs
    the model to return a structured startup blueprint.
    """
    return f"""You are an expert startup consultant, business strategist, and venture advisor with 20+ years of experience helping founders across technology, SaaS, fintech, healthtech, edtech, and consumer industries.

A founder has described the following startup idea:

\"\"\"{idea}\"\"\"

Using your deep expertise and knowledge of startup ecosystems, produce a comprehensive, actionable Startup Blueprint. Structure your response exactly as follows:

---

## 🚀 Startup Blueprint

### 1. Executive Summary
Provide a concise 3–4 sentence overview of the startup concept, its value proposition, and market opportunity.

### 2. Business Model Canvas
- **Customer Segments:** Who are the primary and secondary target customers?
- **Value Propositions:** What unique value does this startup deliver?
- **Channels:** How will the product/service reach customers?
- **Customer Relationships:** How will the startup acquire, retain, and grow customers?
- **Revenue Streams:** List 3–5 monetization models with estimated pricing strategy.
- **Key Resources:** Critical assets required (technology, talent, IP, data).
- **Key Activities:** Core operations to deliver the value proposition.
- **Key Partnerships:** Strategic alliances, vendors, or platform partnerships.
- **Cost Structure:** Major cost drivers (fixed vs. variable).

### 3. Market Research & Opportunity
- **Total Addressable Market (TAM):** Estimated market size with reasoning.
- **Target Market Segment:** Specific niche to focus on first.
- **Market Trends:** 3–5 relevant industry trends supporting this idea.
- **Customer Pain Points:** Primary problems being solved.

### 4. Competitor Analysis
Identify 3–5 real or hypothetical competitors. For each, list:
- Name / Type
- Strengths
- Weaknesses
- Differentiation opportunity for this startup

### 5. Go-To-Market Strategy
- **Phase 1 – Launch (0–3 months):** Key activities, channels, and targets.
- **Phase 2 – Growth (3–12 months):** Scaling tactics and partnerships.
- **Phase 3 – Expansion (12–24 months):** Geographic or product expansion plans.
- **Key Marketing Channels:** SEO, content, social, paid, partnerships, etc.

### 6. Revenue Model & Financial Projections
- Pricing strategy with specific numbers.
- Estimated Month 1, Month 6, and Year 1 revenue targets.
- Break-even analysis (approximate timeline).

### 7. Estimated Budget Breakdown
| Category | Estimated Cost (USD) |
|---|---|
| Product Development | $ |
| Marketing & Sales | $ |
| Operations & Legal | $ |
| Team & HR | $ |
| Contingency (10%) | $ |
| **Total Seed Budget** | **$** |

### 8. Funding Options & Government Schemes
- Best-fit funding stages (Bootstrapping → Pre-Seed → Seed → Series A).
- 3–5 relevant government grants, incubators, or accelerators (e.g., Y Combinator, Techstars, SBIR, Startup India, EU Horizon).
- Suggested investor profiles (angels, micro-VCs, corporate VCs).

### 9. Legal & Compliance Requirements
- Recommended business entity type (LLC, C-Corp, etc.) and why.
- Key licenses, permits, or certifications needed.
- IP protection strategy (patents, trademarks, copyrights).
- Data privacy and regulatory considerations.

### 10. Team & Talent Plan
- Critical founding team roles and skills needed.
- First 5 hires with justification.
- Advisory board recommendations.

### 11. Key Risks & Mitigation Strategies
List the top 5 risks with a mitigation plan for each.

### 12. 90-Day Action Plan
Provide a week-by-week or milestone-based action plan for the first 90 days.

---

Be specific, data-driven, and actionable. Avoid generic advice. Tailor every section to the specific startup idea provided above.
"""


def query_watsonx(prompt: str) -> str:
    """Send the prompt to IBM watsonx and return the generated text."""
    token = get_iam_token()
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {
        "model_id": "ibm/granite-4-h-small",
        "project_id": WATSONX_PROJECT_ID,
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 3000,
            "min_new_tokens": 200,
            "repetition_penalty": 1.1,
            "stop_sequences": [],
        },
    }
    response = requests.post(WATSONX_URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    result = response.json()
    generated = result.get("results", [{}])[0].get("generated_text", "")
    if not generated.strip():
        raise ValueError("watsonx returned an empty response.")
    return generated.strip()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    idea = (data.get("idea") or "").strip()
    if not idea:
        return jsonify({"error": "Please describe your startup idea."}), 400
    if len(idea) < 10:
        return jsonify({"error": "Please provide more detail about your idea."}), 400
    if len(idea) > 2000:
        return jsonify({"error": "Description too long. Please keep it under 2000 characters."}), 400

    try:
        prompt = build_blueprint_prompt(idea)
        blueprint = query_watsonx(prompt)
        return jsonify({"blueprint": blueprint})
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else 0
        if status == 401:
            return jsonify({"error": "Authentication failed. Check your IBM API key."}), 502
        elif status == 429:
            return jsonify({"error": "Rate limit reached. Please try again in a moment."}), 502
        else:
            return jsonify({"error": f"watsonx API error ({status}). Please try again."}), 502
    except requests.exceptions.Timeout:
        return jsonify({"error": "The request timed out. watsonx may be busy — please retry."}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Cannot reach IBM watsonx. Check your internet connection."}), 503
    except ValueError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)

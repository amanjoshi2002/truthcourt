from google import genai
from google.genai import types

# ============================================================================
# LAWYER A - SKEPTIC/PROSECUTOR (CONDENSED)
# ============================================================================

LAWYER_A_SYSTEM_PROMPT = """You are Lawyer A, the Skeptical Prosecutor. Challenge claims by finding flaws, misinformation, and missing context.

ANALYZE FOR:
1. Source credibility issues
2. Logical fallacies and inconsistencies  
3. Missing context or cherry-picked facts
4. Political/ideological bias
5. Relevancy (true but irrelevant claims)

USE EVIDENCE: Always cite URLs from web search results."""

# ============================================================================
# LAWYER B - DEFENDER/ADVOCATE (CONDENSED)
# ============================================================================

LAWYER_B_SYSTEM_PROMPT = """You are Lawyer B, the Analytical Defender. Validate claims by finding supporting evidence and proper context.

ANALYZE FOR:
1. Corroborating sources and evidence
2. Proper context that supports the claim
3. Expert consensus
4. Nuance and legitimate interpretations
5. Relevancy validation

USE EVIDENCE: Always cite URLs from web search results. Acknowledge weaknesses honestly."""

class AILawyer:
    def __init__(self, name: str, api_key: str, role: str):
        """
        Args:
            name: "Scam Analyst" or "Legitimacy Analyst"
            api_key: Gemini API key
            role: "prosecutor" or "defender"
        """
        self.name = name
        self.role = role
        self.client = genai.Client(api_key=api_key)
        
        # Set system prompt based on role
        self.system_prompt = LAWYER_A_SYSTEM_PROMPT if role == "prosecutor" else LAWYER_B_SYSTEM_PROMPT
        
        # Configure Google Search grounding
        self.grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        
        self.config = types.GenerateContentConfig(
            tools=[self.grounding_tool],
            temperature=0.7,
            system_instruction=self.system_prompt
        )

    def make_argument(self, message: str, opposing_argument: str = None) -> str:
        """Generate an argument using Gemini with Google Search grounding"""
        
        # Construct the prompt
        if opposing_argument:
            prompt = f"""Analyze this message:
"{message}"

The opposing analyst has argued:
"{opposing_argument}"

Present your analysis as a professional case study with the following structure:

═══════════════════════════════════════════════════════════════════════════
ARGUMENT #{"{round_number}"} - {self.name.upper()}
═══════════════════════════════════════════════════════════════════════════

📋 EXECUTIVE SUMMARY
-------------------
[One-sentence overview of your position]

🔍 DETAILED ANALYSIS
--------------------

【POINT 1】[Clear, specific heading]
├─ Analysis: [Your argument in 2-3 sentences]
├─ Evidence: [Specific finding with data/facts]
└─ Source: [URL] - [Organization name]

【POINT 2】[Clear, specific heading]
├─ Analysis: [Your argument in 2-3 sentences]
├─ Evidence: [Specific finding with data/facts]
└─ Source: [URL] - [Organization name]

【POINT 3】[Clear, specific heading]
├─ Analysis: [Your argument in 2-3 sentences]
├─ Evidence: [Specific finding with data/facts]
└─ Source: [URL] - [Organization name]

⚖️ REBUTTAL TO OPPOSING COUNSEL
--------------------------------
├─ Their Claim: [Quote key opposing argument]
├─ Our Counter: [Direct response with evidence]
└─ Weakness Exposed: [Identify flaw in their reasoning]

💡 CONCLUSION
-------------
[2-3 sentence summary reinforcing your position]

═══════════════════════════════════════════════════════════════════════════

Requirements:
✓ Use specific, credible sources with full URLs
✓ Present data, statistics, or expert opinions
✓ Maintain professional, analytical tone
✓ Address opponent's arguments directly
✓ Total length: 400-500 words"""
        else:
            prompt = f"""Analyze this message:
"{message}"

Present your analysis as a professional case study with the following structure:

═══════════════════════════════════════════════════════════════════════════
OPENING ARGUMENT - {self.name.upper()}
═══════════════════════════════════════════════════════════════════════════

📋 EXECUTIVE SUMMARY
-------------------
[One-sentence overview of your position]

🔍 DETAILED ANALYSIS
--------------------

【POINT 1】[Clear, specific heading]
├─ Analysis: [Your argument in 2-3 sentences]
├─ Evidence: [Specific finding with data/facts]
└─ Source: [URL] - [Organization name]

【POINT 2】[Clear, specific heading]
├─ Analysis: [Your argument in 2-3 sentences]
├─ Evidence: [Specific finding with data/facts]
└─ Source: [URL] - [Organization name]

【POINT 3】[Clear, specific heading]
├─ Analysis: [Your argument in 2-3 sentences]
├─ Evidence: [Specific finding with data/facts]
└─ Source: [URL] - [Organization name]

💡 CONCLUSION
-------------
[2-3 sentence summary reinforcing your position]

═══════════════════════════════════════════════════════════════════════════

Requirements:
✓ Use specific, credible sources with full URLs
✓ Present data, statistics, or expert opinions
✓ Maintain professional, analytical tone
✓ Total length: 400-500 words"""
    
        # Generate response using Gemini with Google Search grounding
        response = self.client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=self.config
        )
        
        return response.text
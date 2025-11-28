from typing import List, Dict
import google.generativeai as genai
from utils.web_search import perform_web_search

class AILawyer:
    def __init__(self, name: str, model: genai.GenerativeModel, role_description: str):
        self.name = name
        self.model = model
        self.role_description = role_description
        self.stance = role_description
        self.evidence = []  # Initialize evidence list
        
    def gather_evidence(self, topic: str) -> List[Dict]:
        """Gather evidence through web search"""
        search_query = f"{topic} {self.stance} fraud scam indicators evidence"
        results = perform_web_search(search_query, num_results=3)
        self.evidence.extend(results)
        return results

    def make_argument(self, message: str, opposing_argument: str = None) -> str:
        """Generate an argument using Gemini and gathered evidence from web search"""
        # Gather new evidence from web search
        new_evidence = self.gather_evidence(message)
        
        # Format evidence for the prompt
        evidence_text = ""
        if new_evidence:
            evidence_text = "Web Search Evidence:\n"
            for i, ev in enumerate(new_evidence, 1):
                evidence_text += f"{i}. {ev['title']}\n   {ev['snippet']}\n   Source: {ev['link']}\n\n"
        else:
            evidence_text = "No web evidence available.\n\n"
        
        # Construct the prompt
        if opposing_argument:
            prompt = f"""
You are {self.name}, {self.role_description}.

Analyze this message objectively:
"{message}"

{evidence_text}

The opposing analyst has argued:
"{opposing_argument}"

Provide your professional analysis in this format:
1. Key Point 1
   - Supporting Evidence: (cite web search results or known patterns)
   - Counter to Opponent: (address opponent's claims with data)

2. Key Point 2
   - Supporting Evidence: (cite web search results or known patterns)
   - Counter to Opponent: (address opponent's claims with data)

3. Key Point 3
   - Supporting Evidence: (cite web search results or known patterns)
   - Counter to Opponent: (address opponent's claims with data)

Requirements:
- Make exactly 3 clear points
- Use the web search evidence provided above
- Cite sources with URLs when referencing evidence
- Address opponent's specific claims
- Keep it focused (300-400 words)
"""
        else:
            prompt = f"""
You are {self.name}, {self.role_description}.

Analyze this message objectively:
"{message}"

{evidence_text}

Provide your professional analysis in this format:
1. Key Point 1
   - Supporting Evidence: (cite web search results or known patterns)

2. Key Point 2
   - Supporting Evidence: (cite web search results or known patterns)

3. Key Point 3
   - Supporting Evidence: (cite web search results or known patterns)

Requirements:
- Make exactly 3 clear points
- Use the web search evidence provided above
- Cite sources with URLs when referencing evidence
- Keep it focused (300-400 words)
"""
    
        # Generate response using Gemini
        response = self.model.generate_content(prompt)
        return response.text
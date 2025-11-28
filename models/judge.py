import json
import time
import os
import google.generativeai as genai
from typing import Dict, Tuple
from .rag_store import RAGStore
import logging

# Configure logging
logger = logging.getLogger(__name__)

class Judge:
    def __init__(self, model: genai.GenerativeModel):
        self.model = model
        self.debate_history = []
        self.rag_store = RAGStore()
        logger.info("Judge initialized with new RAGStore")
        
        # Create logs directory if it doesn't exist
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "debate_logs")
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
            logger.info(f"Created debate logs directory at {self.logs_dir}")
        
    def record_argument(self, speaker: str, argument: str):
        """Record each argument for final analysis"""
        self.debate_history.append({
            "speaker": speaker,
            "argument": argument
        })
        logger.info(f"Recorded argument from {speaker}")
    
    def check_similar_case(self, topic: str) -> Tuple[bool, dict]:
        """Check if there's a similar case and return verdict if found"""
        if not isinstance(topic, str):
            logger.info(f"Invalid topic type provided: {type(topic)}")
            return False, {}
            
        if not topic.strip():
            logger.info("Empty topic provided")
            return False, {}
            
        logger.info(f"Checking for similar cases for topic: {topic[:100]}...")
        similar_cases = self.rag_store.find_similar_cases(topic)
        
        if similar_cases:
            best_match = similar_cases[0]
            similarity = best_match['similarity']
            logger.info(f"Best match similarity score: {similarity:.2f}")
            
            # Increased threshold to 0.90 (90%) for more accurate matches
            if similarity > 0.90:  # Higher threshold for more accurate matching
                logger.info(f"Found highly similar case with similarity: {similarity:.2f}")
                # Return the exact same verdict as the previous case
                return True, best_match['verdict']
                
        logger.info("No highly similar cases found")
        return False, {}
    
    def direct_verdict(self, topic: str) -> dict:
        """Provide verdict directly based on topic without debate"""
        logger.info(f"Providing direct verdict for topic: {topic[:100]}...")
        
        prompt = f"""
        Analyze this message objectively to determine if it's a scam or legitimate:
        "{topic}"
        
        Consider these scam indicators:
        - Urgent language or pressure tactics
        - Requests for personal/financial information
        - Suspicious email domains or contact methods
        - Too-good-to-be-true offers
        - Poor grammar/spelling
        - Generic greetings
        
        Consider these legitimacy indicators:
        - Professional company domain
        - Realistic job requirements and salary
        - Proper contact information
        - Clear application process
        - No requests for money or personal details
        
        Provide exactly:
        1. Verdict: SCAM or LEGITIMATE
        2. One sentence summary explaining why
        3. Single most important evidence point
        Keep it extremely concise.
        """
        
        response = self.model.generate_content(prompt)
        
        # Parse the response into structured format
        lines = [line.strip() for line in response.text.split('\n') if line.strip()]
        verdict_data = {
            'verdict': 'SCAM' if 'scam' in lines[0].lower() else 'NOT A SCAM',
            'summary': lines[1] if len(lines) > 1 else 'Analysis unavailable',
            'evidence': [lines[2]] if len(lines) > 2 else ['No specific evidence provided']
        }
        
        # Save direct verdict to log file
        self._save_direct_verdict_log(topic, verdict_data)
        
        # Store the case
        case = {
            'topic': topic,
            'verdict': verdict_data,
            'key_evidence': verdict_data['evidence'][0],  # Ensure key_evidence is set
            'timestamp': time.time()
        }
        self.rag_store.add_case(case)
        
        return verdict_data
    
    def analyze_debate(self, topic: str) -> dict:
        """Analyze the debate and provide a structured verdict"""
        logger.info(f"Analyzing debate for topic: {topic[:100]}...")
        debate_text = json.dumps(self.debate_history, indent=2)
        
        prompt = f"""
        Based on the debate about this message:
        "{topic}"
        
        Debate history:
        {debate_text}
        
        Provide exactly:
        1. Verdict: SCAM or LEGITIMATE
        2. One sentence summary explaining why
        3. Single most important evidence point
        Keep it extremely concise.
        """
        
        response = self.model.generate_content(prompt)
        
        # Parse the response into structured format
        lines = [line.strip() for line in response.text.split('\n') if line.strip()]
        verdict_data = {
            'verdict': 'SCAM' if 'scam' in lines[0].lower() else 'LEGITIMATE',
            'summary': lines[1] if len(lines) > 1 else 'Analysis unavailable',
            'evidence': [lines[2]] if len(lines) > 2 else ['No specific evidence provided'],
            'arguments': self.debate_history.copy(),
            'judge_statement': response.text
        }
        
        # Save debate log to file
        self._save_debate_log(topic, verdict_data)
        
        # Store the case
        self._store_case(topic, verdict_data)
        
        return verdict_data
    
    def _store_case(self, topic: str, verdict: dict):
        """Store the case in RAG store"""
        case = {
            'topic': topic,
            'verdict': verdict,
            'key_evidence': json.dumps(self.debate_history),
            'timestamp': time.time()
        }
        self.rag_store.add_case(case)
        logger.info("Case stored in RAGStore")
    
    def _format_cached_response(self, case: Dict) -> str:
        """Format cached response"""
        formatted_response = f"""[CACHED RESPONSE - Similarity: {case['similarity']:.2f}]

{case['verdict']}

Note: This response is based on a similar previous case. The analysis and recommendations should be applicable to your situation.
Reference case timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(case['timestamp']))}"""
        logger.info("Formatted cached response")
        return formatted_response
        
    def _save_debate_log(self, topic: str, verdict_data: dict):
        """Save the debate to a text file for review"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        # Create a safe filename from the first few words of the topic
        safe_topic = "".join(c if c.isalnum() else "_" for c in topic[:30])
        filename = f"{timestamp}_{safe_topic}.txt"
        filepath = os.path.join(self.logs_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"DEBATE LOG - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"TOPIC:\n{topic}\n\n")
            f.write(f"{'='*80}\n\n")
            f.write("DEBATE:\n")
            
            for entry in self.debate_history:
                f.write(f"\n{entry['speaker']}:\n")
                f.write(f"{entry['argument']}\n")
                f.write(f"{'-'*80}\n")
            
            f.write(f"\n{'='*80}\n\n")
            f.write("VERDICT:\n")
            f.write(f"Verdict: {verdict_data['verdict']}\n")
            f.write(f"Summary: {verdict_data['summary']}\n")
            f.write(f"Evidence: {', '.join(verdict_data['evidence'])}\n")
        
        logger.info(f"Debate log saved to {filepath}")
        return filepath
        
    def _save_direct_verdict_log(self, topic: str, verdict_data: dict):
        """Save direct verdict to a text file for review"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        # Create a safe filename from the first few words of the topic
        safe_topic = "".join(c if c.isalnum() else "_" for c in topic[:30])
        filename = f"{timestamp}_{safe_topic}_direct.txt"
        filepath = os.path.join(self.logs_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"DIRECT VERDICT LOG - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"TOPIC:\n{topic}\n\n")
            f.write(f"{'='*80}\n\n")
            f.write("VERDICT:\n")
            f.write(f"Verdict: {verdict_data['verdict']}\n")
            f.write(f"Summary: {verdict_data['summary']}\n")
            f.write(f"Evidence: {', '.join(verdict_data['evidence'])}\n")
        
        logger.info(f"Direct verdict log saved to {filepath}")
        return filepath
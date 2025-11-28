from flask import Flask, request, jsonify
from flask_cors import CORS  # Add this import
from config import GEMINI_KEY_1, GEMINI_KEY_2, ROUNDS
from utils.gemini_setup import setup_gemini
from models.ai_lawyer import AILawyer
from models.judge import Judge
from models.debate_db import DebateDB
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes



limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
# Initialize database
db = DebateDB()

# Modify the analyze_message function to force a debate for testing purposes

def analyze_message(message: str):
    """Analyze a custom message for potential scams"""
    # Ensure message is a string
    if isinstance(message, dict):
        message = message.get('text', '')  # assuming the message is in 'text' field
    
    # Setup judge
    judge = Judge(setup_gemini(GEMINI_KEY_1))
    
    # First check if we have a similar case
    has_similar, cached_verdict = judge.check_similar_case(message)
    if has_similar:
        return {
            "message": message,
            "verdict": cached_verdict['verdict'],
            "summary": cached_verdict['summary'],
            "evidence": cached_verdict['evidence'],
            "source": "cached"
        }
    
    # COMMENT OUT THIS SECTION TO FORCE DEBATE FOR TESTING
    # if isinstance(message, str) and len(message.split()) < 50:  # Simple case threshold
    #     verdict_data = judge.direct_verdict(message)
    #     return {
    #         "message": message,
    #         "verdict": verdict_data['verdict'],
    #         "summary": verdict_data['summary'],
    #         "evidence": verdict_data['evidence'],
    #         "source": "direct"
    #     }
    
    # For complex cases, proceed with full debate
    prosecutor = AILawyer(
        "Scam Analyst",
        setup_gemini(GEMINI_KEY_1),
        "analyzing potential scam indicators in this message using established fraud detection criteria"
    )
    
    defender = AILawyer(
        "Legitimacy Analyst",
        setup_gemini(GEMINI_KEY_2),
        "analyzing indicators that suggest this message is legitimate using authentic communication patterns"
    )
    
    # Multi-round debate for message analysis
    previous_defender_arg = None
    
    for round_num in range(1, ROUNDS + 1):
        print(f"\n=== Round {round_num}/{ROUNDS} ===")
        
        # Prosecutor makes argument (considering defender's previous argument)
        prosecutor_argument = prosecutor.make_argument(message, previous_defender_arg)
        print(f"Prosecutor Argument: {prosecutor_argument}")
        judge.record_argument(prosecutor.name, f"Round {round_num}: {prosecutor_argument}")
        print(f"{prosecutor.name}: Argument presented")
        
        # Defender responds to prosecutor's argument
        defender_argument = defender.make_argument(message, prosecutor_argument)
        print(f"Defender Argument: {defender_argument}")
        judge.record_argument(defender.name, f"Round {round_num}: {defender_argument}")
        print(f"{defender.name}: Counter-argument presented")
        
        # Store defender's argument for next round
        previous_defender_arg = defender_argument
    
    print(f"\n=== Debate Complete: {ROUNDS} rounds finished ===")
    verdict_data = judge.analyze_debate(message)
    
    # Save to database
    debate_id = db.save_debate(
        message=message,
        verdict=verdict_data['verdict'],
        summary=verdict_data['summary'],
        evidence=verdict_data['evidence'],
        arguments=verdict_data['arguments'],
        judge_statement=verdict_data['judge_statement'],
        source="debate"
    )
    
    return {
        "debate_id": debate_id,
        "message": message,
        "verdict": verdict_data['verdict'],
        "summary": verdict_data['summary'],
        "evidence": verdict_data['evidence'],
        "arguments": verdict_data['arguments'],
        "judge_statement": verdict_data['judge_statement'],
        "source": "debate"
    }

@app.route('/testanalyze', methods=['POST'])
def testanalyze_endpoint():
    """API endpoint to analyze messages"""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if 'message' not in data:
        return jsonify({"error": "Message field is required"}), 400
    
    # Extract the actual message text from the request
    message = data['message']
    if isinstance(message, dict):
        if 'text' not in message:
            return jsonify({"error": "Message must contain 'text' field"}), 400
        message = message['text']
    
    result = analyze_message(message)
    return jsonify(result)



@app.route('/analyze', methods=['POST'])
@limiter.limit("2 per day")  # Max 2 requests per day per IP
def analyze_endpoint():
    """API endpoint to analyze messages"""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if 'message' not in data:
        return jsonify({"error": "Message field is required"}), 400
    
    # Extract the actual message text from the request
    message = data['message']
    if isinstance(message, dict):
        if 'text' not in message:
            return jsonify({"error": "Message must contain 'text' field"}), 400
        message = message['text']
    
    result = analyze_message(message)
    return jsonify(result)


@app.route('/debates', methods=['GET'])
def get_debates():
    """Get all debates with optional limit"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        debates = db.get_all_debates(limit=limit)
        return jsonify({
            "success": True,
            "count": len(debates),
            "debates": debates
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/debates/<int:debate_id>', methods=['GET'])
def get_debate(debate_id):
    """Get a specific debate by ID"""
    try:
        debate = db.get_debate(debate_id)
        if debate:
            return jsonify({
                "success": True,
                "debate": debate
            })
        else:
            return jsonify({"error": "Debate not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Modify the main block to work with both direct Python and Gunicorn
if __name__ == "__main__":
    # Test API connection first
    try:
        test_model = setup_gemini(GEMINI_KEY_1)
        test_response = test_model.generate_content("Test connection")
        print("API connection successful!")
    except Exception as e:
        print(f"API connection failed: {e}")
        exit(1)
        
    # Run the app (will only run when directly executed, not with Gunicorn)
    app.run(host='0.0.0.0', debug=True, port=5000)
import time
from config import GEMINI_KEY_1, GEMINI_KEY_2
from utils.gemini_setup import setup_gemini
from models.ai_lawyer import AILawyer
from models.judge import Judge

def start_debate(topic: str):
    """Initialize and run a debate on the given topic"""
    # Setup the participants
    prosecutor = AILawyer(
        "Prosecutor Thompson",
        setup_gemini(GEMINI_KEY_1),
        f"arguing that {topic} is a serious threat to public safety"
    )
    
    defender = AILawyer(
        "Defender Rodriguez",
        setup_gemini(GEMINI_KEY_2),
        f"arguing for a balanced perspective on {topic}"
    )
    
    judge = Judge(setup_gemini(GEMINI_KEY_1))

    # Number of debate rounds
    rounds = 3

    print("\n=== AI Legal Debate ===")
    print(f"Topic: {topic}")
    print("=" * 50)

    last_argument = None
    for round_num in range(rounds):
        print(f"\nRound {round_num + 1}")
        print("-" * 20)

        # Prosecutor's turn
        print(f"\n{prosecutor.name}:")
        prosecutor_argument = prosecutor.make_argument(topic, last_argument)
        print(prosecutor_argument)
        judge.record_argument(prosecutor.name, prosecutor_argument)
        last_argument = prosecutor_argument
        
        time.sleep(2)

        # Defender's turn
        print(f"\n{defender.name}:")
        defender_argument = defender.make_argument(topic, last_argument)
        print(defender_argument)
        judge.record_argument(defender.name, defender_argument)
        last_argument = defender_argument
        
        time.sleep(2)
    
    # Judge's final verdict
    print("\n=== Judge's Verdict ===")
    print("=" * 50)
    verdict = judge.analyze_debate(topic)
    print(verdict)

if __name__ == "__main__":
    # Example topics - can be changed to any online scam topic
    scam_topics = [
        "Romance scams on dating websites",
        "Job offer email scams",
        "Fake online shopping websites",
        "Tech support scam calls",
        "Investment fraud schemes",
        "Phishing emails impersonating banks"
    ]
    
    # Let user choose a topic
    print("Available scam topics for debate:")
    for i, topic in enumerate(scam_topics, 1):
        print(f"{i}. {topic}")
    
    try:
        choice = int(input("\nChoose a topic number (or 0 to enter your own): "))
        if choice == 0:
            custom_topic = input("Enter your own scam topic: ")
            start_debate(custom_topic)
        else:
            start_debate(scam_topics[choice - 1])
    except (ValueError, IndexError):
        print("Invalid choice. Starting debate with default topic.")
        start_debate(scam_topics[0])
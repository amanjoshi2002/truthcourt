import sqlite3
import json
import time
import os
from typing import Dict, List

class DebateDB:
    def __init__(self):
        """Initialize database connection"""
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "debates.db")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """Create necessary database tables"""
        cursor = self.conn.cursor()
        
        # Main debates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS debates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                verdict TEXT NOT NULL,
                summary TEXT,
                evidence TEXT,
                judge_statement TEXT,
                source TEXT,
                timestamp REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Arguments table (stores all round arguments)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arguments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debate_id INTEGER NOT NULL,
                round_number INTEGER NOT NULL,
                speaker TEXT NOT NULL,
                argument TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debate_id) REFERENCES debates (id)
            )
        ''')
        
        self.conn.commit()
    
    def save_debate(self, message: str, verdict: str, summary: str, evidence: List[str], 
                   arguments: List[Dict], judge_statement: str, source: str = "debate") -> int:
        """Save a complete debate to the database"""
        cursor = self.conn.cursor()
        
        # Insert debate record
        cursor.execute('''
            INSERT INTO debates (message, verdict, summary, evidence, judge_statement, source, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (message, verdict, summary, json.dumps(evidence), judge_statement, source, time.time()))
        
        debate_id = cursor.lastrowid
        
        # Insert all arguments
        for arg in arguments:
            # Extract round number from speaker field if it has "Round X:" prefix
            round_number = arg.get('round', 0)
            speaker = arg.get('speaker', '')
            argument_text = arg.get('argument', '')
            
            # Try to extract round number from argument text if it starts with "Round X:"
            if argument_text.startswith("Round "):
                try:
                    parts = argument_text.split(":", 1)
                    round_str = parts[0].replace("Round ", "").strip()
                    round_number = int(round_str)
                    argument_text = parts[1].strip() if len(parts) > 1 else argument_text
                except Exception:
                    pass
            
            cursor.execute('''
                INSERT INTO arguments (debate_id, round_number, speaker, argument)
                VALUES (?, ?, ?, ?)
            ''', (debate_id, round_number, speaker, argument_text))
        
        self.conn.commit()
        return debate_id
    
    def get_debate(self, debate_id: int) -> Dict:
        """Retrieve a debate by ID"""
        cursor = self.conn.cursor()
        
        # Get debate info
        cursor.execute('SELECT * FROM debates WHERE id = ?', (debate_id,))
        debate_row = cursor.fetchone()
        
        if not debate_row:
            return None
        
        # Get all arguments for this debate
        cursor.execute('''
            SELECT round_number, speaker, argument 
            FROM arguments 
            WHERE debate_id = ? 
            ORDER BY id
        ''', (debate_id,))
        arguments = cursor.fetchall()
        
        return {
            'id': debate_row[0],
            'message': debate_row[1],
            'verdict': debate_row[2],
            'summary': debate_row[3],
            'evidence': json.loads(debate_row[4]),
            'judge_statement': debate_row[5],
            'source': debate_row[6],
            'timestamp': debate_row[7],
            'arguments': [
                {'round': arg[0], 'speaker': arg[1], 'argument': arg[2]} 
                for arg in arguments
            ]
        }
    
    def get_all_debates(self, limit: int = 100) -> List[Dict]:
        """Retrieve all debates"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM debates ORDER BY timestamp DESC LIMIT ?', (limit,))
        debate_ids = [row[0] for row in cursor.fetchall()]
        
        return [self.get_debate(debate_id) for debate_id in debate_ids]
    
    def close(self):
        """Close database connection"""
        self.conn.close()

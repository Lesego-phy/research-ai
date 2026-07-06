import re
from typing import Optional, Tuple
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Initialize Presidio for PII detection
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# INPUT GUARDRAILS

def validate_input(topic: str) -> Tuple[bool, Optional[str]]:
    """
    Validates user input before it reaches the agents.
    Returns (is_valid, error_message)
    """
    # Check 1: Length validation
    if len(topic.strip()) < 5:
        return False, "Topic must be at least 5 characters long."
    
    if len(topic) > 500:
        return False, "Topic must be less than 500 characters."
    
    # Check 2: Prompt injection detection
    injection_patterns = [
        r"ignore previous instructions",
        r"you are now",
        r"system prompt",
        r"forget everything",
        r"act as if",
        r"new role",
    ]
    
    topic_lower = topic.lower()
    for pattern in injection_patterns:
        if re.search(pattern, topic_lower):
            return False, "Invalid input detected. Please rephrase your topic."
    
    # Check 3: PII detection (optional - you might want to allow names)
    # results = analyzer.analyze(text=topic, entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS"], language='en')
    # if results:
    #     return False, "Please remove personal information from your topic."
    
    return True, None

# OUTPUT GUARDRAILS

def validate_output(report: str, sources: list) -> Tuple[bool, Optional[str]]:
    """
    Validates the final report before it's shown to the user.
    Returns (is_valid, error_message)
    """
    # Check 1: Minimum length
    if len(report) < 500:
        return False, "Report is too short. Minimum 500 characters required."
    
    # Check 2: Must have sources
    if not sources or len(sources) < 2:
        return False, "Report must cite at least 2 sources."
    
    # Check 3: PII detection and anonymization
    results = analyzer.analyze(
        text=report, 
        entities=["PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD", "US_SSN"],
        language='en'
    )
    
    if results:
        # Anonymize PII instead of rejecting
        anonymized = anonymizer.anonymize(text=report, analyzer_results=results)
        # You could return the anonymized version, or reject
        # For now, let's just warn
        return False, "Report contains personal information. Please review."
    
    # Check 4: Basic quality checks
    if "I don't know" in report or "I cannot" in report:
        return False, "Report contains uncertainty markers. Please revise."
    
    return True, None

# TOOL GUARDRAILS (Rate Limiting)

class ToolRateLimiter:
    """Prevents agents from calling tools too many times."""
    
    def __init__(self, max_calls: int = 10):
        self.max_calls = max_calls
        self.call_count = 0
    
    def can_call(self) -> bool:
        if self.call_count >= self.max_calls:
            return False
        self.call_count += 1
        return True
    
    def reset(self):
        self.call_count = 0

# Global rate limiter instance
search_rate_limiter = ToolRateLimiter(max_calls=10)
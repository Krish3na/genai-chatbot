"""
Intent classification for routing user queries appropriately
"""
import re
from typing import Dict, Any, Tuple
from enum import Enum

class IntentType(Enum):
    """Enumeration of possible intent types"""
    GENERAL = "general"
    TECHNICAL = "technical"
    HELP = "help"
    KNOWLEDGE = "knowledge"
    SYSTEM = "system"

class IntentClassifier:
    """Classify user intent based on message content and patterns"""
    
    def __init__(self):
        """Initialize the intent classifier with patterns"""
        self.patterns = {
            IntentType.TECHNICAL: [
                r'\b(api|endpoint|server|deployment|docker|kubernetes|jenkins|mlflow|prometheus|grafana)\b',
                r'\b(openai|gpt|langchain|chromadb|vector|embedding)\b',
                r'\b(fastapi|uvicorn|poetry|requirements|dependencies)\b',
                r'\b(architecture|system|infrastructure|monitoring|logging)\b',
                r'\b(production|development|staging|environment)\b'
            ],
            IntentType.HELP: [
                r'\b(help|support|assist|guide|tutorial|how to|what is)\b',
                r'\b(problem|issue|error|bug|fix|troubleshoot)\b',
                r'\b(can you help|need help|stuck|confused)\b'
            ],
            IntentType.KNOWLEDGE: [
                r'\b(features|capabilities|what can|abilities|functions)\b',
                r'\b(rag|retrieval|document|knowledge|information)\b',
                r'\b(chatbot|ai|assistant|intelligence)\b',
                r'\b(explain|describe|tell me about|what are)\b'
            ],
            IntentType.SYSTEM: [
                r'\b(status|health|uptime|performance|metrics)\b',
                r'\b(stats|statistics|monitoring|logs)\b',
                r'\b(version|update|upgrade|maintenance)\b',
                r'\b(server|service|application|system)\b'
            ]
        }
        
        # Compile patterns for efficiency
        self.compiled_patterns = {}
        for intent, patterns in self.patterns.items():
            self.compiled_patterns[intent] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def classify_intent(self, message: str) -> Tuple[IntentType, float]:
        """
        Classify the intent of a user message
        
        Args:
            message: User's message
            
        Returns:
            Tuple of (intent_type, confidence_score)
        """
        message_lower = message.lower()
        
        # Calculate scores for each intent
        scores = {}
        
        for intent, patterns in self.compiled_patterns.items():
            score = 0
            for pattern in patterns:
                matches = pattern.findall(message_lower)
                score += len(matches) * 0.3  # Weight for each match
            
            if score > 0:
                scores[intent] = score
        
        # If no specific intent found, return general
        if not scores:
            return IntentType.GENERAL, 0.5
        
        # Find the highest scoring intent
        best_intent = max(scores.items(), key=lambda x: x[1])
        
        # Normalize confidence score (0.5 to 1.0)
        confidence = min(0.5 + (best_intent[1] * 0.5), 1.0)
        
        return best_intent[0], confidence
    
    def get_intent_metadata(self, intent: IntentType) -> Dict[str, Any]:
        """
        Get metadata for an intent type
        
        Args:
            intent: The classified intent
            
        Returns:
            Dictionary with intent metadata
        """
        metadata = {
            IntentType.GENERAL: {
                "description": "General conversation and casual chat",
                "use_rag": False,
                "response_style": "conversational"
            },
            IntentType.TECHNICAL: {
                "description": "Technical questions about system architecture and implementation",
                "use_rag": True,
                "response_style": "technical"
            },
            IntentType.HELP: {
                "description": "Help and support requests",
                "use_rag": True,
                "response_style": "helpful"
            },
            IntentType.KNOWLEDGE: {
                "description": "Questions about features and capabilities",
                "use_rag": True,
                "response_style": "informative"
            },
            IntentType.SYSTEM: {
                "description": "System status and health queries",
                "use_rag": False,
                "response_style": "system"
            }
        }
        
        return metadata.get(intent, metadata[IntentType.GENERAL])
    
    def should_use_rag(self, intent: IntentType) -> bool:
        """
        Determine if RAG should be used for this intent
        
        Args:
            intent: The classified intent
            
        Returns:
            True if RAG should be used
        """
        metadata = self.get_intent_metadata(intent)
        return metadata.get("use_rag", False) 
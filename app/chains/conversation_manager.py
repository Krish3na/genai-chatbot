"""
Conversation manager for handling multiple user sessions with RAG and Intent Classification
"""
from typing import Dict, Any, Optional
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
import asyncio
import time

from app.chains.chat_chain import ChatChain
from app.retriever.rag_chain import RAGChain
from app.intents.intent_classifier import IntentClassifier, IntentType

class ConversationManager:
    """Manages conversations for multiple users with RAG and Intent Classification"""
    
    def __init__(self):
        """Initialize the conversation manager"""
        self.conversations: Dict[str, ChatChain] = {}
        self.rag_chain = RAGChain()
        self.intent_classifier = IntentClassifier()
        self.user_metadata: Dict[str, Dict[str, Any]] = {}
    
    def get_or_create_conversation(self, user_id: str) -> ChatChain:
        """Get existing conversation or create new one for user"""
        if user_id not in self.conversations:
            self.conversations[user_id] = ChatChain()
            self.user_metadata[user_id] = {
                "created_at": time.time(),
                "message_count": 0,
                "last_activity": time.time()
            }
        
        # Update last activity
        self.user_metadata[user_id]["last_activity"] = time.time()
        return self.conversations[user_id]
    
    async def process_message(self, message: str, user_id: str, use_rag: Optional[bool] = None) -> Dict[str, Any]:
        """
        Process a message for a specific user with automatic intent classification
        
        Args:
            message: User's message
            user_id: User identifier
            use_rag: Whether to use RAG (None for auto-detection based on intent)
            
        Returns:
            Dictionary with response and metadata
        """
        start_time = time.time()
        
        # Update message count
        if user_id not in self.user_metadata:
            self.user_metadata[user_id] = {
                "created_at": time.time(),
                "message_count": 0,
                "last_activity": time.time()
            }
        
        self.user_metadata[user_id]["message_count"] += 1
        self.user_metadata[user_id]["last_activity"] = time.time()
        
        try:
            # Classify intent
            intent, confidence = self.intent_classifier.classify_intent(message)
            intent_metadata = self.intent_classifier.get_intent_metadata(intent)
            
            # Determine if RAG should be used
            if use_rag is None:
                use_rag = self.intent_classifier.should_use_rag(intent)
            
            if use_rag:
                # Use RAG for enhanced responses
                result = await self.rag_chain.process_query(message, user_id)
                result["response_type"] = "rag"
            else:
                # Use regular chat
                conversation = self.get_or_create_conversation(user_id)
                result = await conversation.chat(message, user_id)
                result["response_type"] = "chat"
            
            # Add intent classification metadata
            result["intent"] = intent.value
            result["confidence"] = confidence
            result["intent_description"] = intent_metadata["description"]
            result["response_style"] = intent_metadata["response_style"]
            
            # Add metadata
            result["user_id"] = user_id
            result["message_count"] = self.user_metadata[user_id]["message_count"]
            result["latency_ms"] = (time.time() - start_time) * 1000
            
            return result
            
        except Exception as e:
            # Log error and return error response
            error_result = {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "user_id": user_id,
                "error": True,
                "latency_ms": (time.time() - start_time) * 1000,
                "response_type": "error",
                "intent": "general",
                "confidence": 0.0
            }
            return error_result
    
    def add_documents_to_knowledge_base(self, documents) -> Dict[str, Any]:
        """
        Add documents to the knowledge base
        
        Args:
            documents: List of documents to add
            
        Returns:
            Dictionary with operation results
        """
        return self.rag_chain.add_documents_to_knowledge_base(documents)
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics
        
        Returns:
            Dictionary with knowledge base statistics
        """
        return self.rag_chain.get_knowledge_base_stats()
    
    def clear_knowledge_base(self) -> Dict[str, Any]:
        """
        Clear the knowledge base
        
        Returns:
            Dictionary with operation results
        """
        return self.rag_chain.clear_knowledge_base()
    
    def clear_conversation(self, user_id: str) -> bool:
        """Clear conversation history for a user"""
        if user_id in self.conversations:
            self.conversations[user_id].clear_memory()
            self.user_metadata[user_id]["message_count"] = 0
            return True
        return False
    
    def get_conversation_history(self, user_id: str) -> list:
        """Get conversation history for a user"""
        if user_id in self.conversations:
            return self.conversations[user_id].get_conversation_history(user_id)
        return []
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics for a user"""
        if user_id in self.user_metadata:
            return {
                "user_id": user_id,
                "message_count": self.user_metadata[user_id]["message_count"],
                "created_at": self.user_metadata[user_id]["created_at"],
                "last_activity": self.user_metadata[user_id]["last_activity"],
                "active_conversations": len(self.conversations)
            }
        return {}
    
    def cleanup_inactive_conversations(self, max_inactive_hours: int = 24):
        """Clean up conversations that have been inactive for too long"""
        current_time = time.time()
        inactive_threshold = current_time - (max_inactive_hours * 3600)
        
        inactive_users = []
        for user_id, metadata in self.user_metadata.items():
            if metadata["last_activity"] < inactive_threshold:
                inactive_users.append(user_id)
        
        # Remove inactive conversations
        for user_id in inactive_users:
            del self.conversations[user_id]
            del self.user_metadata[user_id]
        
        return len(inactive_users) 
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
        self.rag_chains: Dict[str, RAGChain] = {}  # Session-specific RAG chains
        self.chat_chain = ChatChain()  # Add direct chat chain
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
    
    def get_or_create_rag_chain(self, session_id: str) -> RAGChain:
        """Get existing RAG chain or create new session-specific one"""
        if session_id not in self.rag_chains:
            self.rag_chains[session_id] = RAGChain(session_id=session_id)
        return self.rag_chains[session_id]
    
    async def process_message(self, message: str, user_id: str, use_rag: Optional[bool] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
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
        
        # Update message count and analytics
        if user_id not in self.user_metadata:
            self.user_metadata[user_id] = {
                "created_at": time.time(),
                "message_count": 0,
                "last_activity": time.time(),
                "total_tokens": 0,
                "total_cost": 0.0,
                "response_times": []
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
            # If use_rag is explicitly set to False, respect that choice
            
            print(f"DEBUG: Final use_rag decision: {use_rag}, intent: {intent.value}")
            
            if use_rag:
                # Use session-specific RAG for enhanced responses
                print(f"DEBUG: Using RAG chain for message: {message}, session: {session_id}")
                rag_chain = self.get_or_create_rag_chain(session_id or user_id)
                result = await rag_chain.process_query(message, user_id)
                result["response_type"] = "rag"
                result["session_id"] = session_id or user_id
                # Ensure user has a conversation object for history tracking
                self.get_or_create_conversation(user_id)
            else:
                # Use regular chat (direct OpenAI without RAG)
                print(f"DEBUG: Using Chat chain for message: {message}")
                result = await self.chat_chain.chat(message, user_id)
                result["response_type"] = "chat"
                # Ensure user has a conversation object for history tracking
                self.get_or_create_conversation(user_id)
            
            # Add intent classification metadata
            result["intent"] = intent.value if intent else "general"
            result["confidence"] = confidence
            result["intent_description"] = intent_metadata.get("description", "General conversation") if intent_metadata else "General conversation"
            result["response_style"] = intent_metadata.get("response_style", "conversational") if intent_metadata else "conversational"
            
            # Add metadata
            result["user_id"] = user_id
            result["message_count"] = self.user_metadata[user_id]["message_count"]
            result["latency_ms"] = (time.time() - start_time) * 1000
            
            # Track analytics
            response_time = (time.time() - start_time) * 1000
            if "response_times" not in self.user_metadata[user_id]:
                self.user_metadata[user_id]["response_times"] = []
            self.user_metadata[user_id]["response_times"].append(response_time)
            
            # Estimate cost (rough calculation based on message length)
            estimated_tokens = len(message.split()) * 1.3  # Rough token estimate
            estimated_cost = estimated_tokens * 0.00002  # $0.00002 per token (GPT-4 pricing)
            
            if "total_tokens" not in self.user_metadata[user_id]:
                self.user_metadata[user_id]["total_tokens"] = 0
            if "total_cost" not in self.user_metadata[user_id]:
                self.user_metadata[user_id]["total_cost"] = 0.0
                
            self.user_metadata[user_id]["total_tokens"] += estimated_tokens
            self.user_metadata[user_id]["total_cost"] += estimated_cost
            
            # Keep only last 100 response times for performance
            if len(self.user_metadata[user_id]["response_times"]) > 100:
                self.user_metadata[user_id]["response_times"] = self.user_metadata[user_id]["response_times"][-100:]
            
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
    
    def add_documents_to_knowledge_base(self, documents, session_id: str = None) -> Dict[str, Any]:
        """
        Add documents to the knowledge base
        
        Args:
            documents: List of documents to add
            session_id: Optional session ID for session-specific knowledge base
            
        Returns:
            Dictionary with operation results
        """
        if session_id:
            # Use session-specific RAG chain
            rag_chain = self.get_or_create_rag_chain(session_id)
            return rag_chain.add_documents_to_knowledge_base(documents)
        else:
            # Use default global RAG chain (backward compatibility)
            if not hasattr(self, 'default_rag_chain'):
                self.default_rag_chain = RAGChain()
            return self.default_rag_chain.add_documents_to_knowledge_base(documents)
    
    def get_knowledge_base_stats(self, session_id: str = None) -> Dict[str, Any]:
        """
        Get knowledge base statistics
        
        Args:
            session_id: Optional session ID for session-specific stats
            
        Returns:
            Dictionary with knowledge base statistics
        """
        if session_id and session_id in self.rag_chains:
            # Return session-specific stats
            return self.rag_chains[session_id].get_knowledge_base_stats()
        elif session_id:
            # Session doesn't exist, return empty stats
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "collection_name": f"session_{session_id}",
                "status": "empty"
            }
        else:
            # Return global stats (backward compatibility)
            if hasattr(self, 'default_rag_chain'):
                return self.default_rag_chain.get_knowledge_base_stats()
            else:
                return {
                    "total_documents": 0,
                    "total_chunks": 0,
                    "collection_name": "default",
                    "status": "empty"
                }
    
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
    
    def get_document_count(self) -> int:
        """
        Get the number of documents in the knowledge base
        
        Returns:
            Number of documents in knowledge base
        """
        try:
            stats = self.get_knowledge_base_stats()
            return stats.get("total_documents", 0)
        except Exception as e:
            print(f"Error getting document count: {e}")
            return 0
    
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
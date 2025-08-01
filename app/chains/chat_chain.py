"""
LangChain chat chain implementation
"""
import os
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain_community.callbacks.manager import get_openai_callback

from app.config import settings

class ChatChain:
    """Main chat chain with OpenAI GPT-4 integration"""
    
    def __init__(self):
        """Initialize the chat chain"""
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # System prompt for the chatbot
        self.system_prompt = """You are a helpful AI assistant. You provide accurate, 
        informative, and engaging responses. Always be polite and professional."""
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # Create the chain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            verbose=False
        )
        
        # Memory for conversation history
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    
    async def chat(self, message: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Process a chat message
        
        Args:
            message: User's message
            user_id: User identifier for tracking
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Get conversation history for this user
            chat_history = self.memory.chat_memory.messages
            
            # Prepare inputs for the chain
            inputs = {
                "input": message,
                "chat_history": chat_history
            }
            
            # Get response with OpenAI callback for token tracking
            with get_openai_callback() as cb:
                response = await self.chain.ainvoke(inputs)
            
            # Add messages to memory
            self.memory.chat_memory.add_user_message(message)
            self.memory.chat_memory.add_ai_message(response["text"])
            
            return {
                "response": response["text"],
                "tokens_used": cb.total_tokens,
                "cost": cb.total_cost,
                "model": settings.OPENAI_MODEL
            }
                
        except Exception as e:
            # Log error and return appropriate response
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "tokens_used": 0,
                "cost": 0.0,
                "model": settings.OPENAI_MODEL
            }
    
    def clear_memory(self, user_id: str = "default"):
        """Clear conversation memory for a user"""
        self.memory.clear()
    
    def get_conversation_history(self, user_id: str = "default") -> List[Dict[str, str]]:
        """Get conversation history for a user"""
        messages = self.memory.chat_memory.messages
        history = []
        
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                history.append({
                    "user": messages[i].content,
                    "assistant": messages[i + 1].content
                })
        
        return history 
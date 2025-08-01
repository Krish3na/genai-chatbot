"""
RAG (Retrieval-Augmented Generation) chain implementation
"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain_community.callbacks.manager import get_openai_callback

from app.config import settings
from app.retriever.vector_store import VectorStore

class RAGChain:
    """RAG chain combining document retrieval with generation"""
    
    def __init__(self):
        """Initialize RAG chain"""
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.vector_store = VectorStore()
        
        # RAG prompt template
        self.rag_prompt = ChatPromptTemplate.from_template("""
You are a helpful AI assistant with access to a knowledge base. Use the provided context to answer the user's question accurately and comprehensively.

Context:
{context}

Question: {question}

Please provide a detailed answer based on the context provided. If the context doesn't contain enough information to answer the question, say so and provide a general response based on your knowledge.

Answer:""")
    
    async def process_query(self, query: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Process a query using RAG
        
        Args:
            query: User's question
            user_id: User identifier
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Retrieve relevant documents
            relevant_docs = self.vector_store.similarity_search(query, k=4)
            
            # Prepare context from retrieved documents
            context = self._prepare_context(relevant_docs)
            
            # Generate response using RAG
            with get_openai_callback() as cb:
                response = await self.llm.ainvoke(
                    self.rag_prompt.format(
                        context=context,
                        question=query
                    )
                )
            
            # Prepare response data
            response_data = {
                "response": response.content,
                "tokens_used": cb.total_tokens,
                "cost": cb.total_cost,
                "model": settings.OPENAI_MODEL,
                "sources_used": len(relevant_docs),
                "context_length": len(context)
            }
            
            return response_data
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "tokens_used": 0,
                "cost": 0.0,
                "model": settings.OPENAI_MODEL,
                "sources_used": 0,
                "context_length": 0
            }
    
    def _prepare_context(self, documents: List[Document]) -> str:
        """
        Prepare context from retrieved documents
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            # Extract source information
            source = doc.metadata.get('source', 'Unknown source')
            page = doc.metadata.get('page', '')
            
            # Format document content
            content = doc.page_content.strip()
            if len(content) > 500:  # Truncate long content
                content = content[:500] + "..."
            
            context_parts.append(f"Document {i} (Source: {source}{f', Page: {page}' if page else ''}):\n{content}\n")
        
        return "\n".join(context_parts)
    
    def add_documents_to_knowledge_base(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Add documents to the knowledge base
        
        Args:
            documents: List of documents to add
            
        Returns:
            Dictionary with operation results
        """
        try:
            self.vector_store.add_documents(documents)
            
            # Get updated stats
            stats = self.vector_store.get_collection_stats()
            
            return {
                "success": True,
                "documents_added": len(documents),
                "vector_store_stats": stats
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "documents_added": 0
            }
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics
        
        Returns:
            Dictionary with knowledge base statistics
        """
        return self.vector_store.get_collection_stats()
    
    def clear_knowledge_base(self) -> Dict[str, Any]:
        """
        Clear the knowledge base
        
        Returns:
            Dictionary with operation results
        """
        try:
            # Try the standard clear method first
            self.vector_store.clear_vector_store()
            
            # Check if it actually worked by getting stats
            stats = self.vector_store.get_collection_stats()
            if stats["total_documents"] > 0:
                # If still has documents, try manual clear
                print("⚠️ Standard clear didn't work, trying manual clear...")
                self.vector_store.clear_vector_store_manual()
            
            return {
                "success": True,
                "message": "Knowledge base cleared successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            } 
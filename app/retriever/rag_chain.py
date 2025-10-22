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
from app.utils.metrics import record_rag_metrics

class RAGChain:
    """RAG chain combining document retrieval with generation"""
    
    def __init__(self, session_id: str = None):
        """Initialize RAG chain
        
        Args:
            session_id: Optional session ID for session-specific knowledge base
        """
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize vector store with session ID (lazy initialization)
        self.session_id = session_id
        self.vector_store = VectorStore(session_id=session_id)
        
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
            # Try to retrieve relevant documents
            try:
                relevant_docs = self.vector_store.similarity_search(query, k=4)
                if relevant_docs:
                    context = self._prepare_context(relevant_docs)
                    sources_used = len(relevant_docs)
                    use_rag = True
                    print(f"Using RAG with {sources_used} documents")
                else:
                    # No documents found, use general knowledge with RAG
                    context = "No specific documents found. Please provide a general response based on your knowledge."
                    sources_used = 0
                    use_rag = True
                    print("Using RAG with general knowledge (no documents found)")
            except Exception as e:
                print(f"Vector store failed, falling back to direct OpenAI: {e}")
                # Fallback to direct OpenAI call without RAG
                context = "Please provide a helpful response to the user's question."
                sources_used = 0
                use_rag = False
                print("Using direct OpenAI (fallback mode)")
            
            # Generate response
            with get_openai_callback() as cb:
                if use_rag:
                    response = await self.llm.ainvoke(
                        self.rag_prompt.format(
                            context=context,
                            question=query
                        )
                    )
                else:
                    # Direct response without RAG
                    direct_prompt = f"Please provide a helpful response to this question: {query}"
                    response = await self.llm.ainvoke(direct_prompt)
            
            # Prepare response data
            response_data = {
                "response": response.content,
                "tokens_used": cb.total_tokens,
                "cost": cb.total_cost,
                "model": settings.OPENAI_MODEL,
                "sources_used": sources_used,
                "context_length": len(context),
                "method": "rag" if use_rag else "direct"
            }
            
            # Record RAG metrics if RAG was used
            if use_rag:
                try:
                    print(f"DEBUG: About to record RAG metrics for user {user_id}")
                    record_rag_metrics(
                        user_id=user_id,
                        sources_used=sources_used,
                        context_length=len(context)
                    )
                    print(f"DEBUG: RAG metrics recorded successfully")
                except Exception as e:
                    print(f"DEBUG: Failed to record RAG metrics: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"DEBUG: Not recording RAG metrics (use_rag=False)")
            
            return response_data
            
        except Exception as e:
            print(f"Error in RAG chain: {e}")
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "tokens_used": 0,
                "cost": 0.0,
                "model": settings.OPENAI_MODEL,
                "sources_used": 0,
                "context_length": 0,
                "method": "error"
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
            context_parts.append(f"Document {i}:\n{doc.page_content}\n")
        
        return "\n".join(context_parts)
    
    def add_documents_to_knowledge_base(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Add documents to the knowledge base
        
        Args:
            documents: List of documents to add
            
        Returns:
            Dictionary with operation result
        """
        try:
            self.vector_store.add_documents(documents)
            return {
                "success": True,
                "documents_added": len(documents),
                "message": f"Successfully added {len(documents)} documents to knowledge base"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to add documents to knowledge base: {str(e)}"
            }
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics
        
        Returns:
            Dictionary with knowledge base statistics
        """
        try:
            stats = self.vector_store.get_collection_stats()
            return stats
        except Exception as e:
            return {
                "total_documents": 0,
                "persist_directory": str(self.vector_store.persist_directory),
                "collection_name": "documents",
                "error": str(e)
            }
    
    def clear_knowledge_base(self) -> Dict[str, Any]:
        """
        Clear the knowledge base
        
        Returns:
            Dictionary with operation result
        """
        try:
            self.vector_store.clear()
            return {
                "success": True,
                "message": "Knowledge base cleared successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to clear knowledge base: {str(e)}"
            } 
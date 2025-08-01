"""
Vector store implementation using ChromaDB for RAG
"""
import os
import shutil
from typing import List, Optional
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from app.config import settings

class VectorStore:
    """Vector store for document embeddings using ChromaDB"""
    
    def __init__(self, persist_directory: str = "chroma_db"):
        """
        Initialize vector store
        
        Args:
            persist_directory: Directory to persist vector store
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize or load existing vector store
        self.vector_store = self._initialize_vector_store()
    
    def _initialize_vector_store(self) -> Chroma:
        """
        Initialize or load existing ChromaDB vector store
        
        Returns:
            ChromaDB vector store instance
        """
        try:
            # Try to load existing vector store
            vector_store = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings,
                collection_name="documents"
            )
            print(f"✅ Loaded existing vector store from {self.persist_directory}")
            return vector_store
        except Exception as e:
            print(f"⚠️ Could not load existing vector store: {e}")
            # Create new vector store
            vector_store = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings,
                collection_name="documents"
            )
            print(f"✅ Created new vector store at {self.persist_directory}")
            return vector_store
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to vector store
        
        Args:
            documents: List of documents to add
        """
        if not documents:
            print("⚠️ No documents to add")
            return
        
        try:
            # Split documents into chunks
            print(f"📄 Processing {len(documents)} documents...")
            chunks = self.text_splitter.split_documents(documents)
            print(f"📄 Created {len(chunks)} chunks")
            
            # Add chunks to vector store
            self.vector_store.add_documents(chunks)
            self.vector_store.persist()
            
            print(f"✅ Added {len(chunks)} chunks to vector store")
            
        except Exception as e:
            print(f"❌ Error adding documents to vector store: {e}")
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of similar documents
        """
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"❌ Error searching vector store: {e}")
            return []
    
    def get_collection_stats(self) -> dict:
        """
        Get vector store statistics
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self.vector_store._collection
            count = collection.count()
            return {
                "total_documents": count,
                "persist_directory": str(self.persist_directory),
                "collection_name": "documents"
            }
        except Exception as e:
            print(f"❌ Error getting collection stats: {e}")
            return {
                "total_documents": 0,
                "persist_directory": str(self.persist_directory),
                "collection_name": "documents"
            }
    
    def clear_vector_store(self) -> None:
        """Clear all documents from vector store"""
        try:
            # Method 1: Try the standard delete with proper where clause
            self.vector_store._collection.delete(where={"$and": []})
            print("✅ Cleared vector store")
        except Exception as e:
            print(f"⚠️ Primary clear method failed: {e}")
            
            # Method 2: Try alternative delete syntax
            try:
                self.vector_store._collection.delete(where={"id": {"$ne": ""}})
                print("✅ Cleared vector store (method 2)")
            except Exception as e2:
                print(f"⚠️ Method 2 failed: {e2}")
                
                # Method 3: Try to delete by getting all IDs first
                try:
                    # Get all document IDs and delete them
                    results = self.vector_store._collection.get()
                    if results and results['ids']:
                        self.vector_store._collection.delete(ids=results['ids'])
                        print("✅ Cleared vector store (method 3)")
                    else:
                        print("✅ Vector store was already empty")
                except Exception as e3:
                    print(f"❌ All clearing methods failed: {e3}")
                    print("💡 You may need to manually delete the chroma_db directory")
    
    def clear_vector_store_manual(self) -> None:
        """Manually clear vector store by deleting the directory and reinitializing"""
        try:
            # Close the current vector store
            if hasattr(self.vector_store, '_client'):
                self.vector_store._client.close()
            
            # Delete the persist directory
            if self.persist_directory.exists():
                shutil.rmtree(self.persist_directory)
                print(f"🗑️ Deleted vector store directory: {self.persist_directory}")
            
            # Reinitialize the vector store
            self.vector_store = self._initialize_vector_store()
            print("✅ Vector store cleared and reinitialized")
            
        except Exception as e:
            print(f"❌ Manual clear failed: {e}")
            # Try to reinitialize anyway
            try:
                self.vector_store = self._initialize_vector_store()
                print("✅ Vector store reinitialized")
            except Exception as e2:
                print(f"❌ Reinitialization failed: {e2}") 
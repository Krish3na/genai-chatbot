"""
Vector store implementation using ChromaDB
"""
import os
from typing import List, Optional
from pathlib import Path

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings

class VectorStore:
    """ChromaDB vector store wrapper with session-based collections"""
    
    def __init__(self, session_id: Optional[str] = None):
        """Initialize the vector store
        
        Args:
            session_id: Optional session ID for creating session-specific collections
        """
        # Set up persist directory
        self.persist_directory = Path(settings.CHROMA_PERSIST_DIRECTORY)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Set up text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Track document count separately from chunks
        self.document_count = 0
        self._document_count_initialized = False
        
        # Session-based collection management
        self.session_id = session_id
        self.collection_name = f"session_{session_id}" if session_id else "documents"
        
        # Initialize embeddings and vector store as None - will be created when needed
        self._embeddings: Optional[OpenAIEmbeddings] = None
        self._vector_store: Optional[Chroma] = None
    
    def _initialize_document_count(self):
        """Initialize document count from existing collection metadata"""
        if self._document_count_initialized:
            return
            
        try:
            vector_store = self._get_vector_store()
            collection = vector_store._collection
            
            # Get all metadata to count unique documents
            if hasattr(collection, 'get') and collection.count() > 0:
                # Get all documents and count unique sources
                results = collection.get()
                if results and 'metadatas' in results:
                    unique_files = set()
                    for metadata in results['metadatas']:
                        if metadata:
                            # Prefer file_name over source for more accurate counting
                            if 'file_name' in metadata:
                                unique_files.add(metadata['file_name'])
                            elif 'source' in metadata:
                                # Fallback to source, but extract filename
                                import os
                                unique_files.add(os.path.basename(metadata['source']))
                    self.document_count = len(unique_files)
                    print(f"Initialized document count: {self.document_count} files from {collection.count()} chunks")
                else:
                    # Fallback: estimate based on chunks (assume 4 chunks per document)
                    chunk_count = collection.count()
                    self.document_count = max(1, chunk_count // 4) if chunk_count > 0 else 0
                    print(f"Estimated document count: {self.document_count} documents from {chunk_count} chunks")
            else:
                self.document_count = 0
                
        except Exception as e:
            print(f"Error initializing document count: {e}")
            self.document_count = 0
            
        self._document_count_initialized = True
    
    def _get_embeddings(self) -> OpenAIEmbeddings:
        """
        Get or create embeddings instance (lazy initialization)
        
        Returns:
            OpenAI embeddings instance
        """
        if self._embeddings is None:
            try:
                self._embeddings = OpenAIEmbeddings(
                    openai_api_key=settings.OPENAI_API_KEY,
                    model="text-embedding-ada-002"
                )
                print("OpenAI embeddings initialized successfully")
            except Exception as e:
                print(f"Failed to initialize OpenAI embeddings: {e}")
                # Create a dummy embeddings class as fallback
                class DummyEmbeddings:
                    def embed_documents(self, texts):
                        return [[0.0] * 1536] * len(texts)
                    def embed_query(self, text):
                        return [0.0] * 1536
                
                self._embeddings = DummyEmbeddings()
                print("Using dummy embeddings as fallback")
        
        return self._embeddings
    
    def _get_vector_store(self) -> Chroma:
        """
        Get or create vector store instance (lazy initialization)
        
        Returns:
            ChromaDB vector store instance
        """
        if self._vector_store is None:
            try:
                # Try to load existing vector store
                self._vector_store = Chroma(
                    persist_directory=str(self.persist_directory),
                    embedding_function=self._get_embeddings(),
                    collection_name=self.collection_name
                )
                print(f"Loaded existing vector store from {self.persist_directory}")
            except Exception as e:
                print(f"Could not load existing vector store: {e}")
                try:
                    # Try to create new vector store with a different approach
                    import chromadb
                    from chromadb.config import Settings
                    
                    # Create a simple in-memory client as fallback
                    client = chromadb.Client(Settings(
                        chroma_db_impl="duckdb+parquet",
                        persist_directory=str(self.persist_directory),
                        anonymized_telemetry=False
                    ))
                    
                    # Create the vector store with the client
                    self._vector_store = Chroma(
                        client=client,
                        embedding_function=self._get_embeddings(),
                        collection_name=self.collection_name
                    )
                    print(f"Created new vector store with fallback client at {self.persist_directory}")
                except Exception as e2:
                    print(f"Failed to create vector store with fallback: {e2}")
                    # Create a minimal working vector store
                    self._vector_store = Chroma(
                        persist_directory="/tmp/chroma_fallback",
                        embedding_function=self._get_embeddings(),
                        collection_name="documents"
                    )
                    print(f"Created minimal vector store in /tmp/chroma_fallback")
        
        return self._vector_store
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to vector store
        
        Args:
            documents: List of documents to add
        """
        if not documents:
            print("No documents to add")
            return
        
        try:
            # Split documents into chunks
            print(f"📄 Processing {len(documents)} documents...")
            chunks = self.text_splitter.split_documents(documents)
            print(f"📄 Created {len(chunks)} chunks")
            
            # Add chunks to vector store
            vector_store = self._get_vector_store()
            vector_store.add_documents(chunks)
            vector_store.persist()
            
            # Update document count
            self.document_count += len(documents)
            
            print(f"Added {len(chunks)} chunks to vector store")
            
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
    
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
            vector_store = self._get_vector_store()
            results = vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"Error searching vector store: {e}")
            # Return empty list as fallback - this will make the RAG chain use general knowledge
            return []
    
    def get_collection_stats(self) -> dict:
        """
        Get vector store statistics
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            # Initialize document count if not already done
            self._initialize_document_count()
            
            vector_store = self._get_vector_store()
            collection = vector_store._collection
            chunk_count = collection.count()
            return {
                "total_documents": self.document_count,
                "total_chunks": chunk_count,
                "persist_directory": str(self.persist_directory),
                "collection_name": self.collection_name
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {
                "total_documents": 0,
                "persist_directory": str(self.persist_directory),
                "collection_name": "documents",
                "error": str(e)
            }
    
    def clear_vector_store(self) -> None:
        """Clear all documents from vector store"""
        try:
            # Method 1: Try the standard delete with proper where clause
            self._get_vector_store()._collection.delete(where={"$and": []})
            print("Cleared vector store")
        except Exception as e:
            print(f"Primary clear method failed: {e}")
            
            # Method 2: Try alternative delete syntax
            try:
                self._get_vector_store()._collection.delete(where={"id": {"$ne": ""}})
                print("Cleared vector store (method 2)")
            except Exception as e2:
                print(f"Method 2 failed: {e2}")
                
                # Method 3: Try to delete by getting all IDs first
                try:
                    # Get all document IDs and delete them
                    results = self._get_vector_store()._collection.get()
                    if results and results['ids']:
                        self._get_vector_store()._collection.delete(ids=results['ids'])
                        print("Cleared vector store (method 3)")
                    else:
                        print("Vector store was already empty")
                except Exception as e3:
                    print(f"All clearing methods failed: {e3}")
                    print("You may need to manually delete the chroma_db directory")
    
    def clear_vector_store_manual(self) -> None:
        """Manually clear vector store by deleting the directory and reinitializing"""
        try:
            # Close the current vector store
            if hasattr(self._get_vector_store(), '_client'):
                self._get_vector_store()._client.close()
            
            # Delete the persist directory
            if self.persist_directory.exists():
                os.rmdir(self.persist_directory) # Changed from shutil.rmtree to os.rmdir for directory
                print(f"Deleted vector store directory: {self.persist_directory}")
            
            # Reinitialize the vector store
            self._vector_store = self._get_vector_store() # Reassign to the new instance
            print("Vector store cleared and reinitialized")
            
        except Exception as e:
            print(f"Manual clear failed: {e}")
            # Try to reinitialize anyway
            try:
                self._vector_store = self._get_vector_store()
                print("Vector store reinitialized")
            except Exception as e2:
                print(f"Reinitialization failed: {e2}") 
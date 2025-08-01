#!/usr/bin/env python3
"""
Script to initialize the knowledge base with sample documents
"""
import asyncio
from app.retriever.document_loader import DocumentLoader
from app.retriever.rag_chain import RAGChain

async def init_knowledge_base():
    """Initialize the knowledge base with sample documents"""
    print("🚀 Initializing knowledge base...")
    
    # Initialize components
    document_loader = DocumentLoader()
    rag_chain = RAGChain()
    
    # Load all documents from data directory
    documents = document_loader.load_all_documents()
    
    if not documents:
        print("⚠️ No documents found in data directory")
        print("📁 Please add PDF or TXT files to the 'data' directory")
        return
    
    print(f"📄 Found {len(documents)} documents to process")
    
    # Add documents to knowledge base
    result = rag_chain.add_documents_to_knowledge_base(documents)
    
    if result["success"]:
        print(f"✅ Successfully added {result['documents_added']} document chunks to knowledge base")
        
        # Get and display stats
        stats = rag_chain.get_knowledge_base_stats()
        print(f"📊 Knowledge base stats: {stats['total_documents']} total documents")
        
    else:
        print(f"❌ Failed to add documents: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(init_knowledge_base()) 
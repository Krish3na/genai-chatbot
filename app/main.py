"""
Main FastAPI application for GenAI Chatbot
"""
import os
import time
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Response, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator

from app.chains.conversation_manager import ConversationManager
from app.chains.chat_chain import ChatChain
from app.retriever.rag_chain import RAGChain
from app.intents.intent_classifier import IntentClassifier
from app.retriever.document_loader import DocumentLoader
from app.config import settings
from app.utils import get_existing_file_hashes, calculate_file_hash
from app.utils.metrics import record_chat_metrics, record_document_upload, record_error
from prometheus_client import REGISTRY, generate_latest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GenAI Chatbot",
    description="Production-grade GenAI Chatbot with LangChain, OpenAI, RAG, and monitoring",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Prometheus metrics
# Disable automatic instrumentation for now - we'll use custom metrics
# instrumentator = Instrumentator()
# instrumentator.instrument(app)
# Don't expose metrics automatically, we'll handle it manually

# Initialize components
conversation_manager = ConversationManager()
chat_chain = ChatChain()
rag_chain = RAGChain()
intent_classifier = IntentClassifier()
document_loader = DocumentLoader()  # Will use DATA_DIR environment variable

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    session_id: str = "default_session"
    use_rag: Optional[bool] = None  # None for auto-detection based on intent

class DocumentUploadRequest(BaseModel):
    initialize_kb: bool = False  # Whether to initialize KB after upload

class ChatResponse(BaseModel):
    response: str
    intent: str = "general"
    confidence: float = 0.0
    intent_description: str = ""
    response_style: str = "conversational"
    latency_ms: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0
    model: str = ""
    response_type: str = "chat"
    sources_used: int = 0
    context_length: int = 0

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    version: str = "1.0.0"

class ConversationHistoryResponse(BaseModel):
    user_id: str
    history: list
    message_count: int

class KnowledgeBaseStatsResponse(BaseModel):
    total_documents: int
    persist_directory: str
    collection_name: str

class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    documents_added: int = 0
    error: str = ""

class DocumentDeleteRequest(BaseModel):
    filename: str

class DocumentDeleteMultipleRequest(BaseModel):
    filenames: list[str]

class DocumentDeleteResponse(BaseModel):
    success: bool
    message: str
    error: str = ""
    deleted_files: list[str] = []
    failed_files: list[str] = []

class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    duplicate_of: str = ""
    file_hash: str = ""
    message: str = ""

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health check"""
    return HealthResponse(
        status="healthy",
        timestamp=time.time()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=time.time()
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint with RAG capabilities"""
    start_time = time.time()
    
    try:
        # Use conversation manager to process the message (this handles intent classification, RAG, and conversation tracking)
        result = await conversation_manager.process_message(request.message, request.user_id, request.use_rag)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Record metrics
        record_chat_metrics(
            user_id=request.user_id,
            intent=result["intent"],
            response_type=result["response_type"],
            duration=latency_ms / 1000,  # Convert to seconds
            tokens=result["tokens_used"],
            cost=result["cost"],
            model=result["model"]
        )
        
        return {
            "response": result["response"],
            "intent": result["intent"],
            "confidence": result["confidence"],
            "intent_description": result["intent_description"],
            "response_style": result["response_style"],
            "latency_ms": latency_ms,
            "tokens_used": result["tokens_used"],
            "cost": result["cost"],
            "model": result["model"],
            "response_type": result["response_type"],
            "sources_used": result.get("sources_used", 0),
            "context_length": result.get("context_length", 0)
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return {
            "response": f"I apologize, but I encountered an error: {str(e)}",
            "intent": "error",
            "confidence": 0.0,
            "intent_description": "Error occurred",
            "response_style": "apologetic",
            "latency_ms": (time.time() - start_time) * 1000,
            "tokens_used": 0,
            "cost": 0.0,
            "model": settings.OPENAI_MODEL,
            "response_type": "error",
            "sources_used": 0,
            "context_length": 0
        }

@app.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    initialize_kb: bool = False
):
    """
    Upload a document to the knowledge base
    """
    try:
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Check for duplicate file
        file_path = data_dir / file.filename
        if file_path.exists():
            # Record failed upload metric
            file_type = file.filename.split('.')[-1].lower()
            record_document_upload(file_type, False)
            return DocumentUploadResponse(
                success=False,
                message=f"File '{file.filename}' already exists in data directory",
                error="Duplicate file"
            )
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Load document based on file type
        documents = []
        if file.filename.lower().endswith('.pdf'):
            documents = document_loader.load_pdf(str(file_path))
        elif file.filename.lower().endswith('.txt'):
            documents = document_loader.load_text(str(file_path))
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Only PDF and TXT files are supported."
            )
        
        if not documents:
            # Record failed upload metric
            file_type = file.filename.split('.')[-1].lower()
            record_document_upload(file_type, False)
            raise HTTPException(
                status_code=400,
                detail="Could not load document content."
            )
        
        # Add documents to knowledge base
        result = conversation_manager.add_documents_to_knowledge_base(documents)
        
        if result["success"]:
            # Record successful upload metric
            file_type = file.filename.split('.')[-1].lower()
            record_document_upload(file_type, True)
            
            # Update knowledge base document count
            from app.utils.metrics import update_knowledge_base_documents
            doc_count = conversation_manager.get_document_count()
            update_knowledge_base_documents(doc_count)
            
            message = f"Document '{file.filename}' uploaded successfully"
            
            # If requested, initialize knowledge base with all documents
            if initialize_kb:
                kb_result = conversation_manager.add_documents_to_knowledge_base(
                    document_loader.load_all_documents()
                )
                if kb_result["success"]:
                    message += f" and knowledge base reinitialized with {kb_result['documents_added']} total chunks"
                else:
                    message += " but knowledge base reinitialization failed"
            
            return DocumentUploadResponse(
                success=True,
                message=message,
                documents_added=result["documents_added"]
            )
        else:
            # Record failed upload metric
            file_type = file.filename.split('.')[-1].lower()
            record_document_upload(file_type, False)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to add document to knowledge base: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        # Record error metrics
        record_error("document_upload_error", "/upload-document")
        return DocumentUploadResponse(
            success=False,
            message="Failed to upload document",
            error=str(e)
        )

@app.post("/upload-document-multiple", response_model=DocumentUploadResponse)
async def upload_multiple_documents(
    files: list[UploadFile] = File(...),
    initialize_kb: bool = False
):
    """
    Upload multiple documents to the knowledge base
    """
    try:
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        uploaded_files = []
        failed_files = []
        all_documents = []
        
        # Process each uploaded file
        for file in files:
            try:
                # Check for duplicate file
                file_path = data_dir / file.filename
                if file_path.exists():
                    failed_files.append(f"{file.filename} (already exists)")
                    continue
                
                # Save uploaded file
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                
                # Load document based on file type
                documents = []
                if file.filename.lower().endswith('.pdf'):
                    documents = document_loader.load_pdf(str(file_path))
                elif file.filename.lower().endswith('.txt'):
                    documents = document_loader.load_text(str(file_path))
                else:
                    failed_files.append(f"{file.filename} (unsupported file type)")
                    continue
                
                if documents:
                    all_documents.extend(documents)
                    uploaded_files.append(file.filename)
                else:
                    failed_files.append(f"{file.filename} (could not load content)")
                    
            except Exception as e:
                failed_files.append(f"{file.filename} (error: {str(e)})")
        
        if not all_documents:
            return DocumentUploadResponse(
                success=False,
                message="No documents could be processed successfully",
                error="All files failed to process"
            )
        
        # Add all documents to knowledge base
        result = conversation_manager.add_documents_to_knowledge_base(all_documents)
        
        if result["success"]:
            # Update knowledge base document count
            from app.utils.metrics import update_knowledge_base_documents
            doc_count = conversation_manager.get_document_count()
            update_knowledge_base_documents(doc_count)
            
            message = f"Successfully uploaded {len(uploaded_files)} files with {result['documents_added']} chunks"
            
            if failed_files:
                message += f". Failed to process: {', '.join(failed_files)}"
            
            # If requested, initialize knowledge base with all documents
            if initialize_kb:
                kb_result = conversation_manager.add_documents_to_knowledge_base(
                    document_loader.load_all_documents()
                )
                if kb_result["success"]:
                    message += f" and knowledge base reinitialized with {kb_result['documents_added']} total chunks"
                else:
                    message += " but knowledge base reinitialization failed"
            
            return DocumentUploadResponse(
                success=True,
                message=message,
                documents_added=result["documents_added"]
            )
        else:
            return DocumentUploadResponse(
                success=False,
                message=f"Failed to add documents to knowledge base: {result.get('error', 'Unknown error')}",
                error=result.get('error', 'Unknown error')
            )
            
    except Exception as e:
        return DocumentUploadResponse(
            success=False,
            message="Failed to upload documents",
            error=str(e)
        )

@app.post("/knowledge-base/initialize", response_model=DocumentUploadResponse)
async def initialize_knowledge_base():
    """
    Initialize the knowledge base with all documents in the data directory
    """
    try:
        # Load all documents from data directory
        documents = document_loader.load_all_documents()
        
        if not documents:
            return DocumentUploadResponse(
                success=False,
                message="No documents found in data directory",
                error="No documents to process"
            )
        
        # Add documents to knowledge base
        result = conversation_manager.add_documents_to_knowledge_base(documents)
        
        if result["success"]:
            # Update knowledge base document count
            from app.utils.metrics import update_knowledge_base_documents
            doc_count = conversation_manager.get_document_count()
            update_knowledge_base_documents(doc_count)
            
            return DocumentUploadResponse(
                success=True,
                message=f"Knowledge base initialized successfully with {len(documents)} documents",
                documents_added=result["documents_added"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize knowledge base: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        return DocumentUploadResponse(
            success=False,
            message="Failed to initialize knowledge base",
            error=str(e)
        )

@app.get("/knowledge-base/stats", response_model=KnowledgeBaseStatsResponse)
async def get_knowledge_base_stats():
    """
    Get knowledge base statistics
    """
    stats = conversation_manager.get_knowledge_base_stats()
    return KnowledgeBaseStatsResponse(**stats)

@app.delete("/knowledge-base/clear")
async def clear_knowledge_base():
    """
    Clear the knowledge base
    """
    result = conversation_manager.clear_knowledge_base()
    if result["success"]:
        return {"message": "Knowledge base cleared successfully"}
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear knowledge base: {result.get('error', 'Unknown error')}"
        )

@app.delete("/knowledge-base/delete", response_model=DocumentDeleteResponse)
async def delete_document(request: DocumentDeleteRequest):
    """
    Delete a specific document from the data directory
    """
    try:
        # Create data directory path
        data_dir = Path("data")
        file_path = data_dir / request.filename
        
        # Check if file exists
        if not file_path.exists():
            return DocumentDeleteResponse(
                success=False,
                message=f"File '{request.filename}' not found in data directory",
                error="File not found"
            )
        
        # Delete the file
        file_path.unlink()
        
        # Optionally reinitialize knowledge base after deletion
        # Load remaining documents and reinitialize KB
        remaining_documents = document_loader.load_all_documents()
        
        if remaining_documents:
            # Clear existing KB and reinitialize with remaining documents
            conversation_manager.clear_knowledge_base()
            result = conversation_manager.add_documents_to_knowledge_base(remaining_documents)
            
            if result["success"]:
                return DocumentDeleteResponse(
                    success=True,
                    message=f"File '{request.filename}' deleted successfully. Knowledge base reinitialized with {result['documents_added']} chunks from remaining documents.",
                    deleted_files=[request.filename]
                )
            else:
                return DocumentDeleteResponse(
                    success=True,
                    message=f"File '{request.filename}' deleted successfully, but knowledge base reinitialization failed: {result.get('error', 'Unknown error')}",
                    deleted_files=[request.filename]
                )
        else:
            # No documents left, clear the knowledge base
            conversation_manager.clear_knowledge_base()
            return DocumentDeleteResponse(
                success=True,
                message=f"File '{request.filename}' deleted successfully. Knowledge base cleared as no documents remain.",
                deleted_files=[request.filename]
            )
            
    except Exception as e:
        return DocumentDeleteResponse(
            success=False,
            message=f"Failed to delete file '{request.filename}'",
            error=str(e),
            failed_files=[request.filename]
        )

@app.delete("/knowledge-base/delete-multiple", response_model=DocumentDeleteResponse)
async def delete_multiple_documents(request: DocumentDeleteMultipleRequest):
    """
    Delete multiple documents from the data directory
    """
    try:
        # Create data directory path
        data_dir = Path("data")
        deleted_files = []
        failed_files = []
        
        # Delete each file
        for filename in request.filenames:
            file_path = data_dir / filename
            
            if file_path.exists():
                try:
                    file_path.unlink()
                    deleted_files.append(filename)
                except Exception as e:
                    failed_files.append(filename)
            else:
                failed_files.append(filename)
        
        # Reinitialize knowledge base with remaining documents
        remaining_documents = document_loader.load_all_documents()
        
        if remaining_documents:
            # Clear existing KB and reinitialize with remaining documents
            conversation_manager.clear_knowledge_base()
            result = conversation_manager.add_documents_to_knowledge_base(remaining_documents)
            
            if result["success"]:
                message = f"Deleted {len(deleted_files)} files successfully. Knowledge base reinitialized with {result['documents_added']} chunks from remaining documents."
                if failed_files:
                    message += f" Failed to delete: {', '.join(failed_files)}"
                
                return DocumentDeleteResponse(
                    success=len(failed_files) == 0,
                    message=message,
                    deleted_files=deleted_files,
                    failed_files=failed_files
                )
            else:
                message = f"Deleted {len(deleted_files)} files successfully, but knowledge base reinitialization failed: {result.get('error', 'Unknown error')}"
                if failed_files:
                    message += f" Failed to delete: {', '.join(failed_files)}"
                
                return DocumentDeleteResponse(
                    success=False,
                    message=message,
                    deleted_files=deleted_files,
                    failed_files=failed_files
                )
        else:
            # No documents left, clear the knowledge base
            conversation_manager.clear_knowledge_base()
            message = f"Deleted {len(deleted_files)} files successfully. Knowledge base cleared as no documents remain."
            if failed_files:
                message += f" Failed to delete: {', '.join(failed_files)}"
            
            return DocumentDeleteResponse(
                success=len(failed_files) == 0,
                message=message,
                deleted_files=deleted_files,
                failed_files=failed_files
            )
            
    except Exception as e:
        return DocumentDeleteResponse(
            success=False,
            message=f"Failed to delete files",
            error=str(e),
            failed_files=request.filenames
        )

@app.post("/check-duplicate", response_model=DuplicateCheckResponse)
async def check_duplicate(file: UploadFile = File(...)):
    """
    Check if a file is a duplicate of existing files
    """
    try:
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Save uploaded file temporarily
        temp_file_path = data_dir / f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Calculate hash of uploaded file
        file_hash = calculate_file_hash(temp_file_path)
        
        # Get existing file hashes
        existing_hashes = get_existing_file_hashes(data_dir)
        
        # Check for duplicates
        if file_hash in existing_hashes:
            duplicate_filename = existing_hashes[file_hash]
            # Clean up temp file
            temp_file_path.unlink()
            
            return DuplicateCheckResponse(
                is_duplicate=True,
                duplicate_of=duplicate_filename,
                file_hash=file_hash,
                message=f"File content is identical to '{duplicate_filename}'"
            )
        else:
            # Clean up temp file
            temp_file_path.unlink()
            
            return DuplicateCheckResponse(
                is_duplicate=False,
                file_hash=file_hash,
                message="File is not a duplicate"
            )
            
    except Exception as e:
        return DuplicateCheckResponse(
            is_duplicate=False,
            message=f"Error checking duplicate: {str(e)}"
        )

@app.get("/documents/available")
async def get_available_documents():
    """
    Get list of available documents in the data directory
    """
    documents = document_loader.get_available_documents()
    return {
        "documents": documents,
        "total_count": len(documents)
    }

@app.get("/conversation/{user_id}/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(user_id: str):
    """Get conversation history for a user"""
    history = conversation_manager.get_conversation_history(user_id)
    stats = conversation_manager.get_user_stats(user_id)
    
    return ConversationHistoryResponse(
        user_id=user_id,
        history=history,
        message_count=stats.get("message_count", 0)
    )

@app.delete("/conversation/{user_id}")
async def clear_conversation(user_id: str):
    """Clear conversation history for a user"""
    success = conversation_manager.clear_conversation(user_id)
    if success:
        return {"message": f"Conversation cleared for user {user_id}"}
    else:
        raise HTTPException(status_code=404, detail=f"No conversation found for user {user_id}")

@app.get("/stats/{user_id}")
async def get_user_stats(user_id: str):
    """Get user statistics"""
    stats = conversation_manager.get_user_stats(user_id)
    if stats:
        return stats
    else:
        raise HTTPException(status_code=404, detail=f"No stats found for user {user_id}")

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint without OpenAI"""
    return {
        "message": "Server is working!",
        "timestamp": time.time(),
        "status": "ok"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest
    return Response(generate_latest(), media_type="text/plain")

@app.get("/intents/info")
async def get_intent_info():
    """
    Get information about available intent types and their descriptions
    """
    intents = {
        "general": {
            "description": "General conversation and casual chat",
            "use_rag": False,
            "response_style": "conversational",
            "examples": ["Hello", "How are you?", "Tell me a joke"]
        },
        "technical": {
            "description": "Technical questions about system architecture and implementation",
            "use_rag": True,
            "response_style": "technical",
            "examples": ["How does the API work?", "Explain the Docker setup", "What is LangChain?"]
        },
        "help": {
            "description": "Help and support requests",
            "use_rag": True,
            "response_style": "helpful",
            "examples": ["I need help", "How do I use this?", "Can you assist me?"]
        },
        "knowledge": {
            "description": "Questions about features and capabilities",
            "use_rag": True,
            "response_style": "informative",
            "examples": ["What are the features?", "Tell me about RAG", "What can this chatbot do?"]
        },
        "system": {
            "description": "System status and health queries",
            "use_rag": False,
            "response_style": "system",
            "examples": ["What's the server status?", "Show me metrics", "System health"]
        }
    }
    
    return {
        "available_intents": intents,
        "total_intents": len(intents),
        "auto_classification": True
    }

@app.on_event("startup")
async def startup_event():
    """Initialize metrics on application startup"""
    try:
        from app.utils.metrics import update_knowledge_base_documents
        doc_count = conversation_manager.get_document_count()
        update_knowledge_base_documents(doc_count)
        print(f"✅ Initialized knowledge base document count: {doc_count}")
    except Exception as e:
        print(f"❌ Failed to initialize knowledge base metrics: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
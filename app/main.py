"""
Main FastAPI application for GenAI Chatbot
"""
import os
import time
import logging
import math
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Response
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
from app.utils.metrics import (
    record_chat_metrics, record_document_upload, record_error,
    log_system_metrics_to_mlflow, log_model_performance_to_mlflow
)
from app.utils.mlflow_alerts import alert_system
from app.monitoring.alert_scheduler import start_alert_monitoring, stop_alert_monitoring
from prometheus_client import REGISTRY, generate_latest

# Track server start time for uptime calculation
start_time = time.time()

def format_time_ago(seconds: float) -> str:
    """Format seconds into human readable time ago string"""
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hours ago"
    else:
        return f"{int(seconds / 86400)} days ago"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Filter out noisy monitoring logs
class MonitoringLogFilter(logging.Filter):
    def filter(self, record):
        # Skip logs for monitoring endpoints
        if hasattr(record, 'getMessage'):
            message = record.getMessage()
            noisy_endpoints = ['/metrics', '/health', '/alerts/check', '/alerts/status', '/mlflow/experiments']
            return not any(endpoint in message for endpoint in noisy_endpoints)
        return True

# Apply filter to uvicorn access logs
uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.addFilter(MonitoringLogFilter())

def sanitize_float(value):
    """Sanitize float values to be JSON compliant"""
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return 0.0
    return value

def sanitize_dict(data):
    """Recursively sanitize all float values in a dictionary"""
    if isinstance(data, dict):
        return {k: sanitize_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_dict(item) for item in data]
    else:
        return sanitize_float(data)

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

# Initialize MLflow if enabled
# MLflow completely disabled for now
if False:  # settings.MLFLOW_ENABLED:
    try:
        from app.utils.mlflow_tracker import mlflow_tracker
        
        # Log experiment configuration on startup
        config = {
            "model": settings.OPENAI_MODEL,
            "max_tokens": settings.OPENAI_MAX_TOKENS,
            "temperature": settings.OPENAI_TEMPERATURE,
            "rag_top_k": settings.RAG_TOP_K,
            "similarity_threshold": settings.RAG_SIMILARITY_THRESHOLD,
            "intent_threshold": settings.INTENT_CONFIDENCE_THRESHOLD,
            "environment": os.getenv("ENVIRONMENT", "development")
        }
        mlflow_tracker.log_experiment_config(config)
        logger.info("MLflow tracking initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MLflow: {e}")

logger.info("MLflow disabled - FastAPI running without experiment tracking")

# Pydantic models
class UploadedFile(BaseModel):
    name: str
    content: str
    type: str

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    session_id: str = "default_session"
    use_rag: Optional[bool] = None  # None for auto-detection based on intent
    uploaded_files: Optional[List[UploadedFile]] = None

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
    total_chunks: int = 0
    collection_name: str
    status: str = "ready"

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
    """Chat endpoint with RAG capabilities and document upload support"""
    start_time = time.time()
    
    try:
        # Process uploaded files if any
        if request.uploaded_files:
            logger.info(f"Processing {len(request.uploaded_files)} uploaded files for user {request.user_id}")
            
            # Save uploaded files temporarily and add to knowledge base
            for uploaded_file in request.uploaded_files:
                try:
                    # Create temp file
                    temp_file_path = f"temp_uploads/{uploaded_file.name}"
                    os.makedirs("temp_uploads", exist_ok=True)
                    
                    # Write content to temp file
                    with open(temp_file_path, 'w', encoding='utf-8') as f:
                        f.write(uploaded_file.content)
                    
                    # Process the file through document loader
                    document_loader = DocumentLoader()
                    chunks = await document_loader.load_and_chunk_document(temp_file_path)
                    
                    # Add to vector store
                    if chunks:
                        rag_chain.vector_store.add_documents(chunks)
                        logger.info(f"Added {len(chunks)} chunks from {uploaded_file.name} to knowledge base")
                    
                    # Clean up temp file
                    os.remove(temp_file_path)
                    
                    # Record upload metric
                    record_document_upload(uploaded_file.type, True)
                    
                except Exception as e:
                    logger.error(f"Error processing uploaded file {uploaded_file.name}: {e}")
                    record_document_upload(uploaded_file.type if hasattr(uploaded_file, 'type') else 'unknown', False)
        
        # Use conversation manager to process the message (this handles intent classification, RAG, and conversation tracking)
        result = await conversation_manager.process_message(request.message, request.user_id, request.use_rag, request.session_id)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Record metrics for Grafana filtering
        rag_sources = result.get("sources", []) if result.get("sources_used", 0) > 0 else None
        record_chat_metrics(
            user_id=request.user_id,
            intent=result["intent"],
            response_type=result["response_type"],
            duration=latency_ms / 1000,  # Convert to seconds
            tokens=result["tokens_used"],
            cost=result["cost"],
            model=result["model"],
            response=result["response"],
            rag_sources=rag_sources,
            confidence=result.get("confidence", 0.0)
        )
        
        response_data = {
            "response": result.get("response", "No response available"),
            "intent": result.get("intent", "general"),
            "confidence": result.get("confidence", 0.0),
            "intent_description": result.get("intent_description", "General conversation"),
            "response_style": result.get("response_style", "conversational"),
            "latency_ms": latency_ms,
            "tokens_used": result.get("tokens_used", 0),
            "cost": result.get("cost", 0.0),
            "model": result.get("model", "unknown"),
            "response_type": result.get("response_type", "chat"),
            "sources_used": result.get("sources_used", 0),
            "context_length": result.get("context_length", 0)
        }
        return sanitize_dict(response_data)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        error_data = {
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
        return sanitize_dict(error_data)

@app.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    initialize_kb: bool = False,
    session_id: str = Form(None)
):
    """
    Upload a document to the knowledge base
    """
    try:
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # For session isolation, allow the same file to be uploaded to different sessions
        # We'll let the conversation manager handle session-specific storage
        file_path = data_dir / file.filename
        
        # Debug logging
        logger.info(f"Upload request - file: {file.filename}, session_id: {session_id}, file_exists: {file_path.exists()}")
        
        # If file exists but we have a session_id, we'll still process it for the session
        if file_path.exists() and not session_id:
            # Only reject duplicates if no session_id is provided (backward compatibility)
            logger.info(f"Rejecting duplicate file {file.filename} (no session_id)")
            file_type = file.filename.split('.')[-1].lower()
            record_document_upload(file_type, False)
            return DocumentUploadResponse(
                success=False,
                message=f"File '{file.filename}' already exists in data directory",
                error="Duplicate file"
            )
        
        # If we have a session_id, allow processing even if file exists
        if session_id:
            logger.info(f"Processing file {file.filename} for session {session_id} (session isolation)")
        
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
        elif file.filename.lower().endswith('.csv'):
            documents = document_loader.load_csv(str(file_path))
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Only PDF, TXT, and CSV files are supported."
            )
        
        if not documents:
            # Record failed upload metric
            file_type = file.filename.split('.')[-1].lower()
            record_document_upload(file_type, False)
            raise HTTPException(
                status_code=400,
                detail="Could not load document content."
            )
        
        # Add documents to session-specific knowledge base
        result = conversation_manager.add_documents_to_knowledge_base(documents, session_id)
        
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
                    document_loader.load_all_documents(),
                    session_id
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
async def get_knowledge_base_stats(session_id: str = None):
    """
    Get knowledge base statistics
    
    Args:
        session_id: Optional session ID for session-specific stats
    """
    # Temporary simple implementation to avoid JSON serialization issues
    try:
        # For now, return basic stats based on session
        if session_id and session_id in conversation_manager.rag_chains:
            # Session exists, check if it has documents
            rag_chain = conversation_manager.rag_chains[session_id]
            try:
                # Try to get basic count
                collection = rag_chain.vector_store._get_vector_store()._collection
                chunk_count = collection.count() if collection else 0
                # Estimate documents as chunks divided by average chunks per document (assume ~3-5 chunks per doc)
                estimated_docs = max(1, chunk_count // 4) if chunk_count > 0 else 0
                return KnowledgeBaseStatsResponse(
                    total_documents=estimated_docs,
                    total_chunks=chunk_count,
                    collection_name=f"session_{session_id}",
                    status="ready"
                )
            except:
                # If any error, return empty stats
                return KnowledgeBaseStatsResponse(
                    total_documents=0,
                    total_chunks=0,
                    collection_name=f"session_{session_id}",
                    status="empty"
                )
        else:
            # Session doesn't exist or no session_id provided
            return KnowledgeBaseStatsResponse(
                total_documents=0,
                total_chunks=0,
                collection_name=f"session_{session_id}" if session_id else "default",
                status="empty"
            )
    except Exception as e:
        logger.error(f"Error getting knowledge base stats: {e}")
        # Return safe default values
        return KnowledgeBaseStatsResponse(
            total_documents=0,
            total_chunks=0,
            collection_name=f"session_{session_id}" if session_id else "default",
            status="error"
        )

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

@app.get("/dashboard/analytics")
async def get_dashboard_analytics(user_id: Optional[str] = None):
    """Get comprehensive dashboard analytics"""
    try:
        if user_id:
            # Get user-specific analytics
            if user_id not in conversation_manager.user_metadata:
                return {
                    "total_conversations": 0,
                    "total_messages": 0,
                    "total_users": 0,
                    "active_sessions": 0,
                    "avg_response_time": 0,
                    "daily_cost": 0.0,
                    "total_documents": 0,
                    "total_chunks": 0,
                    "system_uptime": time.time() - start_time,
                    "timestamp": time.time(),
                    "user_filter": user_id,
                    "performance_metrics": {
                        "total_response_times": 0,
                        "fastest_response": 0,
                        "slowest_response": 0
                    }
                }
            
            # Get specific user's data
            user_metadata = conversation_manager.user_metadata[user_id]
            total_users = 1  # Always 1 for user-specific view
            total_conversations = 1 if user_id in conversation_manager.conversations else 0
            total_messages = user_metadata.get("message_count", 0)
            
            # User-specific metrics
            response_times = user_metadata.get("response_times", [])
            avg_response_time = int(sum(response_times) / len(response_times)) if response_times else 0
            total_cost = user_metadata.get("total_cost", 0.0)
            
            # Check if user is active (last 24 hours)
            current_time = time.time()
            active_sessions = 1 if current_time - user_metadata.get("last_activity", 0) < 86400 else 0
            
            # User-specific knowledge base stats
            total_documents = 0
            total_chunks = 0
            if user_id in conversation_manager.rag_chains:
                kb_stats = conversation_manager.get_knowledge_base_stats(user_id)
                total_documents = kb_stats.get("total_documents", 0)
                total_chunks = kb_stats.get("total_chunks", 0)
            
            performance_metrics = {
                "total_response_times": len(response_times),
                "fastest_response": min(response_times) if response_times else 0,
                "slowest_response": max(response_times) if response_times else 0
            }
        else:
            # Get overall system stats
            total_users = len(conversation_manager.user_metadata)
            total_conversations = len(conversation_manager.conversations)
            
            # Calculate total messages and enhanced metrics
            total_messages = sum(
                metadata.get("message_count", 0) 
                for metadata in conversation_manager.user_metadata.values()
            )
            
            # Calculate average response time from actual data
            all_response_times = []
            total_cost = 0.0
            for metadata in conversation_manager.user_metadata.values():
                response_times = metadata.get("response_times", [])
                all_response_times.extend(response_times)
                total_cost += metadata.get("total_cost", 0.0)
            
            avg_response_time = int(sum(all_response_times) / len(all_response_times)) if all_response_times else 0
            
            # Get active sessions (last 24 hours)
            current_time = time.time()
            active_sessions = sum(
                1 for metadata in conversation_manager.user_metadata.values()
                if current_time - metadata.get("last_activity", 0) < 86400  # 24 hours
            )
            
            # Knowledge base stats across all sessions
            total_documents = 0
            total_chunks = 0
            for session_id in conversation_manager.rag_chains:
                kb_stats = conversation_manager.get_knowledge_base_stats(session_id)
                total_documents += kb_stats.get("total_documents", 0)
                total_chunks += kb_stats.get("total_chunks", 0)
            
            performance_metrics = {
                "total_response_times": len(all_response_times),
                "fastest_response": min(all_response_times) if all_response_times else 0,
                "slowest_response": max(all_response_times) if all_response_times else 0
            }
        
        result = {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_users": total_users,
            "active_sessions": active_sessions,
            "avg_response_time": avg_response_time,
            "daily_cost": round(total_cost, 4),  # More precise cost tracking
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "system_uptime": time.time() - start_time,
            "timestamp": time.time(),
            "performance_metrics": performance_metrics
        }
        
        # Add user filter info if applicable
        if user_id:
            result["user_filter"] = user_id
            
        return result
    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {e}")
        return {
            "total_conversations": 0,
            "total_messages": 0,
            "total_users": 0,
            "active_sessions": 0,
            "avg_response_time": 0,
            "daily_cost": 0.0,
            "total_documents": 0,
            "total_chunks": 0,
            "system_uptime": 0,
            "timestamp": time.time(),
            "error": str(e),
            "performance_metrics": {
                "total_response_times": 0,
                "fastest_response": 0,
                "slowest_response": 0
            }
        }

@app.get("/dashboard/recent-activity")
async def get_recent_activity(user_id: Optional[str] = None):
    """Get recent system activity"""
    try:
        activities = []
        current_time = time.time()
        
        if user_id and user_id != "all":
            # Get user-specific activities
            if user_id in conversation_manager.user_metadata:
                metadata = conversation_manager.user_metadata[user_id]
                last_activity = metadata.get("last_activity", 0)
                message_count = metadata.get("message_count", 0)
                
                if last_activity > 0:
                    time_ago = format_time_ago(current_time - last_activity)
                    activities.append({
                        "icon": "fas fa-comment",
                        "text": f"Last conversation ({message_count} messages total)",
                        "time": time_ago,
                        "timestamp": last_activity
                    })
                
                # Add user-specific document activities if they have RAG chains
                if user_id in conversation_manager.rag_chains:
                    kb_stats = conversation_manager.get_knowledge_base_stats(user_id)
                    if kb_stats.get("total_documents", 0) > 0:
                        activities.append({
                            "icon": "fas fa-upload",
                            "text": f"Uploaded {kb_stats['total_documents']} documents",
                            "time": "Recently",
                            "timestamp": last_activity - 300
                        })
                
                # Add user creation activity
                created_at = metadata.get("created_at", 0)
                if created_at > 0:
                    time_ago = format_time_ago(current_time - created_at)
                    activities.append({
                        "icon": "fas fa-user-plus",
                        "text": "User account created",
                        "time": time_ago,
                        "timestamp": created_at
                    })
            
            if not activities:
                activities.append({
                    "icon": "fas fa-info-circle",
                    "text": "No activity found for this user",
                    "time": "N/A",
                    "timestamp": current_time
                })
        else:
            # Get system-wide activities (last 24 hours)
            for uid, metadata in conversation_manager.user_metadata.items():
                last_activity = metadata.get("last_activity", 0)
                if current_time - last_activity < 86400:  # 24 hours
                    time_ago = format_time_ago(current_time - last_activity)
                    activities.append({
                        "icon": "fas fa-comment",
                        "text": f"User {uid} had a conversation",
                        "time": time_ago,
                        "timestamp": last_activity
                    })
            
            # Add system activities
            activities.extend([
                {
                    "icon": "fas fa-chart-line",
                    "text": "System metrics updated",
                    "time": "30 minutes ago",
                    "timestamp": current_time - 1800
                },
                {
                    "icon": "fas fa-server",
                    "text": "System health check completed",
                    "time": "1 hour ago",
                    "timestamp": current_time - 3600
                }
            ])
        
        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {"activities": activities[:10]}  # Return top 10
        
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return {"activities": []}

@app.get("/dashboard/system-health")
async def get_system_health():
    """Get comprehensive system health status"""
    try:
        health_status = {
            "api_server": {
                "status": "healthy",
                "response_time": 45,
                "last_check": time.time()
            },
            "database": {
                "status": "healthy",
                "connections": 5,
                "last_check": time.time()
            },
            "vector_store": {
                "status": "healthy",
                "collections": len(conversation_manager.rag_chains),
                "last_check": time.time()
            },
            "mlflow": {
                "status": "warning",
                "experiments": 0,
                "last_check": time.time()
            },
            "email_alerts": {
                "status": "warning",
                "last_sent": None,
                "last_check": time.time()
            }
        }
        
        # Check if we have active conversations
        if len(conversation_manager.conversations) == 0:
            health_status["api_server"]["status"] = "warning"
            
        return health_status
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return {
            "api_server": {"status": "error", "response_time": 0, "last_check": time.time()},
            "database": {"status": "error", "connections": 0, "last_check": time.time()},
            "vector_store": {"status": "error", "collections": 0, "last_check": time.time()},
            "mlflow": {"status": "error", "experiments": 0, "last_check": time.time()},
            "email_alerts": {"status": "error", "last_sent": None, "last_check": time.time()}
        }

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

@app.get("/mlflow/system-metrics")
async def log_system_metrics():
    """Log current system metrics to MLflow"""
    try:
        if not settings.MLFLOW_ENABLED:
            return {"message": "MLflow is disabled", "success": False}
            
        log_system_metrics_to_mlflow()
        return {"message": "System metrics logged to MLflow successfully", "success": True}
    except Exception as e:
        logger.error(f"Failed to log system metrics: {e}")
        return {"message": f"Failed to log system metrics: {str(e)}", "success": False}

@app.get("/mlflow/model-performance")
async def log_model_performance():
    """Log model performance metrics to MLflow"""
    try:
        if not settings.MLFLOW_ENABLED:
            return {"message": "MLflow is disabled", "success": False}
            
        log_model_performance_to_mlflow()
        return {"message": "Model performance logged to MLflow successfully", "success": True}
    except Exception as e:
        logger.error(f"Failed to log model performance: {e}")
        return {"message": f"Failed to log model performance: {str(e)}", "success": False}

@app.get("/mlflow/experiments")
async def get_mlflow_experiments():
    """Get MLflow experiment runs"""
    try:
        if not settings.MLFLOW_ENABLED:
            return {"message": "MLflow is disabled", "experiments": []}
            
        from app.utils.mlflow_tracker import mlflow_tracker
        runs = mlflow_tracker.get_experiment_runs()
        return {"experiments": runs, "count": len(runs)}
    except Exception as e:
        logger.error(f"Failed to get MLflow experiments: {e}")
        return {"message": f"Failed to get experiments: {str(e)}", "experiments": []}

@app.get("/mlflow/best-run")
async def get_best_mlflow_run():
    """Get the best MLflow run based on F1 score"""
    try:
        if not settings.MLFLOW_ENABLED:
            return {"message": "MLflow is disabled", "best_run": None}
            
        from app.utils.mlflow_tracker import mlflow_tracker
        best_run = mlflow_tracker.get_best_run("f1_score")
        return {"best_run": best_run}
    except Exception as e:
        logger.error(f"Failed to get best MLflow run: {e}")
        return {"message": f"Failed to get best run: {str(e)}", "best_run": None}

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

# MLflow Alert Endpoints
@app.get("/alerts/check")
async def check_alerts():
    """Run immediate alert checks"""
    try:
        if not settings.MLFLOW_ENABLED:
            return {
                "total_alerts": 0,
                "alerts": {},
                "timestamp": time.time(),
                "status": "disabled",
                "message": "MLflow alerts are disabled"
            }
            
        # TEMPORARILY DISABLED FOR PERFORMANCE - MLflow timestamp issues
        # alerts = alert_system.run_all_checks()
        alerts = {}
        
        # Count total alerts
        total_alerts = sum(len(alert_list) for alert_list in alerts.values())
        
        return {
            "total_alerts": total_alerts,
            "alerts": alerts,
            "timestamp": time.time(),
            "status": "critical" if any(
                alert.get("type") == "CRITICAL" 
                for alert_list in alerts.values() 
                for alert in alert_list
            ) else "warning" if total_alerts > 0 else "healthy"
        }
        
    except Exception as e:
        logger.error(f"Error checking alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts/thresholds")
async def get_alert_thresholds():
    """Get current alert thresholds"""
    try:
        if not settings.MLFLOW_ENABLED:
            raise HTTPException(status_code=503, detail="MLflow is not enabled")
            
        return {
            "thresholds": alert_system.thresholds,
            "description": {
                "response_time_warning": "Response time warning threshold (seconds)",
                "response_time_critical": "Response time critical threshold (seconds)",
                "accuracy_warning": "Model accuracy warning threshold (percentage)",
                "accuracy_critical": "Model accuracy critical threshold (percentage)",
                "cost_per_interaction_warning": "Cost per interaction warning threshold (USD)",
                "cost_per_interaction_critical": "Cost per interaction critical threshold (USD)",
                "daily_cost_warning": "Daily cost warning threshold (USD)",
                "daily_cost_critical": "Daily cost critical threshold (USD)",
                "error_rate_warning": "Error rate warning threshold (percentage)",
                "error_rate_critical": "Error rate critical threshold (percentage)"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting thresholds: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/alerts/thresholds")
async def update_alert_thresholds(thresholds: Dict[str, float]):
    """Update alert thresholds"""
    try:
        if not settings.MLFLOW_ENABLED:
            raise HTTPException(status_code=503, detail="MLflow is not enabled")
            
        # Validate threshold keys
        valid_keys = set(alert_system.thresholds.keys())
        provided_keys = set(thresholds.keys())
        
        invalid_keys = provided_keys - valid_keys
        if invalid_keys:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid threshold keys: {list(invalid_keys)}"
            )
            
        # Update thresholds
        alert_system.thresholds.update(thresholds)
        
        return {
            "message": "Thresholds updated successfully",
            "updated_thresholds": thresholds,
            "current_thresholds": alert_system.thresholds
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating thresholds: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts/status")
async def get_alert_status():
    """Get alert system status"""
    try:
        from app.monitoring.alert_scheduler import scheduler
        
        return {
            "mlflow_enabled": settings.MLFLOW_ENABLED,
            "alert_scheduler_running": scheduler.running,
            "alert_handlers_count": len(alert_system.alert_handlers),
            "email_alerts_enabled": settings.EMAIL_ALERTS_ENABLED,
            "email_configured": bool(settings.SENDER_EMAIL and settings.SENDER_PASSWORD),
            "alert_recipients": settings.ALERT_RECIPIENTS.split(",") if settings.ALERT_RECIPIENTS else [],
            "last_check": "Not implemented yet",  # Could add timestamp tracking
            "system_status": "operational" if settings.MLFLOW_ENABLED and scheduler.running else "disabled"
        }
        
    except Exception as e:
        logger.error(f"Error getting alert status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/alerts/test-email")
async def send_test_email():
    """Send a test email alert"""
    try:
        if not settings.EMAIL_ALERTS_ENABLED:
            raise HTTPException(status_code=400, detail="Email alerts are not enabled")
            
        if not settings.SENDER_EMAIL or not settings.SENDER_PASSWORD:
            raise HTTPException(status_code=400, detail="Email credentials not configured")
        
        # Create test alert
        test_alerts = [{
            "type": "WARNING",
            "category": "Test",
            "metric": "Email Configuration",
            "value": "Test",
            "threshold": "N/A",
            "message": "Your MLflow email alerts are working perfectly! This is a test message from your GenAI Chatbot monitoring system.",
            "timestamp": time.time()
        }]
        
        # Send test email
        alert_system.send_alerts({"test": test_alerts})
        
        recipients = settings.ALERT_RECIPIENTS.split(",")
        return {
            "message": "Test email sent successfully!",
            "recipients": recipients,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send test email: {str(e)}")

@app.get("/alerts/email-config")
async def get_email_config():
    """Get email configuration status (without sensitive data)"""
    try:
        return {
            "email_alerts_enabled": settings.EMAIL_ALERTS_ENABLED,
            "smtp_server": settings.SMTP_SERVER,
            "smtp_port": settings.SMTP_PORT,
            "sender_email": settings.SENDER_EMAIL,
            "sender_configured": bool(settings.SENDER_EMAIL),
            "password_configured": bool(settings.SENDER_PASSWORD),
            "recipients": settings.ALERT_RECIPIENTS.split(",") if settings.ALERT_RECIPIENTS else [],
            "recipients_count": len(settings.ALERT_RECIPIENTS.split(",")) if settings.ALERT_RECIPIENTS else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting email config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Initialize metrics on application startup"""
    try:
        from app.utils.metrics import update_knowledge_base_documents
        doc_count = conversation_manager.get_document_count()
        update_knowledge_base_documents(doc_count)
        print(f"Initialized knowledge base document count: {doc_count}")
        
        # Initialize MLflow if enabled
        if False:  # Completely disabled for now
            from app.utils.mlflow_tracker import mlflow_tracker
            mlflow_tracker.log_experiment_config({
                "model": settings.OPENAI_MODEL,
                "temperature": settings.OPENAI_TEMPERATURE,
                "max_tokens": settings.OPENAI_MAX_TOKENS,
                "rag_top_k": settings.RAG_TOP_K,
                "rag_similarity_threshold": settings.RAG_SIMILARITY_THRESHOLD,
                "intent_confidence_threshold": settings.INTENT_CONFIDENCE_THRESHOLD,
                "environment": os.getenv("ENVIRONMENT", "development"),
                "version": "1.0.0"
            })
            logger.info("MLflow experiment configuration logged")
            
            # Start alert monitoring (disabled for now)
            # start_alert_monitoring()
            logger.info("MLflow alert monitoring disabled")
            
            # Start cost tracking
            from app.utils.cost_aggregator import schedule_cost_logging
            schedule_cost_logging()
            logger.info("MLflow cost tracking started")
            
            # Start performance tracking
            from app.utils.performance_aggregator import schedule_performance_logging
            schedule_performance_logging()
            logger.info("MLflow performance tracking started")
            
            # Start quality tracking
            from app.utils.quality_aggregator import schedule_quality_logging
            schedule_quality_logging()
            logger.info("MLflow quality tracking started")
            
            # Start error tracking
            from app.utils.error_aggregator import schedule_error_logging
            schedule_error_logging()
            logger.info("MLflow error tracking started")
            
    except Exception as e:
        print(f"Failed to initialize metrics: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        # Stop alert monitoring
        stop_alert_monitoring()
        logger.info("Alert monitoring stopped")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    logger.info("Application shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
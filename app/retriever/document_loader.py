"""
Document loader for RAG implementation
"""
import os
from typing import List, Optional
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.schema import Document

class DocumentLoader:
    """Load documents from various file formats for RAG"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize document loader
        
        Args:
            data_dir: Directory containing documents
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """
        Load PDF document
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of document chunks
        """
        try:
            loader = PyPDFLoader(file_path)
            return loader.load()
        except Exception as e:
            print(f"Error loading PDF {file_path}: {e}")
            return []
    
    def load_text(self, file_path: str) -> List[Document]:
        """
        Load text document
        
        Args:
            file_path: Path to text file
            
        Returns:
            List of document chunks
        """
        try:
            loader = TextLoader(file_path)
            return loader.load()
        except Exception as e:
            print(f"Error loading text file {file_path}: {e}")
            return []
    
    def load_all_documents(self) -> List[Document]:
        """
        Load all documents from the data directory
        
        Returns:
            List of all document chunks
        """
        documents = []
        
        # Load PDFs
        for pdf_file in self.data_dir.glob("*.pdf"):
            documents.extend(self.load_pdf(str(pdf_file)))
        
        # Load text files
        for text_file in self.data_dir.glob("*.txt"):
            documents.extend(self.load_text(str(text_file)))
        
        return documents
    
    def get_available_documents(self) -> List[str]:
        """
        Get list of available document files
        
        Returns:
            List of document file names
        """
        files = []
        
        # PDF files
        for pdf_file in self.data_dir.glob("*.pdf"):
            files.append(pdf_file.name)
        
        # Text files
        for text_file in self.data_dir.glob("*.txt"):
            files.append(text_file.name)
        
        return files 
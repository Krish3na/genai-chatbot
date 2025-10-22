"""
Document loader for RAG implementation
"""
import os
from typing import List, Optional
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain.schema import Document

class DocumentLoader:
    """Load documents from various file formats for RAG"""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize document loader
        
        Args:
            data_dir: Directory containing documents
        """
        if data_dir is None:
            data_dir = os.getenv("DATA_DIR", "data")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """
        Load PDF document
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of document chunks (one per page)
        """
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Add file-level metadata to distinguish pages from separate files
            file_name = Path(file_path).name
            for i, doc in enumerate(documents):
                if doc.metadata:
                    doc.metadata['file_name'] = file_name
                    doc.metadata['page_number'] = i + 1
                    doc.metadata['total_pages'] = len(documents)
                else:
                    doc.metadata = {
                        'source': file_path,
                        'file_name': file_name,
                        'page_number': i + 1,
                        'total_pages': len(documents)
                    }
            
            print(f"Loaded PDF {file_name}: {len(documents)} pages")
            return documents
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
    
    def load_csv(self, file_path: str) -> List[Document]:
        """
        Load CSV document
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of document chunks
        """
        try:
            loader = CSVLoader(file_path)
            return loader.load()
        except Exception as e:
            print(f"Error loading CSV file {file_path}: {e}")
            return []
    
    async def load_and_chunk_document(self, file_path: str) -> List[Document]:
        """
        Load and chunk a single document based on its file type
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of document chunks
        """
        try:
            file_path = Path(file_path)
            
            if file_path.suffix.lower() == '.pdf':
                return self.load_pdf(str(file_path))
            elif file_path.suffix.lower() == '.txt':
                return self.load_text(str(file_path))
            elif file_path.suffix.lower() == '.csv':
                return self.load_csv(str(file_path))
            else:
                print(f"Unsupported file type: {file_path.suffix}")
                return []
                
        except Exception as e:
            print(f"Error loading and chunking document {file_path}: {e}")
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
        
        # Load CSV files
        for csv_file in self.data_dir.glob("*.csv"):
            documents.extend(self.load_csv(str(csv_file)))
        
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
        
        # CSV files
        for csv_file in self.data_dir.glob("*.csv"):
            files.append(csv_file.name)
        
        return files 
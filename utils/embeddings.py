"""
Embeddings and Vector Store utilities
"""
import os
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CHUNK_SIZE, CHUNK_OVERLAP, VECTOR_STORE_PATH

class VectorStoreManager:
    """Manages vector store operations"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=['\n\n', '\n', '.', ',', ' '],
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        self.vector_store = None
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """Create a new vector store from documents"""
        try:
            # Split documents
            split_docs = self.text_splitter.split_documents(documents)
            
            # Create vector store
            self.vector_store = FAISS.from_documents(split_docs, self.embeddings)
            return self.vector_store
        except Exception as e:
            raise Exception(f"Error creating vector store: {str(e)}")
    
    def add_documents(self, documents: List[Document]):
        """Add documents to existing vector store"""
        try:
            split_docs = self.text_splitter.split_documents(documents)
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(split_docs, self.embeddings)
            else:
                self.vector_store.add_documents(split_docs)
        except Exception as e:
            raise Exception(f"Error adding documents: {str(e)}")
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents"""
        if self.vector_store is None:
            return []
        try:
            return self.vector_store.similarity_search(query, k=k)
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
    
    def save_local(self, path: str = VECTOR_STORE_PATH):
        """Save vector store locally"""
        if self.vector_store:
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                self.vector_store.save_local(path)
            except Exception as e:
                raise Exception(f"Error saving vector store: {str(e)}")
    
    def load_local(self, path: str = VECTOR_STORE_PATH):
        """Load vector store from local storage"""
        try:
            if os.path.exists(path):
                self.vector_store = FAISS.load_local(
                    path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                return self.vector_store
        except Exception as e:
            print(f"Error loading vector store: {str(e)}")
        return None

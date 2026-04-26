import chromadb
from typing import List, Optional, Dict, Any
import os
from datetime import datetime
import google.generativeai as genai

from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.models_to_try = ["models/text-embedding-004", "models/gemini-embedding-001"]
        self.active_model = self.models_to_try[0]

    def __call__(self, input: Documents) -> Embeddings:
        for model in self.models_to_try:
            try:
                results = genai.embed_content(model=model, content=input, task_type="retrieval_document")
                self.active_model = model
                return results["embedding"]
            except:
                if model == self.models_to_try[-1]: raise
                continue
        return []
        
    def name(self) -> str: return "gemini"

class Memory:
    def __init__(self, persist_path: str = None):
        if persist_path is None: persist_path = os.getenv("ARENA_MEMORY_PATH", ".arena_memory")
        self.client = chromadb.PersistentClient(path=persist_path)
        api_key = os.getenv("GOOGLE_API_KEY")
        self.embedding_fn = GeminiEmbeddingFunction(api_key) if api_key else None
        self.collection = self.client.get_or_create_collection(name="arena_memory", embedding_function=self.embedding_fn)

    async def store(self, task_description, content, metadata=None):
        task_id = str(hash(task_description))[:8]
        timestamp = datetime.now().isoformat()
        self.collection.add(documents=[content], ids=[f"{task_id}_{timestamp}"], metadatas=[{"task_description": task_description, "timestamp": timestamp, **(metadata or {})}])

    async def retrieve(self, query, top_k=3):
        results = self.collection.query(query_texts=[query], n_results=top_k)
        return results["documents"][0] if results and results["documents"] else []

    async def list_all(self, limit=50):
        results = self.collection.get(limit=limit)
        return [{"id": results["ids"][i], "task_description": results["metadatas"][i].get("task_description", ""), "content": results["documents"][i][:500]} for i in range(len(results["documents"]))] if results else []

    async def clear(self):
        try: self.client.delete_collection("arena_memory")
        except: pass
        self.collection = self.client.get_or_create_collection(name="arena_memory", embedding_function=self.embedding_fn)

memory = Memory()

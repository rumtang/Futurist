"""Vector database tools for Pinecone integration."""

import os
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime
import json
from loguru import logger
import openai
from openai import OpenAI

try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logger.warning("Pinecone not installed - vector search disabled")

from src.config.base_config import settings


class PineconeManager:
    """Manages Pinecone vector database operations."""
    
    def __init__(self):
        self.pc = None
        self.index = None
        self.dimension = settings.pinecone_dimension
        self.client = OpenAI(api_key=settings.openai_api_key)
        
    async def initialize(self):
        """Initialize Pinecone connection."""
        try:
            # Check if Pinecone is available
            if not PINECONE_AVAILABLE:
                raise ImportError("Pinecone library not installed")
                
            # Check if API key is configured
            if not settings.pinecone_api_key or settings.pinecone_api_key == "your-pinecone-api-key":
                raise ValueError("Pinecone API key not configured")
            
            # Initialize Pinecone
            self.pc = Pinecone(api_key=settings.pinecone_api_key)
            
            # Create index if it doesn't exist
            index_name = settings.pinecone_index_name
            
            if not index_name or index_name == "cx-futurist":
                raise ValueError("Pinecone index name not properly configured")
            
            if index_name not in self.pc.list_indexes().names():
                logger.info(f"Creating Pinecone index: {index_name}")
                self.pc.create_index(
                    name=index_name,
                    dimension=self.dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=settings.pinecone_environment
                    )
                )
                
                # Wait for index to be ready
                await asyncio.sleep(10)
            
            # Connect to index
            self.index = self.pc.Index(index_name)
            logger.info(f"Connected to Pinecone index: {index_name}")
            
            # Get index stats
            stats = self.index.describe_index_stats()
            logger.info(f"Index stats: {stats}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise
    
    async def close(self):
        """Close Pinecone connections."""
        # Pinecone client doesn't need explicit closing
        logger.info("Pinecone connections closed")
    
    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding using OpenAI."""
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            raise
    
    async def upsert_documents(self, documents: List[Dict[str, Any]], namespace: str = "") -> Dict[str, Any]:
        """Upsert documents to Pinecone."""
        if not self.index:
            logger.warning("Pinecone not initialized - skipping document upsert")
            return {
                "success": False,
                "error": "Vector database not available"
            }
        
        try:
            vectors = []
            
            for doc in documents:
                # Create embedding
                embedding = await self.create_embedding(doc["content"])
                
                # Prepare vector data
                vector_data = {
                    "id": doc["id"],
                    "values": embedding,
                    "metadata": {
                        "content": doc["content"][:1000],  # Truncate for metadata
                        "title": doc.get("title", ""),
                        "source": doc.get("source", ""),
                        "category": doc.get("category", "general"),
                        "timestamp": doc.get("timestamp", datetime.now().isoformat()),
                        "type": doc.get("type", "document")
                    }
                }
                
                vectors.append(vector_data)
            
            # Upsert in batches
            batch_size = 100
            upserted_count = 0
            
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch, namespace=namespace)
                upserted_count += len(batch)
                logger.info(f"Upserted {upserted_count}/{len(vectors)} vectors")
            
            return {
                "success": True,
                "upserted_count": upserted_count,
                "namespace": namespace
            }
            
        except Exception as e:
            logger.error(f"Error upserting documents: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search(self, 
                    query: str, 
                    top_k: int = 10, 
                    namespace: str = "",
                    filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        if not self.index:
            logger.warning("Pinecone not initialized - returning empty search results")
            return []
        
        try:
            # Create query embedding
            query_embedding = await self.create_embedding(query)
            
            # Search
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                include_metadata=True,
                filter=filter
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    async def delete_vectors(self, ids: List[str], namespace: str = "") -> bool:
        """Delete vectors by IDs."""
        if not self.index:
            logger.warning("Pinecone not initialized - skipping vector deletion")
            return False
        
        try:
            self.index.delete(ids=ids, namespace=namespace)
            logger.info(f"Deleted {len(ids)} vectors from namespace '{namespace}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return False
    
    async def update_metadata(self, id: str, metadata: Dict[str, Any], namespace: str = "") -> bool:
        """Update vector metadata."""
        if not self.index:
            logger.warning("Pinecone not initialized - skipping metadata update")
            return False
        
        try:
            # Fetch existing vector
            fetch_response = self.index.fetch(ids=[id], namespace=namespace)
            
            if id in fetch_response.vectors:
                vector = fetch_response.vectors[id]
                
                # Update metadata
                updated_metadata = {**vector.metadata, **metadata}
                
                # Re-upsert with updated metadata
                self.index.upsert(
                    vectors=[{
                        "id": id,
                        "values": vector.values,
                        "metadata": updated_metadata
                    }],
                    namespace=namespace
                )
                
                logger.info(f"Updated metadata for vector {id}")
                return True
            else:
                logger.warning(f"Vector {id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        if not self.index:
            logger.warning("Pinecone not initialized - returning empty stats")
            return {"error": "Vector database not available"}
        
        try:
            return self.index.describe_index_stats()
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}


# Global Pinecone manager instance
pinecone_manager = PineconeManager()


async def initialize_pinecone():
    """Initialize Pinecone for the application."""
    await pinecone_manager.initialize()


async def close_pinecone():
    """Close Pinecone connections."""
    await pinecone_manager.close()


# Convenience functions
async def store_insight(insight: Dict[str, Any]) -> bool:
    """Store an insight in the vector database."""
    try:
        document = {
            "id": f"insight_{insight.get('id', datetime.now().timestamp())}",
            "content": insight["content"],
            "title": insight.get("title", "Insight"),
            "source": insight.get("agent", "unknown"),
            "category": "insight",
            "type": "insight",
            "timestamp": insight.get("timestamp", datetime.now().isoformat())
        }
        
        result = await pinecone_manager.upsert_documents([document], namespace="insights")
        return result["success"]
        
    except Exception as e:
        logger.error(f"Error storing insight: {e}")
        return False


async def store_trend(trend: Dict[str, Any]) -> bool:
    """Store a trend in the vector database."""
    try:
        document = {
            "id": f"trend_{trend.get('id', datetime.now().timestamp())}",
            "content": f"{trend['name']}: {trend.get('description', '')}",
            "title": trend["name"],
            "source": trend.get("source", "trend_scanner"),
            "category": trend.get("category", "general"),
            "type": "trend",
            "timestamp": trend.get("timestamp", datetime.now().isoformat())
        }
        
        result = await pinecone_manager.upsert_documents([document], namespace="trends")
        return result["success"]
        
    except Exception as e:
        logger.error(f"Error storing trend: {e}")
        return False


async def search_insights(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for insights."""
    return await pinecone_manager.search(query, top_k=limit, namespace="insights")


async def search_trends(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for trends."""
    return await pinecone_manager.search(query, top_k=limit, namespace="trends")


async def search_all(query: str, limit: int = 20) -> Dict[str, List[Dict[str, Any]]]:
    """Search across all namespaces."""
    results = {
        "insights": await search_insights(query, limit=limit//2),
        "trends": await search_trends(query, limit=limit//2),
        "documents": await pinecone_manager.search(query, top_k=limit//2, namespace="")
    }
    return results
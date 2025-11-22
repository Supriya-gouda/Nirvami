"""RAG (Retrieval-Augmented Generation) service for context-aware responses."""
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """Service for retrieving relevant context and building prompts."""
    
    def __init__(self, supabase_client, model_manager):
        self.supabase = supabase_client
        self.model_manager = model_manager
    
    async def retrieve_context(
        self,
        query: str,
        query_embedding: List[float],
        dosha_type: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Retrieve relevant Ayurvedic resources using vector similarity.
        
        Args:
            query: User's question/message
            query_embedding: Embedding vector for the query
            dosha_type: User's dosha type for filtering
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents
        """
        try:
            # Build query
            rpc_query = self.supabase.rpc(
                "match_ayurveda_resources",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.5,
                    "match_count": top_k
                }
            )
            
            # Filter by dosha if provided
            if dosha_type:
                # Note: This requires a custom RPC function in Supabase
                # For now, we'll fetch and filter
                result = rpc_query.execute()
                if result.data:
                    # Filter by dosha tags
                    filtered = [
                        doc for doc in result.data
                        if dosha_type in (doc.get("dosha_tags") or [])
                    ]
                    return filtered[:top_k] if filtered else result.data[:top_k]
                return []
            else:
                result = rpc_query.execute()
                return result.data if result.data else []
        
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            # Return empty list on error, don't fail the whole request
            return []
    
    def build_prompt(
        self,
        user_message: str,
        context_docs: List[Dict],
        user_profile: Dict,
        emotion_data: Dict
    ) -> str:
        """
        Build a comprehensive prompt for the LLM.
        
        Args:
            user_message: User's current message
            context_docs: Retrieved context documents
            user_profile: User profile information
            emotion_data: Detected emotion information
            
        Returns:
            Formatted prompt string
        """
        # Extract relevant info
        dosha_type = user_profile.get("dosha_type", "unknown")
        user_name = user_profile.get("full_name", "there")
        emotion = emotion_data.get("dominant_emotion", "neutral")
        
        # Build context string
        context_str = ""
        if context_docs:
            context_str = "\n\n".join([
                f"Resource: {doc.get('title', 'Untitled')}\n{doc.get('content', '')}"
                for doc in context_docs
            ])
        
        # Build prompt
        prompt = f"""You are Nirvami, an AI wellness assistant specializing in Ayurvedic principles and mental health support.

User Profile:
- Name: {user_name}
- Dosha Type: {dosha_type}
- Current Emotion: {emotion}

Relevant Ayurvedic Knowledge:
{context_str if context_str else "No specific resources retrieved."}

User's Message: {user_message}

Instructions:
1. Provide compassionate, personalized guidance based on their dosha type
2. Acknowledge their emotional state if relevant
3. Offer practical, actionable Ayurvedic recommendations
4. Be warm, supportive, and non-judgmental
5. Keep responses concise (2-3 paragraphs)
6. If suggesting practices, explain how they benefit their specific dosha

Response:"""
        
        return prompt
    
    async def get_dosha_specific_recommendations(
        self,
        dosha_type: str,
        category: str = "lifestyle"
    ) -> List[Dict]:
        """
        Get dosha-specific recommendations.
        
        Args:
            dosha_type: User's dosha type
            category: Category of recommendations (diet, yoga, meditation, lifestyle)
            
        Returns:
            List of recommendations
        """
        try:
            result = self.supabase.table("ayurveda_resources").select("*").contains(
                "dosha_tags", [dosha_type]
            ).eq("category", category).limit(5).execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching dosha recommendations: {e}")
            return []

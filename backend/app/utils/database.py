"""Supabase database client and utilities."""
from supabase import create_client, Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Singleton Supabase client manager."""
    
    _instance: Client = None
    _service_client: Client = None
    
    @classmethod
    def get_client(cls, use_service_role: bool = False) -> Client:
        """
        Get Supabase client instance.
        
        Args:
            use_service_role: If True, use service role key (bypasses RLS)
        """
        if use_service_role:
            if cls._service_client is None:
                cls._service_client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_SERVICE_ROLE_KEY
                )
                logger.info("Supabase service role client initialized")
            return cls._service_client
        else:
            if cls._instance is None:
                cls._instance = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
                logger.info("Supabase client initialized")
            return cls._instance


def get_supabase(use_service_role: bool = False) -> Client:
    """Dependency function to get Supabase client."""
    return SupabaseClient.get_client(use_service_role)

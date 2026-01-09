"""Media routes for serving audio files and other media content."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Path to songs directory
SONGS_DIR = Path(__file__).parent.parent.parent.parent / "songs"

# List of available music files
AVAILABLE_MUSIC = [
    "30 Minute Deep Meditation Music Relax Mind Body Healing Music 432Hz Positive Energy Music 57344.mp3",
    "beautiful-dream-piano-146718.mp3",
    "bliss-146707.mp3",
    "calm-beach-meditation-247449.mp3",
    "embrace-14593.mp3",
    "just-relax-11157.mp3",
    "meditation-healing-248683.mp3",
    "piano-moment-9835.mp3",
    "relaxing-145038.mp3",
    "slow-motion-191583.mp3",
    "tender-142833.mp3",
    "the-beat-of-nature-122841.mp3",
    "white-dwarf-261405.mp3"
]


@router.get("/music/{filename}")
async def get_music_file(filename: str):
    """Serve a music file with proper MIME type and CORS."""
    try:
        # Validate filename
        if filename not in AVAILABLE_MUSIC:
            logger.warning(f"❌ Requested music file not found: {filename}")
            raise HTTPException(status_code=404, detail=f"Music file not found: {filename}")
        
        file_path = SONGS_DIR / filename
        
        if not file_path.exists():
            logger.error(f"❌ Music file exists in list but not on disk: {file_path}")
            raise HTTPException(status_code=404, detail=f"Music file not found on disk: {filename}")
        
        logger.info(f"🎵 Serving music file: {filename}")
        
        # Return file with proper MIME type for streaming
        return FileResponse(
            path=file_path,
            media_type="audio/mpeg",
            headers={
                "Accept-Ranges": "bytes",
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error serving music file {filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error serving music file: {str(e)}")


@router.get("/music")
async def list_available_music():
    """List all available music files."""
    try:
        # Check which files actually exist
        available = []
        for filename in AVAILABLE_MUSIC:
            file_path = SONGS_DIR / filename
            if file_path.exists():
                file_size = file_path.stat().st_size
                available.append({
                    "filename": filename,
                    "size_bytes": file_size,
                    "url": f"/api/v1/media/music/{filename}"
                })
        
        return {
            "success": True,
            "count": len(available),
            "music": available
        }
        
    except Exception as e:
        logger.error(f"❌ Error listing music files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing music files: {str(e)}")

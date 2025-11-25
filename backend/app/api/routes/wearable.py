"""Wearable device integration routes."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from app.utils.auth import get_current_user_id
from app.services.wearable_service import WearableService
from app.services.wearable_health_analyzer import WearableHealthAnalyzer
from app.models.schemas import WearableIntakeRequest, ManualEntryRequest, WearableSnapshot
from datetime import date, datetime
from typing import Optional
import logging
import xml.etree.ElementTree as ET
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()


async def run_health_analysis(user_id: str, snapshot_data: dict):
    """Wrapper to run health analysis in background."""
    try:
        await WearableHealthAnalyzer.analyze_and_alert(user_id, snapshot_data)
    except Exception as e:
        logger.error(f"Error in background health analysis: {e}", exc_info=True)


@router.post("/intake")
async def ingest_watch_data(
    data: WearableIntakeRequest,
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Ingest data from a smartwatch (Apple Watch, Fitbit, etc.).
    
    Expected payload:
    {
        "provider": "apple_watch",
        "captured_at": "2025-11-24T06:30:00Z",
        "heart_rate": 78,
        "hrv_ms": 65,
        "steps": 4500,
        "sleep_hours": 7.2,
        "stress_level": 4,
        "calories_burned": 320
    }
    """
    try:
        result = WearableService.ingest_watch_data(
            user_id=current_user_id,
            data=data.dict(exclude_none=True)
        )
        
        # Schedule background task for health analysis
        background_tasks.add_task(run_health_analysis, current_user_id, result)
        
        return {
            "success": True,
            "message": "Watch data ingested successfully. Health analysis in progress.",
            "snapshot": result
        }
        
    except Exception as e:
        logger.error(f"Error ingesting watch data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/manual-entry")
async def ingest_manual_entry(
    data: ManualEntryRequest,
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Ingest manually entered health data and analyze for anomalies.
    
    Expected payload:
    {
        "date": "2025-11-23",
        "sleep_hours": 6.5,
        "avg_heart_rate": 85,
        "steps": 3200,
        "stress_level": 7
    }
    """
    try:
        result = WearableService.ingest_manual_entry(
            user_id=current_user_id,
            data=data.dict(exclude_none=True)
        )
        
        # Schedule background task for health analysis
        background_tasks.add_task(run_health_analysis, current_user_id, result)
        
        # Aggregate daily stats for the entry date
        try:
            from datetime import date as date_class
            entry_date_str = data.date
            target_date = date_class.fromisoformat(entry_date_str)
            WearableService.aggregate_daily_stats(
                user_id=current_user_id,
                target_date=target_date
            )
            logger.info(f"Aggregated daily stats for manual entry on {entry_date_str}")
        except Exception as agg_error:
            logger.error(f"Failed to aggregate stats for manual entry: {agg_error}")
        
        return {
            "success": True,
            "message": "Manual entry saved successfully. Health analysis in progress.",
            "snapshot": result
        }
        
    except Exception as e:
        logger.error(f"Error saving manual entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/aggregate-daily")
async def aggregate_daily_stats(
    target_date: Optional[str] = None,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Manually trigger daily stats aggregation for a specific date.
    
    Query params:
        target_date: Date in ISO format (default: yesterday)
    """
    try:
        if target_date:
            date_obj = date.fromisoformat(target_date)
        else:
            date_obj = None
        
        result = WearableService.aggregate_daily_stats(
            user_id=current_user_id,
            target_date=date_obj
        )
        
        return {
            "success": True,
            "message": "Daily stats aggregated successfully",
            "stats": result
        }
        
    except Exception as e:
        logger.error(f"Error aggregating daily stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest-summary")
async def get_latest_wearable_summary(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get the latest wearable summary from daily stats.
    Returns the most recent data from either XML upload or manual entry.
    """
    from app.utils.database import get_supabase
    supabase = get_supabase()
    
    try:
        # Get the most recent daily stats entry
        result = supabase.table("wearable_daily_stats").select("*").eq(
            "user_id", current_user_id
        ).order("date", desc=True).limit(1).execute()
        
        if not result.data or len(result.data) == 0:
            return {
                "hasData": False,
                "heartRate": None,
                "hrv": None,
                "sleepHours": None,
                "steps": None,
                "stressLevel": None,
                "lastSynced": None,
                "source": None
            }
        
        stats = result.data[0]
        
        return {
            "hasData": True,
            "heartRate": stats.get("avg_heart_rate"),
            "hrv": stats.get("avg_hrv_ms"),
            "sleepHours": stats.get("sleep_hours"),
            "steps": stats.get("total_steps"),
            "stressLevel": stats.get("avg_stress_level"),
            "lastSynced": stats.get("updated_at") or stats.get("created_at"),
            "source": stats.get("data_source", "unknown"),
            "date": stats.get("date")
        }
        
    except Exception as e:
        logger.error(f"Error fetching latest wearable summary: {e}")
        return {
            "hasData": False,
            "heartRate": None,
            "hrv": None,
            "sleepHours": None,
            "steps": None,
            "stressLevel": None,
            "lastSynced": None,
            "source": None
        }


@router.get("/latest")
async def get_latest_wearable(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get latest wearable snapshot for the user (backward compatibility)."""
    from app.utils.database import get_supabase
    supabase = get_supabase()
    
    try:
        result = supabase.table("wearable_snapshots").select("*").eq(
            "user_id", current_user_id
        ).order("captured_at", desc=True).limit(1).execute()
        
        if result.data:
            return result.data[0]
        else:
            return None
    except Exception as e:
        logger.error(f"Error getting wearable data: {e}")
        return None


@router.post("/sync")
async def sync_wearable_data(
    data: dict,
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id)
):
    """Sync wearable data from device and analyze for health anomalies."""
    try:
        # Map frontend format to backend format
        mapped_data = {
            "provider": data.get("device_type", "unknown"),
            "captured_at": data.get("recorded_at") or datetime.now().isoformat(),
            "heart_rate": data.get("heart_rate"),
            "hrv_ms": int(data.get("hrv") * 1000) if data.get("hrv") else None,  # Convert to ms
            "steps": data.get("steps"),
            "sleep_hours": data.get("sleep_hours"),
            "stress_level": _convert_stress_to_numeric(data.get("stress_level")),
            "active_calories": data.get("active_calories")  # Use legacy field
        }
        
        result = WearableService.ingest_watch_data(
            user_id=current_user_id,
            data=mapped_data
        )
        
        # Schedule background task for health analysis
        background_tasks.add_task(
            WearableHealthAnalyzer.analyze_and_alert,
            current_user_id,
            result
        )
        
        logger.info(f"✅ Wearable data synced for user {current_user_id}")
        return {"success": True, "data": result, "message": "Data synced. Health analysis in progress."}
        
    except Exception as e:
        logger.error(f"❌ Error syncing wearable data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/push")
async def push_wearable_data(
    data: dict,
    current_user_id: str = Depends(get_current_user_id)
):
    """Push wearable data from device (backward compatibility - routes to /sync)."""
    return await sync_wearable_data(data, current_user_id)


def _convert_stress_to_numeric(stress_input: Optional[int | str]) -> Optional[int]:
    """Convert legacy stress levels to numeric (1-10)."""
    if stress_input is None:
        return None
    # If already an integer, return it
    if isinstance(stress_input, int):
        return stress_input
    # Convert string to numeric
    stress_map = {"low": 3, "moderate": 6, "high": 9}
    return stress_map.get(str(stress_input).lower(), 5)


@router.post("/upload-xml")
async def upload_wearable_xml(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Upload Apple Health XML export to sync wearable data.
    
    Uses a three-step process:
    1. Parse XML and extract health metrics
    2. Convert to standardized snapshot format
    3. Store in database and aggregate daily stats
    """
    from app.services.apple_health_parser import AppleHealthParser
    from app.services.apple_health_storage import AppleHealthStorage
    
    try:
        # Validate file is XML
        if not file.filename.endswith('.xml'):
            raise HTTPException(status_code=400, detail="File must be an XML file")
        
        logger.info(f"📤 Processing XML upload: {file.filename} for user {current_user_id}")
        
        # Step 1: Read XML content
        content = await file.read()
        logger.info(f"✅ Read {len(content)} bytes from XML file")
        
        # Decode content
        if isinstance(content, bytes):
            content_str = content.decode('utf-8')
        else:
            content_str = content
        
        # Step 2: Parse XML and extract health data
        logger.info("🔍 Parsing Apple Health XML...")
        parse_result = AppleHealthParser.parse_xml_file(content_str)
        
        if not parse_result['success']:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse XML: {parse_result.get('error', 'Unknown error')}"
            )
        
        daily_data = parse_result['daily_data']
        stats = parse_result['stats']
        
        logger.info(f"✅ Parsed {stats['total_records']} records, found data for {stats['days_with_data']} days")
        logger.info(f"📋 Sample record types: {stats['sample_types'][:5]}")
        
        if not daily_data:
            return {
                "success": False,
                "message": f"No health data extracted from XML. Found {stats['total_records']} records but none contained heart rate, steps, or sleep data.",
                "stats": stats
            }
        
        # Step 3: Convert to snapshots
        logger.info("🔄 Converting to snapshot format...")
        snapshots = AppleHealthParser.convert_to_snapshots(daily_data, current_user_id)
        
        if not snapshots:
            return {
                "success": False,
                "message": "No valid snapshots created from parsed data",
                "stats": stats
            }
        
        logger.info(f"✅ Created {len(snapshots)} snapshots")
        
        # Step 4: Save to database
        logger.info("💾 Saving snapshots to database...")
        save_result = AppleHealthStorage.save_snapshots(snapshots)
        
        if not save_result['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save data: {save_result['message']}"
            )
        
        logger.info(f"✅ Saved {save_result['saved_count']} snapshots to database")
        
        # Step 5: Aggregate daily statistics
        logger.info("📊 Aggregating daily statistics...")
        dates = list(daily_data.keys())
        agg_result = AppleHealthStorage.aggregate_daily_stats(current_user_id, dates)
        
        logger.info(f"✅ Aggregated stats for {agg_result['aggregated_count']} days")
        
        # Step 6: Schedule health analysis for recent data
        if snapshots:
            # Analyze most recent snapshot
            latest_snapshot = max(snapshots, key=lambda s: s['captured_at'])
            background_tasks.add_task(run_health_analysis, current_user_id, latest_snapshot)
        
        # Return success response
        date_range = {
            'start': min(dates) if dates else None,
            'end': max(dates) if dates else None
        }
        
        return {
            "success": True,
            "message": f"✅ Successfully uploaded Apple Health data! Processed {save_result['saved_count']} days of health data.",
            "stats": {
                "total_records": stats['total_records'],
                "days_processed": len(dates),
                "snapshots_saved": save_result['saved_count'],
                "snapshots_failed": save_result['failed_count'],
                "stats_aggregated": agg_result['aggregated_count'],
                "date_range": date_range
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error uploading wearable XML: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process XML file: {str(e)}")

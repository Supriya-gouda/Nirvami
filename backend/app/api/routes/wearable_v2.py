"""Clean Wearable API Routes - Simplified version."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.utils.auth import get_current_user_id
from app.services.wearable_service_v2 import WearableService
from app.services.alert_service import AlertService
from app.utils.database import get_supabase
from pydantic import BaseModel
from typing import Optional
import logging
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


class ManualEntryRequest(BaseModel):
    """Manual health entry from frontend."""
    date: str
    sleep_hours: Optional[float] = None
    avg_heart_rate: Optional[int] = None
    steps: Optional[int] = None
    stress_level: Optional[int] = None
    calories_burned: Optional[float] = None
    hrv_ms: Optional[int] = None


@router.post("/manual-entry")
async def save_manual_entry(
    data: ManualEntryRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Save manually entered health data."""
    try:
        logger.info(f"📝 Manual entry from user {current_user_id}: {data.dict()}")
        
        result = WearableService.save_manual_entry(
            user_id=current_user_id,
            data=data.dict(exclude_none=True)
        )
        
        return {
            "success": True,
            "message": "Health data saved successfully!",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ Error saving manual entry: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest")
async def get_latest_entry(
    current_user_id: str = Depends(get_current_user_id)
):
    """Get the most recent wearable entry."""
    try:
        latest = WearableService.get_latest(current_user_id)
        
        if not latest:
            return {
                "hasData": False,
                "message": "No wearable data found"
            }
        
        return {
            "hasData": True,
            "data": latest,
            "sleepHours": latest.get("sleep_hours"),
            "heartRate": latest.get("avg_heart_rate"),
            "steps": latest.get("steps"),
            "stressLevel": latest.get("stress_level"),
            "caloriesBurned": latest.get("calories_burned"),
            "date": latest.get("date"),
            "source": latest.get("source")
        }
        
    except Exception as e:
        logger.error(f"Error fetching latest wearable: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history(
    limit: int = 30,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get wearable history for a user."""
    try:
        history = WearableService.get_all_for_user(current_user_id, limit=limit)
        return {"data": history, "count": len(history)}
        
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_health(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Analyze wearable data for health risks and send notifications.
    
    Returns analysis results and creates in-app notification + SMS if needed.
    """
    try:
        logger.info(f"🔍 Analyzing health data for user {current_user_id}")
        
        # Perform analysis
        analysis = WearableService.analyze_health_risks(current_user_id)
        
        if not analysis["has_risks"]:
            return {
                "success": True,
                "message": "✅ No health risks detected! Keep up the good work!",
                "analysis": analysis
            }
        
        # Create in-app notification using AlertService
        supabase = get_supabase(use_service_role=True)
        
        risk_emoji = {
            "low": "ℹ️",
            "medium": "⚠️",
            "high": "🚨",
            "critical": "🆘"
        }
        
        notification_title = f"{risk_emoji.get(analysis['risk_level'], '📊')} Health Analysis Alert"
        notification_body = f"{len(analysis['risks'])} health concern(s) detected:\n\n" + "\n".join(analysis['risks'][:3])
        
        # Create notification using AlertService
        try:
            notification_type = "warning" if analysis['risk_level'] in ["high", "critical"] else "info"
            await AlertService.create_in_app_notification(
                supabase=supabase,
                user_id=current_user_id,
                title=notification_title,
                body=notification_body,
                notification_type=notification_type,
                action_url="/device"
            )
            logger.info(f"✅ Created in-app notification for user {current_user_id}")
            
        except Exception as notif_error:
            logger.error(f"Failed to create notification: {notif_error}")
        
        # Send SMS notification for ALL analysis completions (not just critical)
        try:
            # Get user profile with phone number
            profile = supabase.table("profiles").select("phone_number").eq("id", current_user_id).single().execute()
            
            if profile.data and profile.data.get("phone_number"):
                phone = profile.data["phone_number"]
                
                # Create SMS message based on risk level
                if analysis['has_risks']:
                    risk_summary = analysis['risks'][0] if analysis['risks'] else "Health analysis completed"
                    sms_message = f"🏥 Nirvami Health Alert: {risk_summary}. Check the app for detailed recommendations."
                else:
                    sms_message = "✅ Nirvami: Your health analysis is complete. No concerns detected. Great job!"
                
                await AlertService.send_sms_alert(
                    to_phone=phone,
                    message=sms_message
                )
                
                logger.info(f"📱 Sent SMS notification to user {current_user_id} at {phone}")
            else:
                logger.info(f"ℹ️ No phone number found for user {current_user_id}, skipping SMS")
                
        except Exception as sms_error:
            logger.error(f"Failed to send SMS: {sms_error}", exc_info=True)
        
        return {
            "success": True,
            "message": f"Analysis complete. {len(analysis['risks'])} risk(s) detected.",
            "analysis": analysis,
            "notification_sent": True
        }
        
    except Exception as e:
        logger.error(f"❌ Error analyzing health: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-xml")
async def upload_xml_and_analyze(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Upload Apple Watch XML export and analyze health data.
    
    Complete pipeline:
    1. Parse XML to extract ALL metrics (HR, steps, sleep, calories, HRV)
    2. Aggregate raw records into daily snapshots
    3. Store in wearable_snapshots table (same as manual entry)
    4. Run the SAME analysis logic as manual "Analyze" button
    5. Return analysis results + recommendations
    """
    from app.services.apple_health_xml_parser import AppleHealthXMLParser
    
    try:
        logger.info(f"📤 XML upload from user {current_user_id}: {file.filename}")
        
        # Validate file
        if not file.filename or not file.filename.endswith('.xml'):
            raise HTTPException(status_code=400, detail="File must be an XML file")
        
        # Read XML content
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")
        
        xml_str = content.decode('utf-8') if isinstance(content, bytes) else content
        
        # Parse XML using comprehensive parser
        logger.info("🔍 Parsing Apple Health XML...")
        parse_result = AppleHealthXMLParser.parse_xml(xml_str)
        
        if not parse_result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse XML: {parse_result.get('error', 'Unknown error')}"
            )
        
        daily_snapshots = parse_result["daily_snapshots"]
        stats = parse_result["stats"]
        
        if not daily_snapshots:
            return {
                "success": False,
                "message": "No health data found in XML file. The file may not contain heart rate, steps, or sleep data.",
                "records_parsed": stats["total_records"],
                "stats": stats
            }
        
        logger.info(f"✅ Extracted {len(daily_snapshots)} daily snapshots from {stats['total_records']} raw records")
        
        # Save ALL daily snapshots to database (same as manual entry)
        saved_count = 0
        failed_count = 0
        
        for snapshot in daily_snapshots:
            try:
                # Add user_id
                snapshot["user_id"] = current_user_id
                
                # Save using the SAME method as manual entry, but with 'watch' source
                WearableService.save_manual_entry(
                    user_id=current_user_id,
                    data=snapshot,
                    source="watch"  # Override source to 'watch' for XML uploads
                )
                saved_count += 1
                
            except Exception as save_error:
                logger.error(f"Failed to save snapshot for {snapshot['date']}: {save_error}")
                failed_count += 1
        
        logger.info(f"💾 Saved {saved_count}/{len(daily_snapshots)} snapshots to database")
        
        # Run the SAME analysis as the manual "Analyze" button
        logger.info("🔍 Running health analysis on latest data...")
        analysis = WearableService.analyze_health_risks(current_user_id)
        
        # Create notification if risks found (same as analyze endpoint)
        supabase = get_supabase(use_service_role=True)
        
        if analysis["has_risks"]:
            risk_emoji = {
                "low": "ℹ️",
                "medium": "⚠️",
                "high": "🚨",
                "critical": "🆘"
            }
            
            notification_title = f"{risk_emoji.get(analysis['risk_level'], '📊')} Health Analysis Alert"
            notification_body = f"{len(analysis['risks'])} health concern(s) detected from Apple Watch data:\n\n" + "\n".join(analysis['risks'][:3])
            
            try:
                notification_type = "warning" if analysis['risk_level'] in ["high", "critical"] else "info"
                await AlertService.create_in_app_notification(
                    supabase=supabase,
                    user_id=current_user_id,
                    title=notification_title,
                    body=notification_body,
                    notification_type=notification_type,
                    action_url="/device"
                )
                logger.info(f"✅ Created in-app notification")
            except Exception as notif_error:
                logger.error(f"Failed to create notification: {notif_error}")
        
        # Send SMS notification for ALL analysis completions from XML upload
        try:
            # Get user profile with phone number
            profile = supabase.table("profiles").select("phone_number").eq("id", current_user_id).single().execute()
            
            if profile.data and profile.data.get("phone_number"):
                phone = profile.data["phone_number"]
                
                # Create SMS message based on analysis results
                if analysis['has_risks']:
                    risk_summary = analysis['risks'][0] if analysis['risks'] else "Health analysis completed"
                    sms_message = f"🏥 Nirvami: Apple Watch data analyzed. {risk_summary}. Check the app for details."
                else:
                    sms_message = f"✅ Nirvami: Apple Watch data analyzed. {saved_count} days processed. No concerns detected!"
                
                await AlertService.send_sms_alert(
                    to_phone=phone,
                    message=sms_message
                )
                
                logger.info(f"📱 Sent SMS notification to user {current_user_id} at {phone}")
            else:
                logger.info(f"ℹ️ No phone number found for user {current_user_id}, skipping SMS")
                
        except Exception as sms_error:
            logger.error(f"Failed to send SMS notification: {sms_error}", exc_info=True)
        
        # Get latest snapshot for display
        latest_snapshot = daily_snapshots[-1] if daily_snapshots else {}
        
        return {
            "success": True,
            "message": f"✅ Successfully uploaded and analyzed Apple Watch data! Processed {saved_count} days of health data.",
            "records_parsed": stats["total_records"],
            "days_processed": saved_count,
            "snapshots_created": saved_count,
            "snapshots_failed": failed_count,
            "latest_metrics": {
                "avg_heart_rate": latest_snapshot.get("avg_heart_rate"),
                "steps": latest_snapshot.get("steps"),
                "sleep_hours": latest_snapshot.get("sleep_hours"),
                "calories_burned": latest_snapshot.get("calories_burned"),
                "hrv_ms": latest_snapshot.get("hrv_ms"),
                "stress_level": latest_snapshot.get("stress_level")
            },
            "stats": stats,
            "analysis": analysis,
            "date_range": {
                "start": daily_snapshots[0]["date"] if daily_snapshots else None,
                "end": daily_snapshots[-1]["date"] if daily_snapshots else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing XML: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process XML: {str(e)}")

"""Seed practice content with YouTube videos and detailed instructions."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from supabase import create_client
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Practice content with YouTube videos and TTS instructions
PRACTICE_CONTENT = [
    # YOGA POSES
    {
        "practice_type": "yoga",
        "practice_name": "Child's Pose",
        "sanskrit_name": "Balasana",
        "description": "A restful pose that gently stretches the lower back, hips, thighs, and ankles while calming the mind.",
        "benefits": ["Releases tension", "Calms nervous system", "Gentle stretch", "Reduces stress"],
        "difficulty": "beginner",
        "duration_min": 1,
        "duration_max": 5,
        "youtube_video_id": "2ↂ5vx-T1u-0",  # "Child's Pose Tutorial" by Yoga With Adriene
        "youtube_title": "Child's Pose - Yoga With Adriene",
        "avatar_animation_steps": [
            {"step": 1, "action": "kneel", "duration": 2},
            {"step": 2, "action": "sit_on_heels", "duration": 2},
            {"step": 3, "action": "fold_forward", "duration": 3},
            {"step": 4, "action": "extend_arms", "duration": 2},
            {"step": 5, "action": "breathe_deeply", "duration": 5}
        ],
        "tts_instructions": [
            "Begin by kneeling on your mat with your knees hip-width apart.",
            "Sit back on your heels and take a deep breath.",
            "Exhale and fold forward, bringing your forehead to the mat.",
            "Extend your arms forward or rest them alongside your body.",
            "Breathe deeply and relax for one to five minutes."
        ],
        "dosha_tags": ["vata", "pitta"],
        "emotion_tags": ["anxious", "stressed", "overwhelmed"],
        "category": "restorative",
        "icon": "🙏"
    },
    {
        "practice_type": "yoga",
        "practice_name": "Tree Pose",
        "sanskrit_name": "Vrksasana",
        "description": "A balancing pose that improves focus, strengthens legs, and grounds scattered energy.",
        "benefits": ["Improves balance", "Strengthens legs", "Calms mind", "Grounds energy"],
        "difficulty": "beginner",
        "duration_min": 1,
        "duration_max": 2,
        "youtube_video_id": "vx8gNW-7Jvg",  # "Tree Pose" by Yoga With Adriene
        "youtube_title": "Tree Pose - Yoga With Adriene",
        "avatar_animation_steps": [
            {"step": 1, "action": "stand_mountain_pose", "duration": 2},
            {"step": 2, "action": "shift_weight_left", "duration": 2},
            {"step": 3, "action": "lift_right_foot", "duration": 3},
            {"step": 4, "action": "place_on_inner_thigh", "duration": 2},
            {"step": 5, "action": "hands_to_prayer", "duration": 2},
            {"step": 6, "action": "balance", "duration": 5}
        ],
        "tts_instructions": [
            "Stand in Mountain Pose with feet together.",
            "Shift your weight onto your left foot.",
            "Bend your right knee and place your right foot on your inner left thigh.",
            "Bring your hands to prayer position at your chest.",
            "Find a focal point and hold for 30 to 60 seconds.",
            "Repeat on the other side."
        ],
        "dosha_tags": ["vata"],
        "emotion_tags": ["anxious", "restless", "scattered"],
        "category": "balancing",
        "icon": "🌳"
    },
    {
        "practice_type": "yoga",
        "practice_name": "Warrior II",
        "sanskrit_name": "Virabhadrasana II",
        "description": "A powerful standing pose that builds strength, stamina, and confidence.",
        "benefits": ["Builds strength", "Increases stamina", "Opens hips", "Energizes"],
        "difficulty": "intermediate",
        "duration_min": 1,
        "duration_max": 2,
        "youtube_video_id": "oqXN8DeCPvU",  # "Warrior II" by Yoga With Adriene
        "youtube_title": "Warrior II - Yoga With Adriene",
        "avatar_animation_steps": [
            {"step": 1, "action": "wide_stance", "duration": 2},
            {"step": 2, "action": "turn_right_foot_out", "duration": 2},
            {"step": 3, "action": "bend_right_knee", "duration": 3},
            {"step": 4, "action": "extend_arms", "duration": 2},
            {"step": 5, "action": "gaze_over_right_hand", "duration": 2},
            {"step": 6, "action": "hold_pose", "duration": 5}
        ],
        "tts_instructions": [
            "Step your feet wide apart, about four feet.",
            "Turn your right foot out 90 degrees and left foot slightly in.",
            "Bend your right knee over your right ankle.",
            "Extend your arms out to the sides at shoulder height.",
            "Gaze over your right fingertips.",
            "Hold for 30 to 60 seconds, then repeat on the left side."
        ],
        "dosha_tags": ["kapha"],
        "emotion_tags": ["tired", "lethargic", "unmotivated"],
        "category": "standing",
        "icon": "⚔️"
    },
    {
        "practice_type": "yoga",
        "practice_name": "Downward Dog",
        "sanskrit_name": "Adho Mukha Svanasana",
        "description": "An energizing inversion that stretches the entire body and builds strength.",
        "benefits": ["Full body stretch", "Energizes", "Strengthens", "Improves circulation"],
        "difficulty": "intermediate",
        "duration_min": 1,
        "duration_max": 3,
        "youtube_video_id": "B0-CqqZQqGQ",  # "Downward Dog" by Yoga With Adriene
        "youtube_title": "Downward Facing Dog - Yoga With Adriene",
        "avatar_animation_steps": [
            {"step": 1, "action": "start_on_hands_and_knees", "duration": 2},
            {"step": 2, "action": "tuck_toes", "duration": 1},
            {"step": 3, "action": "lift_hips_up", "duration": 3},
            {"step": 4, "action": "straighten_legs", "duration": 2},
            {"step": 5, "action": "press_heels_down", "duration": 2},
            {"step": 6, "action": "hold_and_breathe", "duration": 5}
        ],
        "tts_instructions": [
            "Start on your hands and knees in tabletop position.",
            "Tuck your toes under and lift your hips up and back.",
            "Straighten your legs as much as comfortable.",
            "Press your heels toward the floor.",
            "Keep your arms straight and head between your arms.",
            "Hold for one to three minutes."
        ],
        "dosha_tags": ["kapha", "pitta"],
        "emotion_tags": ["tired", "neutral", "energized"],
        "category": "inversion",
        "icon": "🐕"
    },
    {
        "practice_type": "yoga",
        "practice_name": "Corpse Pose",
        "sanskrit_name": "Savasana",
        "description": "The final relaxation pose that allows the body to integrate the practice.",
        "benefits": ["Deep relaxation", "Reduces stress", "Integrates practice", "Calms mind"],
        "difficulty": "beginner",
        "duration_min": 5,
        "duration_max": 15,
        "youtube_video_id": "1ZBWSkJIVDQ",  # "Savasana" guided by Yoga With Adriene
        "youtube_title": "Savasana - Final Relaxation - Yoga With Adriene",
        "avatar_animation_steps": [
            {"step": 1, "action": "lie_on_back", "duration": 3},
            {"step": 2, "action": "legs_apart", "duration": 2},
            {"step": 3, "action": "arms_at_sides", "duration": 2},
            {"step": 4, "action": "palms_up", "duration": 2},
            {"step": 5, "action": "close_eyes", "duration": 1},
            {"step": 6, "action": "breathe_naturally", "duration": 10}
        ],
        "tts_instructions": [
            "Lie flat on your back with your legs extended.",
            "Allow your feet to fall open to the sides.",
            "Rest your arms alongside your body with palms facing up.",
            "Close your eyes gently.",
            "Breathe naturally and let your entire body relax.",
            "Stay in this pose for five to fifteen minutes."
        ],
        "dosha_tags": ["vata", "pitta", "kapha"],
        "emotion_tags": ["stressed", "anxious", "angry", "overwhelmed"],
        "category": "restorative",
        "icon": "😌"
    },
    
    # BREATHING EXERCISES
    {
        "practice_type": "breathing",
        "practice_name": "4-7-8 Breathing",
        "sanskrit_name": None,
        "description": "A calming breathing technique that reduces anxiety and promotes relaxation.",
        "benefits": ["Reduces anxiety", "Promotes sleep", "Lowers stress", "Calms mind"],
        "difficulty": "beginner",
        "duration_min": 2,
        "duration_max": 5,
        "youtube_video_id": "gz4G31LGyog",  # "4-7-8 Breathing" by Dr. Andrew Weil
        "youtube_title": "4-7-8 Breathing Exercise by Dr. Weil",
        "avatar_animation_steps": [
            {"step": 1, "action": "sit_comfortably", "duration": 2},
            {"step": 2, "action": "inhale_4", "duration": 4},
            {"step": 3, "action": "hold_7", "duration": 7},
            {"step": 4, "action": "exhale_8", "duration": 8},
            {"step": 5, "action": "repeat_cycle", "duration": 2}
        ],
        "tts_instructions": [
            "Sit comfortably with your back straight.",
            "Place the tip of your tongue behind your upper front teeth.",
            "Exhale completely through your mouth making a whoosh sound.",
            "Close your mouth and inhale quietly through your nose for a count of four.",
            "Hold your breath for a count of seven.",
            "Exhale completely through your mouth for a count of eight.",
            "Repeat this cycle three to four times."
        ],
        "dosha_tags": ["vata", "pitta"],
        "emotion_tags": ["anxious", "stressed", "overwhelmed"],
        "category": "pranayama",
        "icon": "🌬️"
    },
    {
        "practice_type": "breathing",
        "practice_name": "Alternate Nostril Breathing",
        "sanskrit_name": "Nadi Shodhana",
        "description": "A balancing breath that harmonizes the left and right hemispheres of the brain.",
        "benefits": ["Balances energy", "Calms mind", "Improves focus", "Reduces stress"],
        "difficulty": "intermediate",
        "duration_min": 3,
        "duration_max": 10,
        "youtube_video_id": "8VwufJrUhic",  # "Nadi Shodhana" by Yoga With Adriene
        "youtube_title": "Alternate Nostril Breathing - Nadi Shodhana",
        "avatar_animation_steps": [
            {"step": 1, "action": "sit_comfortably", "duration": 2},
            {"step": 2, "action": "right_hand_position", "duration": 2},
            {"step": 3, "action": "close_right_nostril", "duration": 1},
            {"step": 4, "action": "inhale_left", "duration": 4},
            {"step": 5, "action": "close_left_nostril", "duration": 1},
            {"step": 6, "action": "exhale_right", "duration": 4},
            {"step": 7, "action": "repeat_cycle", "duration": 2}
        ],
        "tts_instructions": [
            "Sit in a comfortable position with your spine straight.",
            "Use your right thumb to close your right nostril.",
            "Inhale slowly through your left nostril.",
            "Close your left nostril with your ring finger.",
            "Release your right nostril and exhale through it.",
            "Inhale through your right nostril.",
            "Close your right nostril and exhale through your left.",
            "Continue this pattern for three to ten minutes."
        ],
        "dosha_tags": ["vata", "pitta", "kapha"],
        "emotion_tags": ["anxious", "scattered", "unbalanced"],
        "category": "pranayama",
        "icon": "🌀"
    },
    
    # MEDITATION
    {
        "practice_type": "meditation",
        "practice_name": "Body Scan Meditation",
        "sanskrit_name": None,
        "description": "A mindfulness practice that systematically relaxes each part of the body.",
        "benefits": ["Releases tension", "Increases awareness", "Promotes relaxation", "Improves sleep"],
        "difficulty": "beginner",
        "duration_min": 10,
        "duration_max": 30,
        "youtube_video_id": "ihO02wUzgkc",  # "Body Scan Meditation" by The Mindful Movement
        "youtube_title": "Body Scan Meditation - The Mindful Movement",
        "avatar_animation_steps": [
            {"step": 1, "action": "lie_down_comfortably", "duration": 3},
            {"step": 2, "action": "close_eyes", "duration": 1},
            {"step": 3, "action": "scan_feet", "duration": 2},
            {"step": 4, "action": "scan_legs", "duration": 2},
            {"step": 5, "action": "scan_torso", "duration": 2},
            {"step": 6, "action": "scan_arms", "duration": 2},
            {"step": 7, "action": "scan_head", "duration": 2}
        ],
        "tts_instructions": [
            "Lie down in a comfortable position on your back.",
            "Close your eyes and take a few deep breaths.",
            "Bring your attention to your toes. Notice any sensations.",
            "Slowly move your awareness up through your feet, ankles, and legs.",
            "Continue scanning through your torso, chest, and shoulders.",
            "Move through your arms, hands, and fingers.",
            "Finally, scan your neck, face, and top of your head.",
            "Take a moment to feel your entire body relaxed."
        ],
        "dosha_tags": ["vata"],
        "emotion_tags": ["anxious", "tense", "restless"],
        "category": "mindfulness",
        "icon": "🧘‍♀️"
    },
    {
        "practice_type": "meditation",
        "practice_name": "Loving-Kindness Meditation",
        "sanskrit_name": "Metta",
        "description": "A practice that cultivates compassion and loving-kindness toward yourself and others.",
        "benefits": ["Increases compassion", "Reduces anger", "Improves relationships", "Boosts happiness"],
        "difficulty": "beginner",
        "duration_min": 10,
        "duration_max": 20,
        "youtube_video_id": "sz7cpV7ERsM",  # "Loving-Kindness Meditation" by UCLA Mindful
        "youtube_title": "Loving-Kindness Meditation - UCLA Mindful",
        "avatar_animation_steps": [
            {"step": 1, "action": "sit_comfortably", "duration": 2},
            {"step": 2, "action": "close_eyes", "duration": 1},
            {"step": 3, "action": "breathe_naturally", "duration": 2},
            {"step": 4, "action": "send_kindness_self", "duration": 3},
            {"step": 5, "action": "send_kindness_loved_one", "duration": 3},
            {"step": 6, "action": "send_kindness_all", "duration": 3}
        ],
        "tts_instructions": [
            "Sit in a comfortable position and close your eyes.",
            "Take a few deep breaths to settle in.",
            "Begin by directing loving-kindness toward yourself.",
            "Silently repeat: May I be happy. May I be healthy. May I be safe. May I live with ease.",
            "Now bring to mind someone you love.",
            "Extend the same wishes to them: May you be happy. May you be healthy.",
            "Gradually extend loving-kindness to all beings everywhere."
        ],
        "dosha_tags": ["pitta"],
        "emotion_tags": ["angry", "frustrated", "sad"],
        "category": "compassion",
        "icon": "❤️"
    }
]


def seed_practice_content():
    """Seed practice content into the database."""
    try:
        logger.info("Starting to seed practice content...")
        
        # Clear existing practice_content (optional)
        # supabase.table("practice_content").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        success_count = 0
        error_count = 0
        
        for content in PRACTICE_CONTENT:
            try:
                # Check if already exists
                existing = supabase.table("practice_content")\
                    .select("id")\
                    .eq("practice_name", content["practice_name"])\
                    .execute()
                
                if existing.data and len(existing.data) > 0:
                    # Update existing
                    result = supabase.table("practice_content")\
                        .update(content)\
                        .eq("practice_name", content["practice_name"])\
                        .execute()
                    logger.info(f"✅ Updated: {content['practice_name']}")
                else:
                    # Insert new
                    result = supabase.table("practice_content").insert(content).execute()
                    logger.info(f"✅ Inserted: {content['practice_name']}")
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"❌ Error with {content['practice_name']}: {e}")
                error_count += 1
        
        logger.info(f"\n✅ Seeding complete!")
        logger.info(f"   Successfully processed: {success_count}")
        logger.info(f"   Errors: {error_count}")
        logger.info(f"   Total practices: {len(PRACTICE_CONTENT)}")
        
    except Exception as e:
        logger.error(f"Fatal error during seeding: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    seed_practice_content()

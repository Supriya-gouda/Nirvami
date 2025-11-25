"""
Seed yoga poses and sound therapy tracks into database.
Run this once to populate the database with personalized content.
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use service role for admin access

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🌟 Seeding Nirvami Database...")

# ============================================
# YOGA POSES DATA
# ============================================

yoga_poses = [
    {
        "name": "Mountain Pose",
        "sanskrit_name": "Tadasana",
        "duration_min": 1,
        "duration_max": 2,
        "difficulty": "beginner",
        "dosha_tags": ["vata", "pitta", "kapha"],  # Good for all
        "emotion_tags": ["anxious", "neutral", "calm"],
        "benefits": ["Improves posture", "Grounds Vata", "Builds focus"],
        "instructions": "Stand with feet together, arms at sides. Distribute weight evenly, engage thighs, lift chest.",
        "icon": "🧘",
        "category": "standing"
    },
    {
        "name": "Tree Pose",
        "sanskrit_name": "Vrksasana",
        "duration_min": 30,
        "duration_max": 60,
        "difficulty": "beginner",
        "dosha_tags": ["vata"],  # Best for Vata
        "emotion_tags": ["anxious", "restless", "scattered"],
        "benefits": ["Improves balance", "Strengthens legs", "Calms mind", "Grounds energy"],
        "instructions": "Stand on one leg, place other foot on inner thigh. Hands in prayer or overhead.",
        "icon": "🌳",
        "category": "balancing"
    },
    {
        "name": "Warrior II",
        "sanskrit_name": "Virabhadrasana II",
        "duration_min": 30,
        "duration_max": 60,
        "difficulty": "intermediate",
        "dosha_tags": ["kapha"],  # Best for Kapha
        "emotion_tags": ["tired", "lethargic", "unmotivated", "sad"],
        "benefits": ["Builds strength", "Increases stamina", "Opens hips", "Energizes"],
        "instructions": "Wide stance, front knee bent 90°, arms extended, gaze over front hand.",
        "icon": "⚔️",
        "category": "standing"
    },
    {
        "name": "Child's Pose",
        "sanskrit_name": "Balasana",
        "duration_min": 1,
        "duration_max": 5,
        "difficulty": "beginner",
        "dosha_tags": ["vata", "pitta"],  # Calming
        "emotion_tags": ["anxious", "stressed", "overwhelmed", "angry"],
        "benefits": ["Releases tension", "Calms nervous system", "Gentle stretch", "Reduces stress"],
        "instructions": "Kneel, sit on heels, fold forward, arms extended or alongside body.",
        "icon": "🙏",
        "category": "restorative"
    },
    {
        "name": "Downward Dog",
        "sanskrit_name": "Adho Mukha Svanasana",
        "duration_min": 1,
        "duration_max": 3,
        "difficulty": "intermediate",
        "dosha_tags": ["kapha", "pitta"],  # Energizing & cooling
        "emotion_tags": ["tired", "neutral", "energized"],
        "benefits": ["Full body stretch", "Energizes", "Strengthens", "Improves circulation"],
        "instructions": "Hands and feet on mat, hips lifted high, forming inverted V shape.",
        "icon": "🐕",
        "category": "inversion"
    },
    {
        "name": "Corpse Pose",
        "sanskrit_name": "Savasana",
        "duration_min": 5,
        "duration_max": 15,
        "difficulty": "beginner",
        "dosha_tags": ["vata", "pitta", "kapha"],  # Essential for all
        "emotion_tags": ["stressed", "anxious", "angry", "overwhelmed"],
        "benefits": ["Deep relaxation", "Reduces stress", "Integrates practice", "Calms mind"],
        "instructions": "Lie on back, arms and legs relaxed, palms up. Close eyes, breathe naturally.",
        "icon": "😌",
        "category": "restorative"
    },
    {
        "name": "Cat-Cow Stretch",
        "sanskrit_name": "Marjaryasana-Bitilasana",
        "duration_min": 2,
        "duration_max": 3,
        "difficulty": "beginner",
        "dosha_tags": ["vata"],  # Gentle movement for Vata
        "emotion_tags": ["stiff", "anxious", "neutral"],
        "benefits": ["Spinal flexibility", "Warms up body", "Relieves back tension"],
        "instructions": "On hands and knees, alternate arching and rounding spine with breath.",
        "icon": "🐱",
        "category": "warm-up"
    },
    {
        "name": "Cobra Pose",
        "sanskrit_name": "Bhujangasana",
        "duration_min": 30,
        "duration_max": 60,
        "difficulty": "beginner",
        "dosha_tags": ["kapha"],  # Heart opening for Kapha
        "emotion_tags": ["sad", "tired", "withdrawn"],
        "benefits": ["Opens chest", "Strengthens back", "Energizes", "Improves mood"],
        "instructions": "Lie on belly, hands under shoulders, lift chest using back muscles.",
        "icon": "🐍",
        "category": "backbend"
    },
    {
        "name": "Forward Bend",
        "sanskrit_name": "Uttanasana",
        "duration_min": 30,
        "duration_max": 90,
        "difficulty": "beginner",
        "dosha_tags": ["pitta"],  # Cooling for Pitta
        "emotion_tags": ["angry", "frustrated", "irritated", "hot"],
        "benefits": ["Calms mind", "Stretches hamstrings", "Cools body", "Reduces tension"],
        "instructions": "Stand, fold forward from hips, let head hang, hold elbows or touch floor.",
        "icon": "🔽",
        "category": "forward-fold"
    },
    {
        "name": "Seated Twist",
        "sanskrit_name": "Ardha Matsyendrasana",
        "duration_min": 30,
        "duration_max": 60,
        "difficulty": "intermediate",
        "dosha_tags": ["pitta", "kapha"],  # Detoxifying
        "emotion_tags": ["angry", "frustrated", "stuck"],
        "benefits": ["Spinal mobility", "Aids digestion", "Detoxifies", "Releases tension"],
        "instructions": "Sit, cross legs, twist torso, use opposite elbow on outside of knee.",
        "icon": "🌀",
        "category": "twist"
    },
    {
        "name": "Legs Up the Wall",
        "sanskrit_name": "Viparita Karani",
        "duration_min": 5,
        "duration_max": 15,
        "difficulty": "beginner",
        "dosha_tags": ["vata", "pitta"],  # Calming and restorative
        "emotion_tags": ["tired", "stressed", "anxious", "overwhelmed"],
        "benefits": ["Relieves tired legs", "Calms nervous system", "Reduces stress", "Improves circulation"],
        "instructions": "Lie on back with legs extended up a wall, arms relaxed at sides, breathe deeply.",
        "icon": "🔄",
        "category": "restorative"
    },
    {
        "name": "Bridge Pose",
        "sanskrit_name": "Setu Bandhasana",
        "duration_min": 30,
        "duration_max": 60,
        "difficulty": "beginner",
        "dosha_tags": ["kapha", "pitta"],  # Energizing backbend
        "emotion_tags": ["sad", "tired", "withdrawn", "low"],
        "benefits": ["Opens chest and heart", "Strengthens back", "Energizes", "Lifts mood"],
        "instructions": "Lie on back, bend knees, lift hips toward ceiling, press through feet.",
        "icon": "🌉",
        "category": "backbend"
    },
    {
        "name": "Triangle Pose",
        "sanskrit_name": "Trikonasana",
        "duration_min": 30,
        "duration_max": 60,
        "difficulty": "beginner",
        "dosha_tags": ["vata", "kapha"],  # Grounding and strengthening
        "emotion_tags": ["scattered", "unfocused", "anxious"],
        "benefits": ["Strengthens legs", "Opens hips and chest", "Improves focus", "Grounds energy"],
        "instructions": "Wide stance, reach one arm down to leg/floor, extend other arm up, gaze at top hand.",
        "icon": "📐",
        "category": "standing"
    },
    {
        "name": "Pigeon Pose",
        "sanskrit_name": "Eka Pada Rajakapotasana",
        "duration_min": 1,
        "duration_max": 5,
        "difficulty": "intermediate",
        "dosha_tags": ["vata", "pitta"],  # Hip opener
        "emotion_tags": ["anxious", "tense", "stuck", "angry"],
        "benefits": ["Opens hips", "Releases emotional tension", "Stretches psoas", "Calms mind"],
        "instructions": "From downward dog, bring one knee forward between hands, extend back leg, fold forward.",
        "icon": "🕊️",
        "category": "hip-opener"
    },
    {
        "name": "Plank Pose",
        "sanskrit_name": "Phalakasana",
        "duration_min": 30,
        "duration_max": 90,
        "difficulty": "intermediate",
        "dosha_tags": ["kapha"],  # Strength building
        "emotion_tags": ["unmotivated", "lethargic", "weak"],
        "benefits": ["Builds core strength", "Tones arms", "Increases stamina", "Energizes"],
        "instructions": "From hands and knees, step feet back, hold body in straight line, engage core.",
        "icon": "💪",
        "category": "strength"
    }
]

# ============================================
# SOUND THERAPY TRACKS DATA
# ============================================

sound_tracks = [
    {
        "title": "Ocean Waves & Tibetan Bowls",
        "duration_minutes": 15,
        "dosha_tags": ["vata"],
        "emotion_tags": ["anxious", "stressed", "restless", "overwhelmed"],
        "frequency_hz": 432,
        "description": "Grounding frequencies to calm Vata imbalance. Deep ocean sounds combined with resonant singing bowls.",
        "mood_category": "calming",
        "icon": "🌊",
        "audio_url": "https://example.com/ocean-bowls.mp3",  # Placeholder
        "thumbnail_gradient": "from-blue-50 to-cyan-50"
    },
    {
        "title": "Forest Rain & Bamboo Flute",
        "duration_minutes": 20,
        "dosha_tags": ["pitta"],
        "emotion_tags": ["angry", "frustrated", "irritated", "hot"],
        "frequency_hz": 528,
        "description": "Cooling sounds to balance Pitta fire. Gentle rain with soothing flute melodies.",
        "mood_category": "cooling",
        "icon": "🌧️",
        "audio_url": "https://example.com/forest-rain.mp3",
        "thumbnail_gradient": "from-green-50 to-emerald-50"
    },
    {
        "title": "Energizing Drum Rhythms",
        "duration_minutes": 12,
        "dosha_tags": ["kapha"],
        "emotion_tags": ["tired", "lethargic", "unmotivated", "sad"],
        "frequency_hz": 639,
        "description": "Uplifting beats to stimulate Kapha energy. Traditional rhythmic drumming patterns.",
        "mood_category": "energizing",
        "icon": "🥁",
        "audio_url": "https://example.com/drum-rhythms.mp3",
        "thumbnail_gradient": "from-orange-50 to-red-50"
    },
    {
        "title": "Himalayan Singing Bowls",
        "duration_minutes": 30,
        "dosha_tags": ["vata", "pitta", "kapha"],  # Universal
        "emotion_tags": ["calm", "meditative", "peaceful", "neutral"],
        "frequency_hz": 528,
        "description": "Universal healing frequency for balance. Pure crystal and metal bowl resonance.",
        "mood_category": "meditative",
        "icon": "🔮",
        "audio_url": "https://example.com/singing-bowls.mp3",
        "thumbnail_gradient": "from-purple-50 to-pink-50"
    },
    {
        "title": "Morning Sunrise Ragas",
        "duration_minutes": 18,
        "dosha_tags": ["kapha"],
        "emotion_tags": ["energized", "motivated", "uplifted", "joyful"],
        "frequency_hz": 396,
        "description": "Traditional Indian ragas to enhance vitality. Sitar and tabla morning melodies.",
        "mood_category": "uplifting",
        "icon": "🎵",
        "audio_url": "https://example.com/morning-ragas.mp3",
        "thumbnail_gradient": "from-amber-50 to-yellow-50"
    },
    {
        "title": "Moonlight Serenity",
        "duration_minutes": 25,
        "dosha_tags": ["pitta"],
        "emotion_tags": ["calm", "relaxed", "peaceful", "sleepy"],
        "frequency_hz": 174,
        "description": "Gentle evening sounds for deep rest. Nighttime nature sounds with soft chimes.",
        "mood_category": "sleep",
        "icon": "🌙",
        "audio_url": "https://example.com/moonlight.mp3",
        "thumbnail_gradient": "from-indigo-50 to-blue-50"
    },
    {
        "title": "Chakra Balancing Tones",
        "duration_minutes": 21,
        "dosha_tags": ["vata", "pitta"],
        "emotion_tags": ["anxious", "unbalanced", "scattered"],
        "frequency_hz": 417,
        "description": "Sequential tones for each energy center. Promotes overall energetic balance.",
        "mood_category": "balancing",
        "icon": "💫",
        "audio_url": "https://example.com/chakra-tones.mp3",
        "thumbnail_gradient": "from-violet-50 to-purple-50"
    },
    {
        "title": "Waterfall Meditation",
        "duration_minutes": 40,
        "dosha_tags": ["vata", "pitta"],
        "emotion_tags": ["stressed", "overwhelmed", "tense"],
        "frequency_hz": 432,
        "description": "Continuous flowing water sounds. Perfect for extended meditation sessions.",
        "mood_category": "meditative",
        "icon": "💧",
        "audio_url": "https://example.com/waterfall.mp3",
        "thumbnail_gradient": "from-cyan-50 to-teal-50"
    },
    {
        "title": "Deep Forest Ambience",
        "duration_minutes": 35,
        "dosha_tags": ["kapha"],
        "emotion_tags": ["unmotivated", "sluggish", "withdrawn"],
        "frequency_hz": 528,
        "description": "Awakening forest sounds with birdsong. Stimulates energy and connection to nature.",
        "mood_category": "energizing",
        "icon": "🌲",
        "audio_url": "https://example.com/forest-ambience.mp3",
        "thumbnail_gradient": "from-green-50 to-lime-50"
    },
    {
        "title": "Sacred Temple Bells",
        "duration_minutes": 20,
        "dosha_tags": ["vata", "pitta", "kapha"],
        "emotion_tags": ["anxious", "scattered", "ungrounded"],
        "frequency_hz": 396,
        "description": "Resonant temple bells for grounding and centering. Traditional meditation accompaniment.",
        "mood_category": "grounding",
        "icon": "🔔",
        "audio_url": "https://example.com/temple-bells.mp3",
        "thumbnail_gradient": "from-amber-50 to-orange-50"
    }
]

# ============================================
# SEED DATABASE
# ============================================

def seed_yoga_poses():
    """Seed yoga poses into database."""
    print("\n📿 Seeding Yoga Poses...")
    
    try:
        # Check if table exists and has data
        existing = supabase.table("yoga_poses").select("id").limit(1).execute()
        
        if existing.data and len(existing.data) > 0:
            print("⚠️  Yoga poses already exist. Clearing old data...")
            # Delete all existing poses
            supabase.table("yoga_poses").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        # Insert all poses
        result = supabase.table("yoga_poses").insert(yoga_poses).execute()
        
        if result.data:
            print(f"✅ Inserted {len(result.data)} yoga poses")
        else:
            print("❌ Failed to insert yoga poses")
            
    except Exception as e:
        print(f"❌ Error seeding yoga poses: {e}")


def seed_sound_tracks():
    """Seed sound therapy tracks into database."""
    print("\n🎵 Seeding Sound Therapy Tracks...")
    
    try:
        # Check if table exists and has data
        existing = supabase.table("sound_tracks").select("id").limit(1).execute()
        
        if existing.data and len(existing.data) > 0:
            print("⚠️  Sound tracks already exist. Clearing old data...")
            # Delete all existing tracks
            supabase.table("sound_tracks").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        # Insert all tracks
        result = supabase.table("sound_tracks").insert(sound_tracks).execute()
        
        if result.data:
            print(f"✅ Inserted {len(result.data)} sound tracks")
        else:
            print("❌ Failed to insert sound tracks")
            
    except Exception as e:
        print(f"❌ Error seeding sound tracks: {e}")


def create_tables_if_missing():
    """Create yoga_poses and sound_tracks tables if they don't exist."""
    print("\n🔧 Checking database tables...")
    
    # Note: This requires direct database access or migration scripts
    # For now, we'll just try to seed and handle errors
    print("ℹ️  Assuming tables exist. Run schema migration if needed.")


if __name__ == "__main__":
    print("=" * 60)
    print("🌟 NIRVAMI DATABASE SEEDING SCRIPT")
    print("=" * 60)
    
    create_tables_if_missing()
    seed_yoga_poses()
    seed_sound_tracks()
    
    print("\n" + "=" * 60)
    print("✅ Database seeding complete!")
    print("=" * 60)
    print("\nℹ️  Next steps:")
    print("1. Verify data in Supabase dashboard")
    print("2. Update frontend to fetch from these tables")
    print("3. Test personalized recommendations")

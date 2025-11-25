"""
Seed comprehensive dosha recommendations into ayurveda_resources table.
Migrates hardcoded recommendations from dosha_service.py to database.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.database import get_supabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Comprehensive dosha recommendations
DOSHA_RECOMMENDATIONS = [
    # ================== VATA DIET ==================
    {
        "title": "Vata Dosha: Warm Cooked Foods",
        "content": "Favor warm, cooked foods to balance Vata's cold and dry qualities. Include soups, stews, and warm grain dishes. These help ground and nourish the body.",
        "category": "diet",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "diet", "warm foods", "cooked"]
    },
    {
        "title": "Vata Dosha: Healthy Fats",
        "content": "Include healthy fats like ghee and sesame oil in your diet. These lubricate and nourish Vata's dry nature. Use in cooking or drizzle over warm foods.",
        "category": "diet",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "diet", "ghee", "oils", "fats"]
    },
    {
        "title": "Vata Dosha: Sweet Fruits",
        "content": "Eat sweet fruits like bananas and avocados. These provide grounding energy and healthy fats. Avoid dry fruits unless soaked.",
        "category": "diet",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "diet", "fruits", "sweet"]
    },
    {
        "title": "Vata Dosha: Avoid Cold Raw Foods",
        "content": "Avoid cold, raw, and dry foods as they aggravate Vata. Raw salads, cold drinks, and crackers can increase dryness. Opt for warm, moist alternatives.",
        "category": "diet",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "diet", "avoid", "cold", "raw"]
    },
    {
        "title": "Vata Dosha: Herbal Teas for Hydration",
        "content": "Stay hydrated with warm herbal teas. Ginger, cinnamon, and fennel teas are especially balancing for Vata. Avoid excessive caffeine.",
        "category": "diet",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "diet", "tea", "hydration", "herbs"]
    },
    {
        "title": "Vata Dosha: Sweet, Sour, and Salty Tastes",
        "content": "Favor sweet, sour, and salty tastes to balance Vata. These tastes are grounding and nourishing. Examples: sweet potatoes, citrus fruits, sea salt.",
        "category": "diet",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "diet", "tastes", "sweet", "sour", "salty"]
    },
    
    # ================== VATA LIFESTYLE ==================
    {
        "title": "Vata Dosha: Regular Daily Routine",
        "content": "Maintain a regular daily routine to balance Vata's erratic nature. Wake up, eat, and sleep at consistent times. This creates stability and grounding.",
        "category": "lifestyle",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "lifestyle", "routine", "schedule", "stability"]
    },
    {
        "title": "Vata Dosha: Adequate Rest and Sleep",
        "content": "Get 7-8 hours of quality sleep. Vata types need more rest to recharge. Establish a calming bedtime routine with warm baths and gentle stretches.",
        "category": "lifestyle",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "lifestyle", "sleep", "rest", "bedtime"]
    },
    {
        "title": "Vata Dosha: Grounding Activities",
        "content": "Practice grounding activities like meditation, gentle yoga, and spending time in nature. These help calm the active Vata mind.",
        "category": "lifestyle",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "lifestyle", "grounding", "meditation", "nature"]
    },
    {
        "title": "Vata Dosha: Stay Warm",
        "content": "Stay warm and avoid cold, windy weather. Wear layers, use warming spices, and keep your environment cozy. Cold aggravates Vata.",
        "category": "lifestyle",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "lifestyle", "warmth", "temperature", "weather"]
    },
    {
        "title": "Vata Dosha: Gentle Calming Exercise",
        "content": "Choose gentle, calming exercises like walking, tai chi, or gentle yoga. Avoid excessive or intense workouts that deplete energy.",
        "category": "lifestyle",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "lifestyle", "exercise", "gentle", "calm"]
    },
    
    # ================== VATA YOGA ==================
    {
        "title": "Vata Dosha: Slow Sun Salutations",
        "content": "Practice Sun Salutations at a slow, mindful pace. This grounds Vata's airy quality while building warmth and stability.",
        "category": "yoga",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "yoga", "sun salutation", "surya namaskar", "slow"]
    },
    {
        "title": "Vata Dosha: Forward Bends",
        "content": "Include forward bends like Paschimottanasana (Seated Forward Fold) and Balasana (Child's Pose). These poses calm the nervous system.",
        "category": "yoga",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "yoga", "forward bend", "calming"]
    },
    {
        "title": "Vata Dosha: Restorative Poses",
        "content": "Practice restorative poses with props for deep relaxation. Supported Child's Pose and Legs-Up-The-Wall are excellent for Vata.",
        "category": "yoga",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "yoga", "restorative", "relaxation", "props"]
    },
    {
        "title": "Vata Dosha: Seated Twists",
        "content": "Gentle seated twists help with digestion and release tension. Practice Ardha Matsyendrasana (Half Lord of the Fishes Pose).",
        "category": "yoga",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "yoga", "twists", "digestion", "seated"]
    },
    
    # ================== VATA MEDITATION ==================
    {
        "title": "Vata Dosha: Grounding Meditation",
        "content": "Practice grounding meditation by visualizing roots growing from your body into the earth. This stabilizes Vata's scattered energy.",
        "category": "meditation",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "meditation", "grounding", "visualization", "stability"]
    },
    {
        "title": "Vata Dosha: Body Scan for Relaxation",
        "content": "Body scan meditation helps Vata types connect with their physical body. Systematically relax each body part from toes to head.",
        "category": "meditation",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "meditation", "body scan", "relaxation", "awareness"]
    },
    {
        "title": "Vata Dosha: Deep Slow Breathing",
        "content": "Practice breath awareness with deep, slow breaths. Inhale for 4 counts, hold for 4, exhale for 6. This calms the nervous system.",
        "category": "meditation",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "meditation", "breathing", "pranayama", "calm"]
    },
    {
        "title": "Vata Dosha: Yoga Nidra",
        "content": "Yoga Nidra (yogic sleep) is profoundly restorative for Vata. This guided meditation induces deep relaxation while maintaining awareness.",
        "category": "meditation",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "meditation", "yoga nidra", "deep relaxation", "sleep"]
    },
    
    # ================== PITTA DIET ==================
    {
        "title": "Pitta Dosha: Cool Refreshing Foods",
        "content": "Favor cool, refreshing foods to balance Pitta's heat. Include cucumbers, melons, coconut water, and leafy greens. These cool and soothe.",
        "category": "diet",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "diet", "cooling foods", "refreshing"]
    },
    {
        "title": "Pitta Dosha: Sweet Fruits and Vegetables",
        "content": "Include sweet fruits like melons, pears, and grapes. Sweet vegetables like zucchini and sweet potatoes are also balancing for Pitta.",
        "category": "diet",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "diet", "fruits", "vegetables", "sweet"]
    },
    {
        "title": "Pitta Dosha: Avoid Spicy and Oily Foods",
        "content": "Avoid spicy, oily, and fried foods as they aggravate Pitta's fire. Skip hot peppers, excess garlic, and deep-fried items.",
        "category": "diet",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "diet", "avoid", "spicy", "oily", "fried"]
    },
    {
        "title": "Pitta Dosha: Sweet, Bitter, and Astringent Tastes",
        "content": "Favor sweet, bitter, and astringent tastes. Examples: sweet fruits, leafy greens, beans, and lentils. These cool Pitta's heat.",
        "category": "diet",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "diet", "tastes", "sweet", "bitter", "astringent"]
    },
    {
        "title": "Pitta Dosha: Cool Water Hydration",
        "content": "Stay hydrated with cool (not ice cold) water. Coconut water and mint tea are especially cooling for Pitta. Avoid alcohol and caffeine.",
        "category": "diet",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "diet", "water", "hydration", "cooling"]
    },
    {
        "title": "Pitta Dosha: Cooling Herbs and Spices",
        "content": "Use cooling herbs like mint, cilantro, and fennel. Cardamom and coriander are also balancing. Avoid heating spices like cayenne.",
        "category": "diet",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "diet", "herbs", "spices", "cooling"]
    },
    
    # ================== PITTA LIFESTYLE ==================
    {
        "title": "Pitta Dosha: Avoid Overworking",
        "content": "Avoid overworking and pushing yourself too hard. Pitta types are naturally driven but need balance. Take regular breaks and rest periods.",
        "category": "lifestyle",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "lifestyle", "work-life balance", "rest", "moderation"]
    },
    {
        "title": "Pitta Dosha: Practice Moderation",
        "content": "Practice moderation in all activities. Balance work with play, intensity with relaxation. Avoid competitive or aggressive environments.",
        "category": "lifestyle",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "lifestyle", "moderation", "balance", "temperance"]
    },
    {
        "title": "Pitta Dosha: Nature and Water",
        "content": "Spend time in nature, especially near water. Lakes, rivers, and oceans are particularly cooling for Pitta. Moonlight walks are beneficial.",
        "category": "lifestyle",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "lifestyle", "nature", "water", "cooling"]
    },
    {
        "title": "Pitta Dosha: Avoid Excessive Heat",
        "content": "Avoid excessive sun exposure and hot environments. Stay in the shade during peak sun hours. Keep your living space cool and well-ventilated.",
        "category": "lifestyle",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "lifestyle", "heat", "sun", "temperature"]
    },
    {
        "title": "Pitta Dosha: Moderate Exercise",
        "content": "Choose cooling, moderate exercises like swimming, walking in nature, or gentle cycling. Avoid heated or overly competitive sports.",
        "category": "lifestyle",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "lifestyle", "exercise", "moderate", "cooling"]
    },
    
    # ================== PITTA YOGA ==================
    {
        "title": "Pitta Dosha: Moon Salutations",
        "content": "Practice Moon Salutations (Chandra Namaskar) for cooling energy. This sequence is less heating than Sun Salutations.",
        "category": "yoga",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "yoga", "moon salutation", "chandra namaskar", "cooling"]
    },
    {
        "title": "Pitta Dosha: Forward Bends and Twists",
        "content": "Include cooling forward bends and gentle twists. These help release heat and tension. Practice with ease, not force.",
        "category": "yoga",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "yoga", "forward bend", "twist", "cooling"]
    },
    {
        "title": "Pitta Dosha: Hip Openers",
        "content": "Hip opening poses like Pigeon Pose release stored heat and emotions. Practice these with patience and acceptance.",
        "category": "yoga",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "yoga", "hip openers", "pigeon pose", "release"]
    },
    {
        "title": "Pitta Dosha: Shoulder Stands and Inversions",
        "content": "Gentle inversions like Shoulder Stand are cooling for Pitta. Avoid hot, intense inversions. Use props for support.",
        "category": "yoga",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "yoga", "inversions", "shoulder stand", "cooling"]
    },
    
    # ================== PITTA MEDITATION ==================
    {
        "title": "Pitta Dosha: Cooling Breath Meditation",
        "content": "Practice Sheetali (cooling breath): curl tongue into tube, inhale through mouth, exhale through nose. This cools Pitta's heat.",
        "category": "meditation",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "meditation", "cooling breath", "sheetali", "pranayama"]
    },
    {
        "title": "Pitta Dosha: Loving-Kindness Meditation",
        "content": "Metta (loving-kindness) meditation softens Pitta's intensity. Send compassion to yourself and others. This cultivates gentleness.",
        "category": "meditation",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "meditation", "loving-kindness", "metta", "compassion"]
    },
    {
        "title": "Pitta Dosha: Peaceful Visualization",
        "content": "Visualize cool, peaceful scenes like moonlit beaches or mountain lakes. This mentally cools Pitta's fiery nature.",
        "category": "meditation",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "meditation", "visualization", "peaceful", "cooling"]
    },
    {
        "title": "Pitta Dosha: Mindfulness Meditation",
        "content": "Practice non-judgmental mindfulness. Observe thoughts and sensations without criticism. This reduces Pitta's tendency to judge.",
        "category": "meditation",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "meditation", "mindfulness", "awareness", "acceptance"]
    },
    
    # ================== KAPHA DIET ==================
    {
        "title": "Kapha Dosha: Light Warm Spicy Foods",
        "content": "Favor light, warm, and spicy foods to balance Kapha's heavy, cool qualities. Include vegetables, legumes, and warming spices.",
        "category": "diet",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "diet", "light foods", "spicy", "warm"]
    },
    {
        "title": "Kapha Dosha: Bitter and Astringent Tastes",
        "content": "Include bitter and astringent tastes like leafy greens, cruciferous vegetables, and beans. These reduce Kapha's heaviness.",
        "category": "diet",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "diet", "tastes", "bitter", "astringent"]
    },
    {
        "title": "Kapha Dosha: Avoid Heavy and Sweet Foods",
        "content": "Avoid heavy, oily, and sweet foods that increase Kapha. Limit dairy, fried foods, and sugary items. Choose lighter alternatives.",
        "category": "diet",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "diet", "avoid", "heavy", "sweet", "oily"]
    },
    {
        "title": "Kapha Dosha: Warming Spices",
        "content": "Use warming spices like ginger, black pepper, turmeric, and cayenne. These stimulate digestion and reduce mucus.",
        "category": "diet",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "diet", "spices", "ginger", "pepper", "warming"]
    },
    {
        "title": "Kapha Dosha: Ginger Tea",
        "content": "Drink warm ginger tea to stimulate digestion and metabolism. Add honey (not heated) for additional benefits. Avoid cold drinks.",
        "category": "diet",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "diet", "ginger tea", "digestion", "metabolism"]
    },
    {
        "title": "Kapha Dosha: Pungent Foods",
        "content": "Include pungent tastes like onions, garlic, radishes, and mustard greens. These cut through Kapha's heaviness and sluggishness.",
        "category": "diet",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "diet", "pungent", "stimulating", "digestion"]
    },
    
    # ================== KAPHA LIFESTYLE ==================
    {
        "title": "Kapha Dosha: Stay Active and Energized",
        "content": "Stay active and energized throughout the day. Kapha types benefit from regular movement. Avoid sedentary habits and excessive sitting.",
        "category": "lifestyle",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "lifestyle", "active", "energized", "movement"]
    },
    {
        "title": "Kapha Dosha: Wake Up Early",
        "content": "Wake up before 6 AM to harness the light, mobile energy of Vata time. Early rising prevents Kapha's sluggishness.",
        "category": "lifestyle",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "lifestyle", "early rising", "morning", "wake up"]
    },
    {
        "title": "Kapha Dosha: Stimulating Activities",
        "content": "Engage in stimulating, varied activities. Try new experiences, learn new skills, and seek variety. Avoid routine that becomes stagnant.",
        "category": "lifestyle",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "lifestyle", "stimulation", "variety", "new experiences"]
    },
    {
        "title": "Kapha Dosha: Avoid Daytime Naps",
        "content": "Avoid daytime naps as they increase Kapha's lethargy. If needed, rest briefly without falling asleep. Stay active during the day.",
        "category": "lifestyle",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "lifestyle", "no naps", "alertness", "activity"]
    },
    {
        "title": "Kapha Dosha: Vigorous Exercise",
        "content": "Choose vigorous, energizing exercises like running, cycling, or aerobics. Kapha types thrive on intense physical activity.",
        "category": "lifestyle",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "lifestyle", "exercise", "vigorous", "energizing"]
    },
    
    # ================== KAPHA YOGA ==================
    {
        "title": "Kapha Dosha: Dynamic Sun Salutations",
        "content": "Practice Sun Salutations at a dynamic, energizing pace. Multiple rounds build heat and counter Kapha's sluggishness.",
        "category": "yoga",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "yoga", "sun salutation", "dynamic", "energizing"]
    },
    {
        "title": "Kapha Dosha: Backbends and Chest Openers",
        "content": "Include backbends like Cobra, Camel, and Bridge Pose. These open the chest, stimulate lungs, and energize the body.",
        "category": "yoga",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "yoga", "backbend", "chest opener", "energizing"]
    },
    {
        "title": "Kapha Dosha: Inversions",
        "content": "Practice inversions like Headstand or Shoulder Stand (when ready). These reverse Kapha's downward energy and stimulate circulation.",
        "category": "yoga",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "yoga", "inversions", "headstand", "stimulating"]
    },
    {
        "title": "Kapha Dosha: Warrior Poses",
        "content": "Hold Warrior I, II, and III for strength and stamina. These poses build heat, strength, and mental focus for Kapha types.",
        "category": "yoga",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "yoga", "warrior poses", "strength", "stamina"]
    },
    {
        "title": "Kapha Dosha: Flow Sequences",
        "content": "Practice flowing vinyasa sequences to maintain heat and movement. Keep moving rather than holding poses for long periods.",
        "category": "yoga",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "yoga", "vinyasa", "flow", "movement"]
    },
    
    # ================== KAPHA MEDITATION ==================
    {
        "title": "Kapha Dosha: Energizing Breathwork",
        "content": "Practice Kapalabhati (skull-shining breath) or Bhastrika (bellows breath). These pranayama techniques energize and clear Kapha congestion.",
        "category": "meditation",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "meditation", "breathwork", "kapalabhati", "energizing"]
    },
    {
        "title": "Kapha Dosha: Active Meditation",
        "content": "Try walking meditation or mindful movement. Active meditation suits Kapha better than long seated sessions.",
        "category": "meditation",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "meditation", "active", "walking", "movement"]
    },
    {
        "title": "Kapha Dosha: Light and Energy Visualization",
        "content": "Visualize bright, energizing light filling your body. Imagine this light burning away heaviness and inertia.",
        "category": "meditation",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "meditation", "visualization", "light", "energy"]
    },
    {
        "title": "Kapha Dosha: Morning Meditation",
        "content": "Practice meditation early in the morning (before 6 AM) when energy is light and clear. This prevents Kapha sluggishness.",
        "category": "meditation",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "meditation", "morning practice", "early", "routine"]
    }
]


def seed_dosha_recommendations():
    """Seed dosha recommendations into ayurveda_resources table."""
    logger.info("🌱 Starting dosha recommendations seeding...")
    
    try:
        supabase = get_supabase(use_service_role=True)
        logger.info(f"📊 Seeding {len(DOSHA_RECOMMENDATIONS)} recommendations...")
        
        # Clear existing dosha-specific resources (optional - comment out to keep existing)
        # logger.info("🗑️  Clearing existing dosha recommendations...")
        # for dosha in ["vata", "pitta", "kapha"]:
        #     supabase.table("ayurveda_resources").delete().contains("dosha_tags", [dosha]).execute()
        
        success_count = 0
        for i, rec in enumerate(DOSHA_RECOMMENDATIONS, 1):
            try:
                # Insert recommendation
                result = supabase.table("ayurveda_resources").insert(rec).execute()
                
                if result.data:
                    success_count += 1
                    dosha = rec['dosha_tags'][0] if rec['dosha_tags'] else 'general'
                    logger.info(f"   [{i}/{len(DOSHA_RECOMMENDATIONS)}] ✅ {dosha.upper()}: {rec['title']}")
                else:
                    logger.warning(f"   [{i}/{len(DOSHA_RECOMMENDATIONS)}] ⚠️  No data returned for: {rec['title']}")
                    
            except Exception as e:
                logger.error(f"   [{i}/{len(DOSHA_RECOMMENDATIONS)}] ❌ Error: {rec['title']} - {e}")
        
        logger.info(f"\n✅ Successfully seeded {success_count}/{len(DOSHA_RECOMMENDATIONS)} recommendations!")
        
        # Summary
        logger.info("\n📈 Summary by dosha:")
        for dosha in ["vata", "pitta", "kapha"]:
            count = len([r for r in DOSHA_RECOMMENDATIONS if dosha in r['dosha_tags']])
            logger.info(f"   {dosha.capitalize()}: {count} recommendations")
        
        logger.info("\n📊 Summary by category:")
        categories = {}
        for rec in DOSHA_RECOMMENDATIONS:
            cat = rec['category']
            categories[cat] = categories.get(cat, 0) + 1
        for cat, count in sorted(categories.items()):
            logger.info(f"   {cat.capitalize()}: {count} recommendations")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to seed recommendations: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    logger.info("="*80)
    logger.info("DOSHA RECOMMENDATIONS SEEDER")
    logger.info("="*80)
    
    success = seed_dosha_recommendations()
    
    if success:
        logger.info("\n" + "="*80)
        logger.info("🎉 SEEDING COMPLETED SUCCESSFULLY!")
        logger.info("="*80)
        logger.info("\n📝 Next steps:")
        logger.info("   1. Verify data in Supabase: SELECT * FROM ayurveda_resources;")
        logger.info("   2. Update dosha_service.py to read from database")
        logger.info("   3. Test /api/v1/dosha/recommendations endpoint")
    else:
        logger.error("\n" + "="*80)
        logger.error("❌ SEEDING FAILED")
        logger.error("="*80)
        sys.exit(1)

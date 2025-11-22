"""Script to seed Ayurvedic resources with embeddings."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.database import get_supabase
from app.ml.model_manager import ModelManager
import asyncio
import uuid

# Sample Ayurvedic resources
RESOURCES = [
    {
        "title": "Vata Dosha Balancing Diet",
        "content": "Vata dosha is characterized by air and space elements. To balance Vata, favor warm, cooked, and grounding foods. Include sweet fruits like bananas, cooked grains like rice and oats, and healthy fats like ghee. Avoid cold, raw, and dry foods. Drink warm liquids and herbal teas.",
        "category": "diet",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "diet", "warm foods", "grounding"]
    },
    {
        "title": "Pitta Dosha Balancing Diet",
        "content": "Pitta dosha is dominated by fire and water elements. To balance Pitta, choose cooling and refreshing foods. Include sweet fruits like melons, coconut water, cucumber, and leafy greens. Avoid spicy, salty, and fried foods. Favor sweet, bitter, and astringent tastes.",
        "category": "diet",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "diet", "cooling foods", "balance"]
    },
    {
        "title": "Kapha Dosha Balancing Diet",
        "content": "Kapha dosha combines earth and water elements. To balance Kapha, eat light, warm, and dry foods. Include spices like ginger, black pepper, and turmeric. Favor bitter and astringent vegetables. Reduce heavy, oily, and sweet foods. Choose warm beverages over cold.",
        "category": "diet",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "diet", "light foods", "spices"]
    },
    {
        "title": "Yoga for Vata Balance",
        "content": "Vata-balancing yoga focuses on grounding and stability. Practice slow, gentle flows with grounding poses like Mountain Pose (Tadasana), Tree Pose (Vrksasana), and Forward Bends. Include restorative poses and Yoga Nidra. Emphasize breath awareness and mindful movement.",
        "category": "yoga",
        "dosha_tags": ["vata"],
        "keywords": ["vata", "yoga", "grounding", "stability"]
    },
    {
        "title": "Yoga for Pitta Balance",
        "content": "Pitta-balancing yoga emphasizes cooling and calming practices. Include forward folds, twists, and moon salutations. Avoid intense inversions and heated practices. Practice with ease and mindfulness. Include cooling pranayama like Sheetali and Sheetkari breathing.",
        "category": "yoga",
        "dosha_tags": ["pitta"],
        "keywords": ["pitta", "yoga", "cooling", "calming"]
    },
    {
        "title": "Yoga for Kapha Balance",
        "content": "Kapha-balancing yoga should be energizing and dynamic. Practice Sun Salutations, backbends, and challenging balances. Include vigorous flows and rhythmic breathing. Focus on movement and heat generation. Practice in the morning for best results.",
        "category": "yoga",
        "dosha_tags": ["kapha"],
        "keywords": ["kapha", "yoga", "energizing", "dynamic"]
    },
    {
        "title": "Meditation for Anxiety",
        "content": "For anxiety relief, practice mindful breathing meditation. Sit comfortably and focus on your natural breath. When thoughts arise, gently return attention to breathing. Practice 10-15 minutes daily. Include body scan meditation to release tension. Grounding techniques help calm anxious minds.",
        "category": "meditation",
        "dosha_tags": ["vata", "pitta"],
        "keywords": ["meditation", "anxiety", "breathing", "mindfulness"]
    },
    {
        "title": "Ayurvedic Sleep Routine",
        "content": "Establish a consistent sleep schedule, aiming to sleep by 10 PM. Create a calming bedtime ritual: warm bath, self-massage with sesame oil, herbal tea. Avoid screens 1 hour before bed. Practice gentle stretches or meditation. Keep bedroom cool and dark.",
        "category": "lifestyle",
        "dosha_tags": ["vata", "pitta", "kapha"],
        "keywords": ["sleep", "routine", "bedtime", "rest"]
    },
    {
        "title": "Stress Management with Ayurveda",
        "content": "Ayurvedic stress management includes regular meditation, pranayama, and yoga. Follow a daily routine (dinacharya). Practice oil massage (abhyanga). Use adaptogenic herbs like Ashwagandha and Brahmi. Maintain work-life balance and spend time in nature.",
        "category": "lifestyle",
        "dosha_tags": ["vata", "pitta", "kapha"],
        "keywords": ["stress", "management", "meditation", "herbs"]
    },
    {
        "title": "Pranayama for Calmness",
        "content": "Nadi Shodhana (alternate nostril breathing) balances the nervous system. Sit comfortably, close right nostril, inhale through left, then close left, exhale through right. Continue alternating. Practice 5-10 minutes daily. This technique reduces stress and anxiety.",
        "category": "meditation",
        "dosha_tags": ["vata", "pitta"],
        "keywords": ["pranayama", "breathing", "calm", "nervous system"]
    }
]


async def seed_resources():
    """Seed Ayurvedic resources with embeddings."""
    print("Initializing model manager...")
    model_manager = ModelManager()
    await model_manager.load_models()
    
    print("Connecting to Supabase...")
    supabase = get_supabase(use_service_role=True)
    
    print(f"Seeding {len(RESOURCES)} Ayurvedic resources...")
    
    for i, resource in enumerate(RESOURCES, 1):
        try:
            # Generate embedding
            print(f"[{i}/{len(RESOURCES)}] Processing: {resource['title']}")
            embedding = model_manager.generate_embedding(resource['content'])
            
            # Create record
            resource_data = {
                "id": str(uuid.uuid4()),
                "title": resource["title"],
                "content": resource["content"],
                "category": resource["category"],
                "dosha_tags": resource["dosha_tags"],
                "keywords": resource["keywords"],
                "embedding": embedding
            }
            
            # Insert into database
            supabase.table("ayurveda_resources").insert(resource_data).execute()
            print(f"  ✓ Inserted successfully")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n✨ Seeding completed!")


if __name__ == "__main__":
    asyncio.run(seed_resources())

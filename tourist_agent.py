import asyncio
from pydantic import BaseModel, Field
from typing import Optional, List
import google.generativeai as genai

# ----- Weather Tool -----
def get_weather(destination: str) -> str:
    """Fake weather data for now. Replace with real API if needed."""
    return f"Currently sunny in {destination} with mild temperatures."

# ----- Query Model -----
class TouristQuery(BaseModel):
    destination: str = Field(..., description="City or location to visit")
    start_date: Optional[str] = Field(None, description="Start date of trip (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date of trip (YYYY-MM-DD)")
    interests: Optional[List[str]] = Field(None, description="User interests like history, food, etc.")
    budget: Optional[str] = Field(None, description="Budget: low, medium, high")

# ----- Guardrail -----
def trip_guardrail(query: TouristQuery) -> bool:
    travel_keywords = {
        "trip", "picnic", "travel", "tour", "holiday", "vacation", "sightseeing",
        "nature", "food", "history", "culture", "adventure", "beach", "mountain",
        "city", "explore", "visit", "destination", "itinerary", "plan", "park",
        "museum", "festival", "hiking", "camping"
    }
    irrelevant_keywords = {
        "math", "physics", "coding", "software", "quantum", "algebra", "calculus",
        "programming", "chemistry", "biology", "exam", "lab", "research"
    }
    destination_lower = query.destination.lower().strip()
    if any(keyword in destination_lower for keyword in irrelevant_keywords):
        return False
    if query.interests:
        has_interest_match = any(
            any(k in interest.lower() for k in travel_keywords)
            for interest in query.interests
        )
        if not has_interest_match:
            return False
    return True

# ----- Prompt Template -----
SYSTEM_PROMPT = """
You are a friendly and knowledgeable tourist agent. Your goal is to help users plan their trips by:
- Suggesting a daily itinerary for their destination based on their interests and budget.
- Providing practical tips (e.g., best time to visit, local customs).
- Incorporating weather information.
- Tailoring recommendations to trip duration if dates are provided.
- Prioritizing activities matching interests.
- Adapting to budget (free vs premium activities).
Keep responses concise, engaging, and informative.
"""

# ----- Main Logic -----
async def run_tourist_agent(query: TouristQuery, gemini_client) -> str:
    if not trip_guardrail(query):
        raise ValueError("Kindly query about picnic, trip, or related topics.")

    weather_info = get_weather(query.destination)

    prompt = f"""
Plan a trip with these details:
- Destination: {query.destination}
- Start Date: {query.start_date or 'Not specified'}
- End Date: {query.end_date or 'Not specified'}
- Interests: {', '.join(query.interests) if query.interests else 'General sightseeing'}
- Budget: {query.budget or 'Not specified'}
- Weather Info: {weather_info}
"""

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: gemini_client.generate_content([
            {"role": "user", "parts": [{"text": SYSTEM_PROMPT + "\n\n" + prompt}]}
        ])
    )
    return response.text

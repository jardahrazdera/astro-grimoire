# ------------------------------------------------------------------------------
# Astro Backend API
# ------------------------------------------------------------------------------
# Author: Gemini
# Description: FastAPI backend for astronomical calculations (Solstices,
#              Sun/Moon cycles, Lunar phases) based on user location.
#
# Requirements:
#   pip install fastapi uvicorn ephem
#
# Usage:
#   Run the server: uvicorn astro_backend:app --reload
#   Access docs:    http://127.0.0.1:8000/docs
# ------------------------------------------------------------------------------

from datetime import datetime, date
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
from geopy.geocoders import Nominatim
import ephem
import math
import requests

# Initialize FastAPI app
app = FastAPI(
    title="AstroCalc API",
    description="API for calculating solstices, lunar phases, and celestial rise/set times.",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://astro.jaroslav.tech"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# Data Models
# ------------------------------------------------------------------------------


class LocationResult(BaseModel):
    name: str
    display_name: str
    lat: float
    lon: float
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None


class SolsticeData(BaseModel):
    summer_solstice: str
    winter_solstice: str
    hemisphere: str


class CelestialBodyTimes(BaseModel):
    rise: Optional[str]
    set: Optional[str]
    is_always_up: bool = False
    is_always_down: bool = False


class MoonPhaseData(BaseModel):
    phase_name: str
    illumination_percent: float
    age_days: float


class AstroResponse(BaseModel):
    location: Dict[str, float]
    current_date: str
    sun_times: CelestialBodyTimes
    moon_times: CelestialBodyTimes
    moon_phase: MoonPhaseData
    solstices_current_year: SolsticeData


# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------


def get_hemisphere(lat: float) -> str:
    """Determines the hemisphere based on latitude."""
    return "Northern" if lat >= 0 else "Southern"


def format_ephem_date(ephem_date) -> str:
    """Converts ephem date object to ISO format string with UTC suffix."""
    try:
        # ephem.Date can be converted to datetime
        dt = ephem.Date(ephem_date).datetime()
        return dt.isoformat() + "Z"
    except Exception:
        return None


def get_moon_phase_name(lunation: float) -> str:
    """
    Returns the moon phase name based on lunation value (0-1).
    0 = New Moon, 0.5 = Full Moon.
    """
    # Normalize to 0-1 range roughly if needed, usually ephem gives 0..2pi logic elsewhere,
    # but here we use simple logic based on phase illumination and angle could be better,
    # but let's use a simpler approximation based on age/angle.

    # Actually, a better way with ephem is checking the phase angle or elongation.
    # But for simplicity, we can categorize by 'phase' (illumination) isn't enough (waxing/waning distinction).
    # Let's use simple logic based on previous new moon.
    pass
    # NOTE: Implemented directly in the main logic using accurate angle calculation below.
    return "Unknown"


# ------------------------------------------------------------------------------
# Core Logic
# ------------------------------------------------------------------------------


@app.get("/", tags=["General"])
async def root():
    """Health check endpoint."""
    return {"message": "AstroCalc API is running. Go to /docs for usage."}


@app.get("/search-location", response_model=List[LocationResult], tags=["Location"])
async def search_location(
    q: str = Query(..., description="City or place name to search for (e.g. 'Prague')")
):
    """
    Search for a location by name and return coordinates with details.
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": q,
            "format": "json",
            "addressdetails": 1,
            "limit": 100,
            "dedupe": 0,  # Ensure we get duplicates/variants
            "accept-language": "en"
        }
        headers = {
            "User-Agent": "astro_grimoire_app/1.0"
        }
        
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
        locations = resp.json()

        if not locations:
            return []

        candidates = []
        for loc in locations:
            # Filter: only keep administrative boundaries or place markers (cities, towns, etc)
            # This excludes 'highway', 'building', 'amenity', etc.
            if loc.get("class") not in ["place", "boundary"]:
                continue

            address = loc.get("address", {})
            city = address.get("city")
            town = address.get("town")
            village = address.get("village")
            hamlet = address.get("hamlet")
            suburb = address.get("suburb")
            muni = address.get("municipality")
            
            place_name = city or town or village or hamlet or suburb or muni or loc.get("display_name", "").split(",")[0]
            
            # Store result with importance for sorting
            importance = loc.get("importance", 0)
            
            result_obj = LocationResult(
                name=place_name,
                display_name=loc.get("display_name"),
                lat=float(loc.get("lat")),
                lon=float(loc.get("lon")),
                country=address.get("country"),
                state=address.get("state") or address.get("region"),
                city=city or town or village
            )
            candidates.append((importance, result_obj))
        
        # Sort by importance descending
        candidates.sort(key=lambda x: x[0], reverse=True)

        # Return top 30 filtered results
        return [c[1] for c in candidates[:30]]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding error: {str(e)}")


@app.get("/reverse-geocode", response_model=LocationResult, tags=["Location"])
async def reverse_geocode(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """
    Find location details from coordinates.
    """
    try:
        geolocator = Nominatim(user_agent="astro_grimoire_app")
        location = geolocator.reverse((lat, lon), language="en", addressdetails=True)

        if not location:
            raise HTTPException(status_code=404, detail="Location not found")

        address = location.raw.get("address", {})
        country = address.get("country")
        state = address.get("state") or address.get("region")
        
        # Try to find a sensible "City" name
        city = address.get("city") or address.get("town") or address.get("village") or address.get("hamlet")
        
        # Determine a short name
        short_name = city if city else location.address.split(",")[0]

        return LocationResult(
            name=short_name,
            display_name=location.address,
            lat=lat,
            lon=lon,
            country=country,
            state=state,
            city=city
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding error: {str(e)}")



@app.get("/astro-data", response_model=AstroResponse, tags=["Astronomy"])
async def get_astro_data(
    lat: float = Query(
        ..., description="Latitude in decimal degrees"
    ),
    lon: float = Query(
        ..., description="Longitude in decimal degrees"
    ),
    date_str: Optional[str] = Query(
        None, alias="date", description="Date in YYYY-MM-DD format. Defaults to today."
    ),
):
    """
    Calculate astronomical data for a specific location and date.
    """
    try:
        # 1. Setup Observer
        observer = ephem.Observer()
        observer.lat = str(lat)
        observer.lon = str(lon)
        observer.elevation = 0  # Default elevation
        observer.pressure = 1013.25 # Standard pressure for refraction
        observer.horizon = '-0:34'  # Standard sunrise/sunset definition (34 arcminutes below horizon)

        # Set date or use current UTC time
        if date_str:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            target_date = datetime.utcnow()

        observer.date = target_date

        # 2. Celestial Bodies
        sun = ephem.Sun()
        moon = ephem.Moon()

        # Compute positions for the current time
        sun.compute(observer)
        moon.compute(observer)

        # 3. Calculate Rise and Set times
        # Strategy: Set observer to noon of the target date to ensure we find 
        # the rise/set times occurring on THIS specific day reliably.
        noon_of_day = target_date.replace(hour=12, minute=0, second=0, microsecond=0)
        
        # We search backwards from noon for the rise and forwards from noon for the set
        # of the current 24h period.
        
        def get_times_precise(body, obs_noon):
            data = {
                "rise": None,
                "set": None,
                "is_always_up": False,
                "is_always_down": False,
            }
            try:
                # To find the events for the current calendar day, 
                # we search from midnight to midnight.
                midnight = obs_noon.date - 0.5
                obs_rising = ephem.Observer()
                obs_rising.lat, obs_rising.lon, obs_rising.elevation = obs_noon.lat, obs_noon.lon, obs_noon.elevation
                obs_rising.pressure, obs_rising.horizon = obs_noon.pressure, obs_noon.horizon
                obs_rising.date = midnight
                
                # next_rising gives the first rising AFTER midnight
                data["rise"] = format_ephem_date(obs_rising.next_rising(body))
                # next_setting gives the first setting AFTER midnight
                data["set"] = format_ephem_date(obs_rising.next_setting(body))
                
            except ephem.AlwaysUpError:
                data["is_always_up"] = True
            except ephem.AlwaysDownError:
                data["is_always_down"] = True
            except Exception:
                pass
            return data

        sun_data = get_times_precise(ephem.Sun(), observer)
        moon_data = get_times_precise(ephem.Moon(), observer)

        # 4. Moon Phase Calculation
        # illumination is percentage (0-100)
        illumination = moon.phase

        # To determine Waxing/Waning, we check the difference between Sun and Moon longitude
        # angular separation
        sun_lon = sun.hlon
        moon_lon = moon.hlon
        # Normalize to 0-2pi
        sep = (moon_lon - sun_lon) % (2 * math.pi)
        degree_sep = math.degrees(sep)

        phase_name = ""
        if degree_sep < 10:
            phase_name = "New Moon"
        elif degree_sep < 85:
            phase_name = "Waxing Crescent"
        elif degree_sep < 95:
            phase_name = "First Quarter"
        elif degree_sep < 175:
            phase_name = "Waxing Gibbous"
        elif degree_sep < 185:
            phase_name = "Full Moon"
        elif degree_sep < 265:
            phase_name = "Waning Gibbous"
        elif degree_sep < 275:
            phase_name = "Last Quarter"
        elif degree_sep < 350:
            phase_name = "Waning Crescent"
        else:
            phase_name = "New Moon"

        # 5. Solstices for the current year
        current_year = target_date.year

        # ephem.next_solstice finds the next one from a given date.
        # To find specific seasonal solstices, we look around standard months.
        # June Solstice (Summer in North, Winter in South) ~ June 21
        # December Solstice (Winter in North, Summer in South) ~ Dec 21

        d1 = ephem.next_solstice(date(current_year, 6, 1))
        d2 = ephem.next_solstice(date(current_year, 12, 1))

        hemisphere = get_hemisphere(lat)

        if hemisphere == "Northern":
            summer_sol_date = format_ephem_date(d1)
            winter_sol_date = format_ephem_date(d2)
        else:
            # Southern hemisphere logic
            summer_sol_date = format_ephem_date(d2)  # December is summer
            winter_sol_date = format_ephem_date(d1)  # June is winter

        # 6. Construct Response
        return AstroResponse(
            location={"lat": lat, "lon": lon},
            current_date=target_date.isoformat(),
            sun_times=CelestialBodyTimes(**sun_data),
            moon_times=CelestialBodyTimes(**moon_data),
            moon_phase=MoonPhaseData(
                phase_name=phase_name,
                illumination_percent=round(illumination, 1),
                age_days=round(degree_sep / 360 * 29.53, 1),  # Approximate moon age
            ),
            solstices_current_year=SolsticeData(
                summer_solstice=summer_sol_date,
                winter_solstice=winter_sol_date,
                hemisphere=hemisphere,
            ),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    # Run on localhost port 8000
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

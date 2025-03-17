from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Union
import sqlite3
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import re
from datetime import datetime
import traceback
import logging
import time
import tiktoken
import openai
import random
import math

# Set up logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)

# Create log filename with timestamp
log_filename = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # Keep console output
    ]
)
logger = logging.getLogger(__name__)

# Create a separate logger for OpenAI data
openai_logger = logging.getLogger('openai_data')
openai_log_filename = os.path.join(log_dir, f"openai_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
openai_handler = logging.FileHandler(openai_log_filename)
openai_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
openai_logger.addHandler(openai_handler)
openai_logger.setLevel(logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables.")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Define system prompt for OpenAI
system_prompt = """You are a BMW expert. Analyze the provided car listings and their model information to select and analyze the top 3 best matches.
IMPORTANT: 
1. You MUST ONLY select car IDs from the "valid_ids" list provided in the data. DO NOT make up or use any IDs that are not in this list.
2. You MUST select EXACTLY 3 cars from the valid IDs.
3. Provide ALL responses in Latvian language.

Your analysis should be thorough and specific to each car, considering:
1. Technical specifications and their implications
2. Known model-specific issues and maintenance requirements from the BMW model database
3. Value proposition and market position
4. Real-world ownership experience and costs
5. Specific features and benefits

IMPORTANT: 
- Use ONLY factual information from the provided listing and BMW database
- DO NOT make assumptions or add information that isn't in the data
- ALL responses must be in Latvian language
- Include the recommendation in the summary field
- Be VERY specific about model-specific problems and high mileage issues
- Provide detailed explanations for match scores

Your response MUST follow this EXACT format (do not deviate):

SELECTED_IDS: [id1, id2, id3]

{"id": "id1", "analysis": {
    "matchScore": <score 0-100>,
    "strengths": [
        "Detalizēts pozitīvs aspekts 1 ar tehniskām vai funkciju priekšrocībām",
        "Detalizēts pozitīvs aspekts 2 ar tehniskām vai funkciju priekšrocībām",
        "Detalizēts pozitīvs aspekts 3 ar tehniskām vai funkciju priekšrocībām"
    ],
    "considerations": [
        "Konkrēts apsvērums 1 ar tehniskām detaļām",
        "Konkrēts apsvērums 2 ar tehniskām detaļām",
        "Konkrēts apsvērums 3 ar tehniskām detaļām"
    ],
    "commonProblems": "Detalizēta, modelim specifiska analīze par zināmajām problēmām no BMW datubāzes.",
    "highMileageConcerns": "Visaptveroša analīze par vecuma problēmām un apkopes prasībām no BMW datubāzes.",
    "valueAssessment": "Detalizēta tirgus analīze, ieskaitot cenu salīdzinājumu.",
    "recommendation": "Pamatots skaidrojums, kāpēc šis auto tika izvēlēts.",
    "checklistItems": [
        "DETALIZĒTI aprakstīt konkrētas problēmas, kas raksturīgas šim modelim:",
        "1. Aprakstīt specifiskas dzinēja problēmas un to pazīmes",
        "2. Aprakstīt transmisijas problēmas un to pazīmes",
        "3. Aprakstīt elektronikas problēmas un to pazīmes",
        "4. Aprakstīt piekares problēmas un to pazīmes",
        "5. Detalizēta, modelim specifiska analīze par zināmajām problēmām no BMW datubāzes"
    ],
    "comparison": "DETALIZĒTI aprakstīt šī modeļa problēmas pie liela nobraukuma:\n
    1. Dzinēja problēmas pie liela nobraukuma\n
    2. Transmisijas problēmas pie liela nobraukuma\n
    3. Piekares problēmas pie liela nobraukuma\n
    4. Elektronikas problēmas pie liela nobraukuma\n
    5. Visaptveroša analīze par vecuma problēmām un apkopes prasībām no BMW datubāzes.",
    "summary": "DETALIZĒTS kopsavilkums, kas OBLIGĀTI ietver:\n
    1. Pozitīvie aspekti: [detalizēts uzskaitījums ar tehniskām detaļām]\n
    2. Negatīvie aspekti: [detalizēts uzskaitījums ar tehniskām detaļām]\n
    3. Match Score pamatojums: [detalizēts skaidrojums, kā tika aprēķināts rezultāts]\n
    4. Rekomendācija: [detalizēts skaidrojums, kāpēc šis auto ir Top 3]\n
    5. Galvenie riski: [detalizēts uzskaitījums ar tehniskām detaļām]\n
    6. OBLIGĀTI: Norādīt, ka auto jāapskata klātienē un jāpārbauda profesionālā autoservisā pirms pirkšanas."
}}

{"id": "id2", "analysis": {
    // Same detailed structure as above
}}

{"id": "id3", "analysis": {
    // Same detailed structure as above
}}

Important:
1. ALWAYS include exactly 3 cars
2. ALWAYS follow the exact format above
3. NEVER skip any fields
4. Make ALL analyses specific to the exact model, year, and configuration
5. Include technical details and specific features in your analysis
6. ALL text must be in Latvian language
7. Use ONLY factual information from the provided listing and BMW database
8. Be EXTREMELY detailed about model-specific problems and high mileage issues
9. Provide DETAILED explanations for match scores and recommendations

For checklistItems:
- OBLIGĀTI izmantot model_info.common_issues datus no BMW datubāzes
- Focus on model-specific problems from the BMW database
- Describe specific symptoms and signs of each problem
- Include estimated repair costs where relevant
- Mention specific components that commonly fail
- Provide detailed inspection points for each issue

For comparison:
- OBLIGĀTI izmantot model_info.high_mileage_considerations datus no BMW datubāzes
- Focus on high mileage problems specific to this model
- Detail what typically fails at different mileage points
- Include maintenance requirements at high mileage
- Describe specific symptoms of age-related issues
- Provide cost estimates for major repairs

For summary:
- Provide a detailed technical analysis of pros and cons
- Explain exactly how the match score was calculated
- Detail why this car made it to the top 3
- Include specific risks and potential issues
- Give clear recommendations based on technical facts
- OBLIGĀTI: Norādīt, ka auto jāapskata klātienē un jāpārbauda profesionālā autoservisā pirms pirkšanas."""

app = FastAPI()

# Add CORS middleware to allow requests from your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000", "http://localhost:5173"],  # Allow all development ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the search filter model
class PriceRange(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None

class MileageRange(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None

class SearchFilters(BaseModel):
    price: PriceRange
    fuelType: Optional[str] = None
    mileage: MileageRange
    color: Optional[str] = None

# Add at the top with other constants
MAX_INPUT_TOKENS = 110000  # Maximum tokens for input
MAX_COMPLETION_TOKENS = 16000  # Maximum tokens for completion

# Database connections
def get_car_listings_db():
    try:
        db_path = os.path.join(os.path.dirname(__file__), "data", "car_listings.db")
        logger.debug(f"Attempting to connect to car_listings database at: {db_path}")
        
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found at: {db_path}")
        
        conn = sqlite3.connect(db_path)
        # Set text factory to handle UTF-8
        conn.text_factory = lambda x: str(x, 'utf-8', 'ignore')
        # Set row factory to get column names
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test the connection with correct table name
        cursor.execute("SELECT COUNT(*) FROM cars")
        count = cursor.fetchone()[0]
        logger.info(f"Successfully connected to car_listings database. Found {count} records.")
        
        return conn
    except sqlite3.Error as e:
        logger.error(f"SQLite error connecting to car_listings database: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        logger.error(f"Error connecting to car_listings database: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_bmw_cars_db():
    try:
        db_path = os.path.join(os.path.dirname(__file__), "data", "bmw_cars.db")
        logger.debug(f"Attempting to connect to bmw_cars database at: {db_path}")
        
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found at: {db_path}")
        
        conn = sqlite3.connect(db_path)
        # Set row factory to get column names
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test the connection
        cursor.execute("SELECT COUNT(*) FROM bmw_models")
        count = cursor.fetchone()[0]
        logger.info(f"Successfully connected to bmw_cars database. Found {count} records.")
        
        return conn
    except sqlite3.Error as e:
        logger.error(f"SQLite error connecting to bmw_cars database: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        logger.error(f"Error connecting to bmw_cars database: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

# Helper function to parse year from Latvian date format
def parse_year(year_str):
    if not year_str:
        return None
    
    # Extract year from string like "2011 janvāris"
    year_match = re.search(r'(\d{4})', year_str)
    if year_match:
        return int(year_match.group(1))
    return None

# Helper function to parse make and model
def parse_make_model(make_model_str):
    if not make_model_str:
        return ("Unknown", "Unknown")
    
    parts = make_model_str.split()
    if len(parts) >= 2:
        make = parts[0]
        model = ' '.join(parts[1:])
        return (make, model)
    return (make_model_str, "")

# Helper function to extract features from options string
def extract_features(options_str):
    if not options_str:
        return []
    
    # Split by pipe and remove any leading/trailing whitespace
    sections = [s.strip() for s in options_str.split('|')]
    features = []
    
    for section in sections:
        # Extract items after colon
        if ':' in section:
            items = section.split(':', 1)[1].strip()
            # Split by commas
            feature_items = [item.strip() for item in items.split(',')]
            features.extend(feature_items)
    
    return features

def calculate_priority_score(listing):
    """Calculate priority score based on year and mileage, without hard limits."""
    try:
        # Year score calculation
        year = parse_year(str(listing.get("year")))
        current_year = datetime.now().year
        
        year_score = 0
        if year:
            # Linear score based on age, but no maximum age limit
            # Newer cars get higher scores, but older cars still get considered
            year_score = (year - 1950) / (current_year - 1950)  # 1950 as a reasonable baseline
        
        # Mileage score calculation
        mileage_str = str(listing.get("mileage", "0"))
        mileage = int(''.join(filter(str.isdigit, mileage_str)) or 0)
        
        # Logarithmic scale for mileage to better handle high mileage vehicles
        # This gives a more gradual decrease in score as mileage increases
        mileage_score = 1.0
        if mileage > 0:
            # Log scale transformation: 1.0 -> 0.0 over a wide range
            # 50,000km -> 0.80 score
            # 150,000km -> 0.60 score
            # 300,000km -> 0.40 score
            # 500,000km -> 0.20 score
            # But never quite reaches 0
            mileage_score = max(0.1, 1 - (math.log10(mileage) - 4) / 3)
        
        # Combined score (50% year, 50% mileage)
        priority_score = (year_score * 0.5 + mileage_score * 0.5) * 100
        
        return priority_score
    except Exception as e:
        logger.error(f"Error calculating priority score: {e}")
        return 0

def calculate_match_score(listing, model_info, filters):
    """Calculate match score based on how well the listing matches user criteria"""
    score = 0
    weights = {
        'price': 0.40,  # Increased weight
        'mileage': 0.35,  # Increased weight
        'age': 0.25     # Kept the same
    }
    
    try:
        # Log the inputs for debugging
        logger.debug(f"Calculating match score for listing ID {listing.get('id')}")
        logger.debug(f"Filters: {json.dumps(filters.dict(), default=str)}")
        
        # Price score - better score for lower price within range
        price = int(''.join(filter(str.isdigit, str(listing.get("price", "0")))) or 0)
        price_score = 0
        
        if filters.price and (filters.price.min is not None or filters.price.max is not None):
            # Specific price range provided
            if filters.price.min is not None and filters.price.max is not None:
                # Both min and max provided
                price_range = filters.price.max - filters.price.min
                if price_range > 0:
                    # Within range - lower is better
                    if filters.price.min <= price <= filters.price.max:
                        # Linear score: min price = 1.0, max price = 0.7
                        price_score = 0.7 + 0.3 * (1 - ((price - filters.price.min) / price_range))
                    else:
                        # Outside range gets partial score based on distance
                        distance = min(abs(price - filters.price.min), abs(price - filters.price.max))
                        price_score = max(0, 0.7 - (distance / price_range))
            elif filters.price.min is not None:
                # Only min provided - higher is better (unusual case)
                if price >= filters.price.min:
                    price_score = 0.8  # Above minimum gets good score
                else:
                    # Below min gets partial score
                    price_score = max(0.3, 0.8 * (price / filters.price.min))
            elif filters.price.max is not None:
                # Only max provided - lower is better
                if price <= filters.price.max:
                    # Linear score: 0 = 1.0, max = 0.7
                    price_score = 0.7 + 0.3 * (1 - (price / filters.price.max))
                else:
                    # Above max gets lower score
                    price_score = max(0, 0.7 - 0.5 * ((price - filters.price.max) / filters.price.max))
        else:
            # No price filter - lower is generally better
            # Use a logarithmic scale: €5,000 -> 0.9, €10,000 -> 0.8, €20,000 -> 0.7
            price_score = max(0.5, 1 - (math.log10(max(5000, price)) - math.log10(5000)) / 3)
        
        score += price_score * weights['price']
        logger.debug(f"Price score: {price_score:.2f} (weight: {weights['price']:.2f})")
        
        # Mileage score - lower is better
        mileage = int(''.join(filter(str.isdigit, str(listing.get("mileage", "0")))) or 0)
        mileage_score = 0
        
        if filters.mileage and (filters.mileage.min is not None or filters.mileage.max is not None):
            # Specific mileage range provided
            if filters.mileage.min is not None and filters.mileage.max is not None:
                # Both min and max provided
                mileage_range = filters.mileage.max - filters.mileage.min
                if mileage_range > 0:
                    # Within range - lower is better
                    if filters.mileage.min <= mileage <= filters.mileage.max:
                        # Linear score: min mileage = 1.0, max mileage = 0.7
                        mileage_score = 0.7 + 0.3 * (1 - ((mileage - filters.mileage.min) / mileage_range))
                    else:
                        # Outside range gets partial score based on distance
                        distance = min(abs(mileage - filters.mileage.min), abs(mileage - filters.mileage.max))
                        mileage_score = max(0, 0.7 - (distance / mileage_range))
            elif filters.mileage.min is not None:
                # Only min provided - higher is better (unusual case)
                if mileage >= filters.mileage.min:
                    mileage_score = 0.8  # Above minimum gets good score
                else:
                    # Below min gets partial score
                    mileage_score = max(0.3, 0.8 * (mileage / filters.mileage.min))
            elif filters.mileage.max is not None:
                # Only max provided - lower is better
                if mileage <= filters.mileage.max:
                    # Linear score: 0 = 1.0, max = 0.7
                    mileage_score = 0.7 + 0.3 * (1 - (mileage / filters.mileage.max))
                else:
                    # Above max gets lower score
                    mileage_score = max(0, 0.7 - 0.5 * ((mileage - filters.mileage.max) / filters.mileage.max))
        else:
            # No mileage filter - lower is better (general preference)
            # Use a logarithmic scale: 0km -> 1.0, 100,000km -> 0.8, 200,000km -> 0.6
            mileage_score = max(0.4, 1 - (math.log10(max(1, mileage)) - 3) / 5)
        
        score += mileage_score * weights['mileage']
        logger.debug(f"Mileage score: {mileage_score:.2f} (weight: {weights['mileage']:.2f})")
        
        # Age score - newer is better
        year = parse_year(listing.get("year"))
        age_score = 0
        
        if year:
            current_year = datetime.now().year
            
            # Newer cars score higher
            if filters.price and filters.price.max is not None:
                # Consider price range when scoring age
                # More expensive cars should be newer
                expected_max_age = 5 + (15 * (1 - min(filters.price.max, 50000) / 50000))
                age = current_year - year
                age_score = max(0.3, 1 - (age / expected_max_age))
            else:
                # Without price context, use standard scale
                # 0-3 years: 1.0-0.9, 4-7 years: 0.9-0.7, 8-15 years: 0.7-0.4, 16+ years: 0.4-0.3
                age = current_year - year
                if age <= 3:
                    age_score = 1.0 - (age / 30)
                elif age <= 7:
                    age_score = 0.9 - ((age - 3) / 40)
                elif age <= 15:
                    age_score = 0.7 - ((age - 7) / 40)
                else:
                    age_score = max(0.3, 0.4 - ((age - 15) / 100))
        else:
            # No year information - below average score
            age_score = 0.4
        
        score += age_score * weights['age']
        logger.debug(f"Age score: {age_score:.2f} (weight: {weights['age']:.2f})")
        
        # Calculate final percentage score
        final_score = min(max(score * 100, 30), 100)  # Minimum 30%, maximum 100%
        logger.debug(f"Final match score: {final_score:.2f}%")
        
        return final_score
    except Exception as e:
        logger.error(f"Error calculating match score: {e}")
        logger.error(traceback.format_exc())
        return 50  # Return a neutral score on error

# Function to get model specific information with detailed data
def get_model_info(model_name, year=None, engine_type=None):
    """Fetch model information from the BMW database with improved matching."""
    try:
        conn = get_bmw_cars_db()
        cursor = conn.cursor()
        
        # Clean and normalize inputs
        clean_model = re.sub(r'[^a-zA-Z0-9]', '', model_name).lower()
        if engine_type:
            engine_type = engine_type.lower()
        
        # Extract base model number (e.g., "320" from "320i")
        base_model = re.search(r'(\d{3})', clean_model)
        base_model = base_model.group(1) if base_model else clean_model
        
        # Check if it's an electric model
        is_electric = False
        if engine_type:
            is_electric = any(term in engine_type.lower() for term in ['electric', 'elektr', 'ev', 'hybrid', 'hibrid'])
        
        # Log search parameters
        logger.info(f"Searching for model: {model_name}, base: {base_model}, year: {year}, engine: {engine_type}, electric: {is_electric}")
        
        # Build query with multiple matching criteria
        query = """
            SELECT model_name, production_years, engine_specifications, engine_code,
                   fuel_type, positives, negatives, common_problems,
                   high_mileage_considerations, original_price_eur
            FROM bmw_models 
            WHERE 1=1
        """
        params = []
        
        # Model name matching
        model_condition = """
            AND (
                LOWER(REPLACE(model_name, ' ', '')) = ? 
                OR LOWER(model_name) LIKE ? 
                OR LOWER(model_name) LIKE ?
            )
        """
        params.extend([clean_model, f"%{model_name.lower()}%", f"%{base_model}%"])
        query += model_condition
        
        # Add fuel type filtering if available
        if engine_type:
            if is_electric:
                query += " AND (LOWER(fuel_type) LIKE ? OR LOWER(engine_specifications) LIKE ?)"
                params.extend(["%electric%", "%electric%"])
            else:
                # Check for diesel/petrol/etc
                if 'diesel' in engine_type.lower() or 'd' in engine_type.lower():
                    query += " AND (LOWER(fuel_type) LIKE ? OR LOWER(engine_specifications) LIKE ?)"
                    params.extend(["%diesel%", "%diesel%"])
                elif 'petrol' in engine_type.lower() or 'benzin' in engine_type.lower() or 'gasoline' in engine_type.lower():
                    query += " AND (LOWER(fuel_type) LIKE ? OR LOWER(engine_specifications) LIKE ?)"
                    params.extend(["%petrol%", "%petrol%"])
        
        # Add year filtering if available
        if year:
            # Try to match production years that include this year
            # Format could be "2010-2015" or "2010-present" or just "2010"
            year_condition = """
                AND (
                    production_years LIKE ? OR
                    (
                        CAST(SUBSTR(production_years, 1, 4) AS INTEGER) <= ? AND
                        (
                            production_years LIKE '%present%' OR
                            CAST(SUBSTR(production_years, 6, 4) AS INTEGER) >= ?
                        )
                    )
                )
            """
            params.extend([f"%{year}%", year, year])
            query += year_condition
        
        # Order by relevance
        query += """
            ORDER BY 
                CASE 
                    WHEN LOWER(REPLACE(model_name, ' ', '')) = ? THEN 1
                    WHEN LOWER(model_name) LIKE ? THEN 2
                    ELSE 3
                END,
                LENGTH(model_name) ASC
            LIMIT 1
        """
        params.extend([clean_model, f"%{model_name.lower()}%"])
        
        logger.debug(f"Model search query: {query}")
        logger.debug(f"Model search params: {params}")
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        
        # If no match with all criteria, try more relaxed search
        if not row:
            logger.info(f"No match found with strict criteria, trying relaxed search for {model_name}")
            
            # Try just with model name
            query = """
                SELECT model_name, production_years, engine_specifications, engine_code,
                       fuel_type, positives, negatives, common_problems,
                       high_mileage_considerations, original_price_eur
                FROM bmw_models 
                WHERE LOWER(model_name) LIKE ?
                ORDER BY LENGTH(model_name) ASC
                LIMIT 1
            """
            cursor.execute(query, [f"%{base_model}%"])
            row = cursor.fetchone()
        
        if row:
            # Convert row to dict and ensure all fields are strings
            model_info = {
                "model_name": str(row[0] or ""),
                "production_years": str(row[1] or ""),
                "engine_specifications": str(row[2] or ""),
                "engine_code": str(row[3] or ""),
                "fuel_type": str(row[4] or ""),
                "positives": str(row[5] or "").split(". ") if row[5] else [],
                "negatives": str(row[6] or "").split(". ") if row[6] else [],
                "common_issues": str(row[7] or ""),
                "high_mileage_considerations": str(row[8] or ""),
                "original_price_eur": str(row[9] or "")
            }
            
            logger.info(f"Found model info for {model_name}: {model_info['model_name']}")
            return model_info
        else:
            logger.warning(f"No model info found for {model_name}, year: {year}, engine: {engine_type}")
            return {
                "positives": [],
                "negatives": [],
                "common_issues": "",
                "high_mileage_considerations": ""
            }
    except Exception as e:
        logger.error(f"Error fetching model info: {e}")
        logger.error(traceback.format_exc())
        return {
            "positives": [],
            "negatives": [],
            "common_issues": "",
            "high_mileage_considerations": ""
        }

def count_tokens(text: str) -> int:
    """Count tokens in a text string using tiktoken"""
    try:
        encoding = tiktoken.encoding_for_model("gpt-4")
        return len(encoding.encode(text))
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        # Fallback to approximate count (4 characters per token)
        return len(text) // 4

def prepare_listing_data(listing: dict, model_info: dict) -> dict:
    """Prepare listing data for OpenAI with model-specific information"""
    try:
        # Clean price and mileage
        price = str(listing.get("price", "")).replace(" ", "").replace(",", "").replace("€", "")
        mileage = str(listing.get("mileage", "")).replace(" ", "").replace(",", "").replace("km", "")
        
        # Ensure clean ID format
        listing_id = str(listing.get("id", "")).strip()
        
        # Extract features without truncation
        features = extract_features(str(listing.get("options", "")))
        
        # Include full description without truncation
        description = str(listing.get("description", ""))
        
        # Prepare model-specific information
        model_data = {
            "model_name": model_info.get("model_name", ""),
            "production_years": model_info.get("production_years", ""),
            "engine_specifications": model_info.get("engine_specifications", ""),
            "engine_code": model_info.get("engine_code", ""),
            "fuel_type": model_info.get("fuel_type", ""),
            "positives": model_info.get("positives", []),
            "negatives": model_info.get("negatives", []),
            "common_issues": model_info.get("common_issues", ""),
            "high_mileage_considerations": model_info.get("high_mileage_considerations", ""),
            "original_price_eur": model_info.get("original_price_eur", "")
        }
        
        return {
            "id": listing_id,
            "make_model": str(listing.get("make_model", "")),
            "year": parse_year(str(listing.get("year", ""))),
            "price": price,
            "mileage": mileage,
            "engine": str(listing.get("engine", "")),
            "transmission": str(listing.get("transmission", "")),
            "color": str(listing.get("color", "")),
            "body_type": str(listing.get("body_type", "")),
            "tech_inspection": str(listing.get("tech_inspection", "")),
            "features": features,
            "description": description,
            "url": str(listing.get("url", "")),
            "image": str(listing.get("image", "")),
            "model_info": model_data,  # Include model-specific information
            "priority_score": listing.get("priority_score", 0),
            "match_score": listing.get("score", 0)
        }
    except Exception as e:
        logger.error(f"Error preparing listing data: {e}")
        return {
            "id": str(listing.get("id", "")),
            "make_model": str(listing.get("make_model", "")),
            "year": 0,
            "price": "0",
            "mileage": "0",
            "engine": "",
            "transmission": "",
            "color": "",
            "features": [],
            "description": "",
            "model_info": {
                "common_issues": "",
                "high_mileage_considerations": ""
            }
        }

# API endpoint to search car listings
@app.post("/api/search")
async def search_cars(filters: SearchFilters):
    try:
        logger.info(f"Starting search with filters: {filters}")
        
        try:
            conn = get_car_listings_db()
            cursor = conn.cursor()
            
            # Build the SQL query with filters - using BETWEEN for ranges
            query = """
                SELECT * FROM cars 
                WHERE 1=1
            """
            params = []
            
            # Price range handling
            if filters.price and filters.price.min is not None and filters.price.max is not None:
                query += " AND CAST(REPLACE(REPLACE(price, ' ', ''), '€', '') AS INTEGER) BETWEEN ? AND ?"
                params.extend([filters.price.min, filters.price.max])
            elif filters.price and filters.price.min is not None:
                query += " AND CAST(REPLACE(REPLACE(price, ' ', ''), '€', '') AS INTEGER) >= ?"
                params.append(filters.price.min)
            elif filters.price and filters.price.max is not None:
                query += " AND CAST(REPLACE(REPLACE(price, ' ', ''), '€', '') AS INTEGER) <= ?"
                params.append(filters.price.max)
            
            # Mileage range handling
            if filters.mileage and filters.mileage.min is not None and filters.mileage.max is not None:
                query += " AND CAST(REPLACE(REPLACE(mileage, ' ', ''), 'km', '') AS INTEGER) BETWEEN ? AND ?"
                params.extend([filters.mileage.min, filters.mileage.max])
            elif filters.mileage and filters.mileage.min is not None:
                query += " AND CAST(REPLACE(REPLACE(mileage, ' ', ''), 'km', '') AS INTEGER) >= ?"
                params.append(filters.mileage.min)
            elif filters.mileage and filters.mileage.max is not None:
                query += " AND CAST(REPLACE(REPLACE(mileage, ' ', ''), 'km', '') AS INTEGER) <= ?"
                params.append(filters.mileage.max)
            
            # Fuel type handling - case insensitive
            if filters.fuelType:
                query += " AND LOWER(engine) LIKE LOWER(?)"
                params.append(f"%{filters.fuelType}%")
            
            # Color handling - case insensitive
            if filters.color:
                query += " AND LOWER(color) = LOWER(?)"
                params.append(filters.color)
            
            cursor.execute(query, params)
            listings = [dict(row) for row in cursor.fetchall()]
            logger.info(f"Found {len(listings)} matching listings")
            
            if not listings:
                return {"ok": True, "data": []}
            
            # Calculate priority scores for all listings
            for listing in listings:
                listing["priority_score"] = calculate_priority_score(listing)
            
            # Sort by priority score and take top 50
            listings.sort(key=lambda x: x["priority_score"], reverse=True)
            top_listings = listings[:50] if len(listings) > 50 else listings
            
            # Get model info for each listing with improved matching
            for listing in top_listings:
                make, model = parse_make_model(str(listing["make_model"]))
                year = parse_year(str(listing.get("year")))
                engine = str(listing.get("engine", ""))
                
                # Get model info with year and engine type
                model_info = get_model_info(model, year, engine)
                
                # Store model info directly with the listing
                listing["model_info"] = model_info
                
                # Calculate match score
                listing["score"] = calculate_match_score(listing, model_info, filters)
            
            # Prepare data for OpenAI
            MAX_LISTINGS = 50  # Limit number of listings to analyze
            
            # Prepare the data structure for OpenAI
            openai_data = {
                "search_criteria": {
                    "price_range": f"€{filters.price.min or 0}-{filters.price.max or 'unlimited'}",
                    "mileage_range": f"{filters.mileage.min or 0}-{filters.mileage.max or 'unlimited'} km",
                    "fuel_type": filters.fuelType or "any",
                    "color": filters.color or "any"
                },
                "valid_ids": [str(listing["id"]).strip() for listing in top_listings],
                "listings": []
            }
            
            # Add listings with their model info
            total_tokens = count_tokens(json.dumps(openai_data))
            for listing in top_listings:
                # Prepare listing data with its specific model info
                listing_data = prepare_listing_data(listing, listing["model_info"])
                listing_tokens = count_tokens(json.dumps(listing_data))
                
                if total_tokens + listing_tokens > MAX_INPUT_TOKENS:
                    break
                    
                openai_data["listings"].append(listing_data)
                total_tokens += listing_tokens
            
            logger.info(f"Prepared {len(openai_data['listings'])} listings for OpenAI analysis")
            
            # Log detailed information about the data being sent to OpenAI
            openai_logger.info("=== NEW SEARCH REQUEST ===")
            openai_logger.info(f"Search Criteria: {json.dumps(openai_data['search_criteria'], indent=2)}")
            openai_logger.info(f"Total listings found: {len(listings)}")
            openai_logger.info(f"Top listings by priority score: {len(top_listings)}")
            openai_logger.info(f"Listings being sent to OpenAI: {len(openai_data['listings'])}")
            
            # Log each listing with its model info
            for i, listing in enumerate(openai_data["listings"]):
                make_model = listing.get("make_model", "")
                year = listing.get("year", "")
                engine = listing.get("engine", "")
                model_info = listing.get("model_info", {})
                
                openai_logger.info(f"\nListing {i+1}: {make_model} ({year}) - {engine}")
                openai_logger.info(f"ID: {listing.get('id')}")
                openai_logger.info(f"Price: {listing.get('price')}")
                openai_logger.info(f"Mileage: {listing.get('mileage')}")
                openai_logger.info(f"Priority Score: {listing.get('priority_score')}")
                openai_logger.info(f"Match Score: {listing.get('match_score')}")
                
                # Log model info details
                openai_logger.info("Model Info:")
                openai_logger.info(f"  Model Name: {model_info.get('model_name', 'N/A')}")
                openai_logger.info(f"  Production Years: {model_info.get('production_years', 'N/A')}")
                openai_logger.info(f"  Fuel Type: {model_info.get('fuel_type', 'N/A')}")
                openai_logger.info(f"  Engine Specs: {model_info.get('engine_specifications', 'N/A')}")
                
                # Log the critical fields for OpenAI analysis
                openai_logger.info("Critical Fields for Analysis:")
                openai_logger.info(f"  Common Issues: {model_info.get('common_issues', 'N/A')[:200]}...")
                openai_logger.info(f"  High Mileage Considerations: {model_info.get('high_mileage_considerations', 'N/A')[:200]}...")
                openai_logger.info(f"  Positives: {model_info.get('positives', [])}")
                openai_logger.info(f"  Negatives: {model_info.get('negatives', [])}")
            
            openai_logger.info(f"Total tokens in request: {total_tokens}")
            openai_logger.info("=== END SEARCH REQUEST ===\n")
            
            # Save the full OpenAI request to a separate file for debugging
            try:
                debug_dir = os.path.join(os.path.dirname(__file__), "logs", "debug")
                os.makedirs(debug_dir, exist_ok=True)
                debug_file = os.path.join(debug_dir, f"openai_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                with open(debug_file, 'w', encoding='utf-8') as f:
                    json.dump(openai_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved full OpenAI request to {debug_file}")
            except Exception as e:
                logger.error(f"Failed to save debug file: {e}")
            
            # Step 5: Get AI analysis
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": json.dumps(openai_data)}
                    ],
                    temperature=0.2,
                    max_tokens=MAX_COMPLETION_TOKENS,
                    presence_penalty=0.0,
                    frequency_penalty=0.0
                )
                
                # Log the raw response for debugging
                logger.debug(f"OpenAI raw response: {response.choices[0].message.content}")
                
                # Save the full OpenAI response to a separate file for debugging
                try:
                    debug_dir = os.path.join(os.path.dirname(__file__), "logs", "debug")
                    os.makedirs(debug_dir, exist_ok=True)
                    debug_file = os.path.join(debug_dir, f"openai_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(response.choices[0].message.content)
                    logger.info(f"Saved full OpenAI response to {debug_file}")
                    
                    # Also log to the openai_logger
                    openai_logger.info("\n=== OPENAI RESPONSE ===")
                    openai_logger.info(f"Response received at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    openai_logger.info("Selected IDs:")
                except Exception as e:
                    logger.error(f"Failed to save response debug file: {e}")
                
                # Extract car IDs and analyses
                content = response.choices[0].message.content
                id_match = re.search(r'SELECTED_IDS:\s*\[(.*?)\]', content)
                if not id_match:
                    logger.error("No SELECTED_IDS found in response")
                    raise ValueError("No SELECTED_IDS found in response")
                
                selected_ids = [id.strip(' "\'') for id in id_match.group(1).split(',')]
                logger.info(f"Found selected IDs: {selected_ids}")
                
                # Log selected IDs to openai_logger
                openai_logger.info(f"Selected IDs: {selected_ids}")
                
                # Extract analysis blocks
                analysis_blocks = []
                for car_id in selected_ids:
                    analysis_match = re.search(rf'{{"id":\s*"{car_id}",\s*"analysis":\s*({{.*?}})\s*}}', content, re.DOTALL)
                    if analysis_match:
                        analysis_blocks.append((car_id, analysis_match.group(1)))
                    else:
                        logger.warning(f"Could not find analysis block for car ID {car_id}")
                
                if not analysis_blocks:
                    logger.error("No valid analysis blocks found in response")
                    raise ValueError("No valid analysis blocks found in response")
                
                logger.info(f"Successfully extracted {len(analysis_blocks)} analysis blocks")
                
                # Process each analysis block
                recommendations = []
                for car_id, analysis_json in analysis_blocks:
                    try:
                        # Clean up the JSON
                        analysis_json = re.sub(r'//.*', '', analysis_json)
                        analysis_json = re.sub(r',\s*}', '}', analysis_json)
                        analysis_json = re.sub(r',\s*]', ']', analysis_json)
                        
                        analysis = json.loads(analysis_json)
                        
                        # Find the corresponding listing
                        listing = next((l for l in top_listings if str(l["id"]).strip() == str(car_id).strip()), None)
                        
                        if not listing:
                            logger.warning(f"No listing found for car ID {car_id}")
                            continue
                        
                        make, model = parse_make_model(str(listing["make_model"]))
                        year = parse_year(str(listing["year"]))
                        
                        # Get model info directly from the listing
                        model_info = listing.get("model_info", {})
                        
                        # Ensure strengths is a list
                        strengths = analysis.get("strengths", [])
                        if not isinstance(strengths, list):
                            strengths = [s.strip() for s in str(strengths).split(".") if s.strip()]
                        if not strengths and model_info.get("positives"):
                            strengths = model_info["positives"]
                        
                        # Ensure considerations is a list
                        considerations = analysis.get("considerations", [])
                        if not isinstance(considerations, list):
                            considerations = [c.strip() for c in str(considerations).split(".") if c.strip()]
                        if not considerations and model_info.get("negatives"):
                            considerations = model_info["negatives"]
                        
                        # Format checklist items
                        checklist_items = analysis.get("checklistItems", [])
                        if isinstance(checklist_items, str):
                            checklist_items = [item.strip() for item in checklist_items.split("\n") if item.strip()]
                        
                        # Create recommendation
                        recommendation = {
                            "carDetails": {
                                "id": str(listing["id"]),
                                "make": make,
                                "model": model,
                                "title": f"{make} {model} ({year})",
                                "price": str(listing["price"]),
                                "year": year,
                                "mileage": str(listing["mileage"]),
                                "fuelType": str(listing["engine"]),
                                "transmission": str(listing["transmission"]),
                                "color": str(listing["color"]),
                                "condition": "Used",
                                "location": "Latvia",
                                "sellerType": "Private",
                                "imageUrl": str(listing.get("image", "")),
                                "url": str(listing.get("url", "")),
                                "features": extract_features(str(listing.get("options", ""))),
                                "engineDetails": str(listing["engine"]),
                                "bodyType": str(listing["body_type"]),
                                "technicalInspection": str(listing.get("tech_inspection", "")),
                                "description": str(listing.get("description", ""))
                            },
                            "aiAnalysis": {
                                "matchScore": int(analysis.get("matchScore", 70)),
                                "strengths": strengths,
                                "considerations": considerations,
                                "commonProblems": str(analysis.get("commonProblems", model_info.get("common_issues", ""))),
                                "highMileageConcerns": str(analysis.get("highMileageConcerns", model_info.get("high_mileage_considerations", ""))),
                                "valueAssessment": str(analysis.get("valueAssessment", "")),
                                "recommendation": str(analysis.get("recommendation", "")),
                                "summary": str(analysis.get("summary", "")) + "\n\n" + str(analysis.get("recommendation", "")),
                                "pros": strengths,
                                "cons": considerations
                            },
                            "checklistItems": "\n".join(checklist_items) if checklist_items else str(model_info.get("common_issues", "")),
                            "comparison": str(analysis.get("comparison", "")) or str(model_info.get("high_mileage_considerations", "")),
                            "summary": str(analysis.get("summary", "")) + "\n\n" + str(analysis.get("recommendation", ""))
                        }
                        
                        recommendations.append(recommendation)
                        logger.info(f"Successfully processed recommendation for car {car_id}")
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing analysis JSON for car {car_id}: {e}")
                        logger.error(f"Problematic JSON: {analysis_json}")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing car {car_id}: {e}")
                        logger.error(traceback.format_exc())
                        continue
                
                if not recommendations:
                    raise ValueError("No valid recommendations could be created")
                
                return {"ok": True, "data": recommendations}
                
            except openai.BadRequestError as e:
                logger.error(f"OpenAI BadRequestError: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="Error analyzing car listings. Please try with fewer filters or a smaller price range."
                )
            except openai.RateLimitError as e:
                logger.error(f"OpenAI RateLimitError: {e}")
                raise HTTPException(
                    status_code=429,
                    detail="Service is currently busy. Please try again in a few minutes."
                )
            except Exception as e:
                logger.error(f"Error getting AI analysis: {e}")
                logger.error(traceback.format_exc())
                raise HTTPException(
                    status_code=500,
                    detail="Error analyzing car listings. Please try again."
                )
            
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Error: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="An error occurred while processing your request")
            
    except Exception as e:
        logger.error(f"Error in search_cars: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error analyzing car listings. Please try again.")

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "AutoAdvisor API is running!"}

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "server:app",
        host="127.0.0.1",  # Listen on localhost
        port=8000,
        reload=True,
        log_level="debug"
    )

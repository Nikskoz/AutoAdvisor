# AutoAdvisor

A sophisticated RAG (Retrieval-Augmented Generation) web application that helps users find and analyze car listings in Latvia. The application combines structured data from databases with AI-powered analysis to provide detailed recommendations based on user preferences and model-specific information. Currently supports only BMW listings and BMW model-specific information.

## Features

- **Smart Search**: Filter cars by:
  - Price range
  - Mileage
  - Fuel type
  - Color
- **AI-Powered Analysis**: 
  - Detailed strengths and considerations for each car
  - Model-specific information and common issues
  - Personalized recommendations
  - Match score calculation
  - High mileage concerns
  - Comprehensive comparison with similar models
- **Latvian Language Support**: 
  - User interface in Latvian
  - Search using Latvian terms
  - AI analysis in Latvian
- **Rich Car Information**:
  - Technical specifications
  - Service history
  - Features and options
  - Current condition
  - Technical inspection status

## Technology Stack

### Frontend
- React with TypeScript
- Vite for build tooling
- TailwindCSS for styling
- Shadcn/ui for UI components
- Lucide React for icons

### Backend
- FastAPI (Python)
- SQLite databases:
  - `car_listings.db`: Current car listings
  - `bmw_cars.db`: BMW model information
- OpenAI GPT-4o-mini for AI analysis
- Environment variables for configuration

## Project Structure

```
├── src/                    # Frontend source code
│   ├── components/         # React components
│   │   ├── CarCard.tsx    # Car listing card component
│   │   ├── SearchForm.tsx # Search form component
│   │   └── ui/           # UI components
│   ├── lib/               # Utilities and API clients
│   │   ├── api.ts        # API client
│   │   └── types.ts      # TypeScript types
│   ├── pages/            # Page components
│   └── hooks/            # Custom React hooks
├── backend/              # Python backend
│   ├── server.py        # Main FastAPI server
│   ├── data/            # Database files
│   └── .env            # Environment configuration
├── public/              # Static assets
└── package.json        # Frontend dependencies
```

## How It Works

### 1. Search Process
1. User submits search criteria through the frontend
2. Backend processes the request and queries the `car_listings.db`
3. Initial filtering is applied based on:
   - Price range
   - Mileage range
   - Fuel type
   - Color
4. Results are retrieved and prepared for analysis

### 2. Model Matching
1. For each car listing, the system:
   - Extracts make and model information
   - Queries `bmw_cars.db` for matching model information
   - Considers production years and engine specifications
   - Matches based on:
     - Model name similarity
     - Production year compatibility
     - Engine code matching
     - Fuel type matching

### 3. Match Score Calculation
The match score is calculated based on multiple factors:
1. **Price Match (30%)**:
   - Calculates how well the price fits within the user's range
   - Uses a linear scale for scoring

2. **Mileage Match (20%)**:
   - Evaluates mileage against user's preferred range
   - Uses a logarithmic scale to account for high-mileage vehicles
   - Considers the car's age in relation to mileage

3. **Model Match (20%)**:
   - Based on the accuracy of model matching
   - Considers production year compatibility
   - Accounts for engine and fuel type matches

4. **Features Match (15%)**:
   - Evaluates available features against user preferences
   - Considers optional equipment

5. **Condition Match (15%)**:
   - Based on technical inspection status
   - Considers service history
   - Evaluates overall condition

### 4. AI Analysis
The system uses OpenAI's GPT-4o-mini model to generate:
1. **Strengths and Considerations**:
   - Based on model-specific information
   - Current condition and features
   - Market position

2. **Common Problems**:
   - Model-specific known issues
   - Age-related concerns
   - Maintenance requirements

3. **High Mileage Concerns**:
   - Specific to the model
   - Based on current mileage
   - Maintenance recommendations

4. **Value Assessment**:
   - Market position analysis
   - Price comparison
   - Feature value evaluation

### 5. OpenAI Data Flow and Processing

#### Data Preparation
1. **Car Listing Data**:
   ```json
   {
     "carDetails": {
       "id": "string",
       "make": "string",
       "model": "string",
       "price": number,
       "year": number,
       "mileage": number,
       "fuelType": "string",
       "transmission": "string",
       "features": ["string"],
       "description": "string",
       "technicalInspection": "string"
     }
   }
   ```

2. **Model Information**:
   ```json
   {
     "modelInfo": {
       "model_name": "string",
       "production_years": "string",
       "engine_specifications": "string",
       "engine_code": "string",
       "fuel_type": "string",
       "positives": "string",
       "negatives": "string",
       "common_problems": "string",
       "high_mileage_considerations": "string"
     }
   }
   ```

3. **User Preferences**:
   ```json
   {
     "userPreferences": {
       "priceRange": { "min": number, "max": number },
       "mileageRange": { "min": number, "max": number },
       "fuelType": "string",
       "color": "string"
     }
   }
   ```

#### OpenAI Request
1. **Token Management**:
   - Maximum input tokens: 110,000
   - Maximum completion tokens: 16,000
   - Uses tiktoken for token counting

2. **Prompt Structure**:
   ```json
   {
     "messages": [
       {
         "role": "system",
         "content": "You are a BMW car expert..."
       },
       {
         "role": "user",
         "content": {
           "carDetails": {...},
           "modelInfo": {...},
           "userPreferences": {...}
         }
       }
     ]
   }
   ```

#### OpenAI Response
1. **Raw Response**:
   ```json
   {
     "matchScore": number,
     "strengths": ["string"],
     "considerations": ["string"],
     "valueAssessment": "string",
     "recommendation": "string",
     "commonProblems": "string",
     "highMileageConcerns": "string",
     "checklistItems": "string",
     "comparison": "string",
     "summary": "string"
   }
   ```

#### Frontend Processing
1. **API Client** (`src/lib/api.ts`):
   - Transforms OpenAI response into frontend-friendly format
   - Handles error cases and fallbacks
   - Validates data structure

2. **Type Definitions** (`src/lib/types.ts`):
   ```typescript
   interface AIRecommendation {
     carDetails: CarDetails;
     aiAnalysis: AIAnalysis;
     checklistItems: string;
     comparison: string;
     summary: string;
   }
   ```

3. **Component Display** (`src/components/CarCard.tsx`):
   - Renders car details in a card format
   - Displays AI analysis in sections:
     - Strengths and considerations
     - Common problems
     - High mileage concerns
     - Value assessment
     - Checklist items
     - Comparison
     - Summary

4. **Data Flow**:
   ```
   OpenAI Response
   ↓
   API Client Processing
   ↓
   Type Validation
   ↓
   Component Rendering
   ↓
   User Interface
   ```

## Setup Instructions

### Prerequisites
- Node.js (v18 or higher)
- Python 3.8+
- SQLite3
- OpenAI API key

### Frontend Setup
1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

### Backend Setup
1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the backend directory with:
```
OPENAI_API_KEY=your_api_key_here
```

4. Start the backend server:
```bash
cd backend
uvicorn server:app --reload
```

## Database Structure

### car_listings.db
Contains current car listings with fields:
- id
- fetch_time
- url
- price
- make_model
- year
- engine
- transmission
- mileage
- color
- body_type
- tech_inspection
- description
- options
- image

### bmw_cars.db
Contains BMW model information with fields:
- id
- model_name
- production_years
- engine_specifications
- engine_code
- fuel_type
- positives
- negatives
- common_problems
- high_mileage_considerations
- original_price_eur

## API Endpoints

### POST /api/search
Main search endpoint that accepts:
```json
{
  "price": {
    "min": number | null,
    "max": number | null
  },
  "fuelType": string | null,
  "mileage": {
    "min": number | null,
    "max": number | null
  },
  "color": string | null
}
```

Returns:
```json
{
  "ok": boolean,
  "data": [
    {
      "carDetails": {...},
      "aiAnalysis": {...},
      "checklistItems": string,
      "comparison": string,
      "summary": string
    }
  ]
}
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

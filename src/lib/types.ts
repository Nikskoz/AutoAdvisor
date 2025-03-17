export interface PriceRange {
  min: number | null;
  max: number | null;
}

export interface MileageRange {
  min: number | null;
  max: number | null;
}

export interface SearchFilters {
  price: PriceRange;
  fuelType: string | null;
  mileage: MileageRange;
  color: string | null;
}

export interface CarListing {
  id: string;
  make: string;
  model: string;
  title?: string;
  price: number;
  year: number;
  mileage: number;
  fuelType: string;
  transmission: string;
  color: string;
  condition?: string;
  location: string;
  sellerType?: string;
  imageUrl: string;
  url: string;
  features: string[];
  engineDetails?: string;
  fuelEconomy?: string;
  drivetrain?: string;
  history?: string;
  interiorFeatures?: string;
  description?: string;
  technicalInspection?: string;
  options?: string;
  bodyType?: string;
}

export interface BMWModelInfo {
  id: number;
  model_name: string;
  production_years: string;
  engine_specifications: string;
  engine_code: string;
  fuel_type: string;
  positives: string;
  negatives: string;
  common_problems: string;
  high_mileage_considerations: string;
  original_price_eur: string;
}

export interface AIAnalysis {
  matchScore: number;
  strengths: string[];
  considerations: string[];
  valueAssessment: string;
  recommendation: string;
  commonProblems?: string;
  highMileageConcerns?: string;
}

export interface AIRecommendation {
  carDetails: CarListing;
  aiAnalysis: AIAnalysis;
  reasoning?: string;
  specifications?: string;
  prosAndCons?: string;
  checklistItems?: string;
  comparison?: string;
  summary?: string;
}

export interface SearchResults {
  recommendations: AIRecommendation[];
  isLoading: boolean;
  error: string | null;
}

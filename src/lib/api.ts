import { SearchFilters, AIRecommendation, CarListing } from './types';

// Function to fetch car listings from the Python backend server
export const searchCarListings = async (filters: SearchFilters): Promise<AIRecommendation[]> => {
  console.log('Starting search with filters:', JSON.stringify(filters, null, 2));
  
  try {
    // Try to fetch from the real backend with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000); // 120 second timeout (increased from 30s)
    
    console.log('Sending request to backend...');
    const response = await fetch('http://localhost:8000/api/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(filters),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    console.log('Received response:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error response:', {
        status: response.status,
        statusText: response.statusText,
        body: errorText
      });
      throw new Error(`API request failed: ${errorText}`);
    }
    
    const responseData = await response.json();
    console.log('Successfully parsed response data:', responseData);
    
    if (!responseData.ok || !Array.isArray(responseData.data)) {
      console.error('Invalid response format:', responseData);
      throw new Error('Invalid response format: expected {ok: true, data: Array}');
    }
    
    const data = responseData.data;
    
    // Transform and validate the API response
    const recommendations = data.map((item: any, index: number) => {
      console.log(`Processing result ${index + 1}:`, item);
      
      if (!item.carDetails) {
        console.error(`Missing carDetails in item ${index + 1}:`, item);
        throw new Error('Missing carDetails in response item');
      }
      
      return {
        carDetails: {
          id: item.carDetails.id || '',
          make: item.carDetails.make || '',
          model: item.carDetails.model || '',
          title: item.carDetails.title || '',
          price: Number(item.carDetails.price) || 0,
          year: Number(item.carDetails.year) || 0,
          mileage: Number(item.carDetails.mileage) || 0,
          fuelType: item.carDetails.fuelType || '',
          transmission: item.carDetails.transmission || '',
          color: item.carDetails.color || '',
          condition: item.carDetails.condition || 'Used',
          location: item.carDetails.location || 'Latvia',
          sellerType: item.carDetails.sellerType || 'Private',
          imageUrl: item.carDetails.imageUrl || '',
          url: item.carDetails.url || '',
          features: Array.isArray(item.carDetails.features) ? item.carDetails.features : [],
          engineDetails: item.carDetails.engineDetails || '',
          bodyType: item.carDetails.bodyType || '',
          technicalInspection: item.carDetails.technicalInspection || '',
          description: item.carDetails.description || ''
        },
        aiAnalysis: {
          matchScore: Number(item.aiAnalysis?.matchScore) || 0,
          strengths: Array.isArray(item.aiAnalysis?.strengths) ? item.aiAnalysis.strengths : [],
          considerations: Array.isArray(item.aiAnalysis?.considerations) ? item.aiAnalysis.considerations : [],
          valueAssessment: item.aiAnalysis?.valueAssessment || '',
          recommendation: item.aiAnalysis?.recommendation || 'Consider this vehicle based on your criteria',
          commonProblems: item.aiAnalysis?.commonProblems || '',
          highMileageConcerns: item.aiAnalysis?.highMileageConcerns || ''
        },
        checklistItems: item.checklistItems || '',
        comparison: item.comparison || '',
        summary: item.summary || ''
      };
    });
    
    console.log('Successfully processed all results:', recommendations);
    return recommendations;
    
  } catch (error) {
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        console.error('Request timed out after 120 seconds');
        throw new Error('Search request timed out. Please try again.');
      }
      console.error('Error fetching car listings:', error.message);
    } else {
      console.error('Unknown error:', error);
    }
    
    throw error;
  }
};


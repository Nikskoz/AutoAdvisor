
import React from 'react';
import { AIRecommendation } from '@/lib/types';
import { AlertCircle, Lightbulb, ShieldCheck } from 'lucide-react';

interface CarDetailsExpandedProps {
  recommendation: AIRecommendation;
}

const CarDetailsExpanded: React.FC<CarDetailsExpandedProps> = ({ recommendation }) => {
  const { carDetails, aiAnalysis } = recommendation;
  
  // Create a title if it doesn't exist
  const title = carDetails.title || `${carDetails.make} ${carDetails.model}`;

  return (
    <div className="mt-6 space-y-6 animate-fade-in">
      <div>
        <h4 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
          <span className="w-6 h-6 flex items-center justify-center rounded-full bg-blue-600 text-white mr-2">
            <span className="text-xs">1</span>
          </span>
          Specifications & Features
        </h4>
        <p className="text-gray-700 leading-relaxed">
          {recommendation.specifications || `${title} features ${carDetails.features.join(', ')}.`}
        </p>
        
        {carDetails.features.length > 0 && (
          <div className="mt-3">
            <h5 className="font-medium text-gray-700 mb-2">Key Features:</h5>
            <div className="flex flex-wrap gap-2">
              {carDetails.features.slice(0, 8).map((feature, i) => (
                <div key={i} className="bg-gray-100 px-3 py-1 rounded-full text-sm text-gray-700">
                  {feature}
                </div>
              ))}
              {carDetails.features.length > 8 && (
                <div className="bg-gray-100 px-3 py-1 rounded-full text-sm text-gray-700">
                  +{carDetails.features.length - 8} more
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      {carDetails.description && (
        <div>
          <h4 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
            <Lightbulb size={20} className="text-blue-600 mr-2" />
            Seller's Description
          </h4>
          <p className="text-gray-700 leading-relaxed">
            {carDetails.description.length > 300 
              ? `${carDetails.description.substring(0, 300)}...` 
              : carDetails.description}
          </p>
        </div>
      )}
      
      <div>
        <h4 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
          <span className="w-6 h-6 flex items-center justify-center rounded-full bg-blue-600 text-white mr-2">
            <span className="text-xs">2</span>
          </span>
          Pros & Cons
        </h4>
        <div className="space-y-3">
          <div>
            <h5 className="font-medium text-green-700">Strengths:</h5>
            <ul className="list-disc pl-5 space-y-1 mt-2">
              {aiAnalysis.strengths.map((strength, i) => (
                <li key={i} className="text-gray-700">{strength}</li>
              ))}
            </ul>
          </div>
          <div>
            <h5 className="font-medium text-amber-700">Considerations:</h5>
            <ul className="list-disc pl-5 space-y-1 mt-2">
              {aiAnalysis.considerations.map((consideration, i) => (
                <li key={i} className="text-gray-700">{consideration}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
      
      <div>
        <h4 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
          <span className="w-6 h-6 flex items-center justify-center rounded-full bg-blue-600 text-white mr-2">
            <span className="text-xs">3</span>
          </span>
          Potential Issues & What to Check
        </h4>
        <div className="bg-amber-50 border border-amber-200 rounded-md p-4">
          <div className="flex items-start">
            <AlertCircle size={20} className="text-amber-500 mt-0.5 mr-2 flex-shrink-0" />
            <p className="text-gray-700 leading-relaxed">
              {recommendation.checklistItems || "Be sure to check the vehicle's service history and have a mechanic inspect it before purchase."}
            </p>
          </div>
        </div>
      </div>
      
      <div>
        <h4 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
          <span className="w-6 h-6 flex items-center justify-center rounded-full bg-blue-600 text-white mr-2">
            <span className="text-xs">4</span>
          </span>
          Market Comparison
        </h4>
        <p className="text-gray-700 leading-relaxed">
          {recommendation.comparison || aiAnalysis.valueAssessment}
        </p>
      </div>
      
      <div>
        <h4 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
          <span className="w-6 h-6 flex items-center justify-center rounded-full bg-blue-600 text-white mr-2">
            <span className="text-xs">5</span>
          </span>
          Final Thoughts
        </h4>
        <div className="bg-gray-50 p-4 rounded-md border border-gray-100">
          <p className="text-gray-800 font-medium leading-relaxed">
            {recommendation.summary || aiAnalysis.recommendation}
          </p>
        </div>
      </div>
    </div>
  );
};

export default CarDetailsExpanded;

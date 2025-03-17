
import React from 'react';
import { CarListing } from '@/lib/types';
import { ShieldCheck } from 'lucide-react';

interface CarHeaderProps {
  carDetails: CarListing;
  title: string;
}

const CarHeader: React.FC<CarHeaderProps> = ({ carDetails, title }) => {
  return (
    <>
      <div className="image-container h-48 relative">
        <img 
          src={carDetails.imageUrl || '/placeholder.svg'} 
          alt={title} 
          className="w-full h-full object-cover"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = '/placeholder.svg';
          }}
        />
        {carDetails.technicalInspection && (
          <div className="absolute top-3 right-3 px-3 py-1 bg-green-100 rounded-full text-sm font-medium text-green-700 flex items-center">
            <ShieldCheck size={16} className="mr-1" />
            Tech inspection: {carDetails.technicalInspection}
          </div>
        )}
      </div>
      
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-lg font-bold text-gray-900 line-clamp-1">{title}</h3>
          <p className="text-lg font-bold text-blue-600 mt-1">€{carDetails.price.toLocaleString()}</p>
        </div>
        <div className="px-2 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-700">
          {carDetails.sellerType || 'Private'}
        </div>
      </div>
    </>
  );
};

export default CarHeader;

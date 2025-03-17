
import React from 'react';
import { CarListing } from '@/lib/types';
import { Calendar, Gauge, MapPin, Settings, Wrench } from 'lucide-react';

interface CarSpecsProps {
  carDetails: CarListing;
}

const CarSpecs: React.FC<CarSpecsProps> = ({ carDetails }) => {
  return (
    <div className="mb-4">
      <div className="grid grid-cols-2 gap-2 mb-3 text-sm">
        <div className="flex items-center gap-1 text-gray-600">
          <Calendar size={16} className="text-blue-600" />
          <span>{carDetails.year}</span>
        </div>
        <div className="flex items-center gap-1 text-gray-600">
          <Gauge size={16} className="text-blue-600" />
          <span>{carDetails.mileage.toLocaleString()} km</span>
        </div>
        <div className="flex items-center gap-1 text-gray-600">
          <Wrench size={16} className="text-blue-600" />
          <span>{carDetails.fuelType}, {carDetails.transmission}</span>
        </div>
        <div className="flex items-center gap-1 text-gray-600">
          <MapPin size={16} className="text-blue-600" />
          <span className="truncate">{carDetails.location}</span>
        </div>
      </div>
      
      {carDetails.bodyType && (
        <div className="flex items-center gap-1 text-sm text-gray-600">
          <Settings size={16} className="text-blue-600" />
          <span>Body type: {carDetails.bodyType}</span>
        </div>
      )}
    </div>
  );
};

export default CarSpecs;

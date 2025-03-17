import React, { useState } from 'react';
import { SearchFilters } from '@/lib/types';
import { Button } from './ui/button';
import { Search, Loader2 } from 'lucide-react';

interface SearchFormProps {
  onSearch: (filters: SearchFilters) => void;
  isLoading: boolean;
}

const SearchForm: React.FC<SearchFormProps> = ({ onSearch, isLoading }) => {
  const [priceMin, setPriceMin] = useState<string>('');
  const [priceMax, setPriceMax] = useState<string>('');
  const [fuelType, setFuelType] = useState<string>('');
  const [mileageMin, setMileageMin] = useState<string>('');
  const [mileageMax, setMileageMax] = useState<string>('');
  const [color, setColor] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Ensure we have at least one filter
    if (!priceMin && !priceMax && !fuelType && !mileageMin && !mileageMax && !color) {
      alert('Lūdzu ievadiet vismaz vienu meklēšanas kritēriju');
      return;
    }
    
    const filters: SearchFilters = {
      price: {
        min: priceMin ? parseInt(priceMin) : null,
        max: priceMax ? parseInt(priceMax) : null
      },
      fuelType: fuelType || null,
      mileage: {
        min: mileageMin ? parseInt(mileageMin) : null,
        max: mileageMax ? parseInt(mileageMax) : null
      },
      color: color || null
    };
    
    console.log('Submitting search with filters:', filters);  // Debug log
    onSearch(filters);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700" htmlFor="price-range">
            Cena (€)
          </label>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="number"
              id="price-min"
              placeholder="Min"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-bmw-blue"
              value={priceMin}
              onChange={(e) => setPriceMin(e.target.value)}
              disabled={isLoading}
            />
            <input
              type="number"
              id="price-max"
              placeholder="Max"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-bmw-blue"
              value={priceMax}
              onChange={(e) => setPriceMax(e.target.value)}
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700" htmlFor="fuel-type">
            Degvielas tips
          </label>
          <select
            id="fuel-type"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-bmw-blue"
            value={fuelType}
            onChange={(e) => setFuelType(e.target.value)}
            disabled={isLoading}
          >
            <option value="">Jebkurš</option>
            <option value="Dīzelis">Dīzelis</option>
            <option value="Benzīns">Benzīns</option>
            <option value="Hibrīds">Hibrīds</option>
            <option value="Elektriskais">Elektriskais</option>
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700" htmlFor="mileage-range">
            Nobraukums (km)
          </label>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="number"
              id="mileage-min"
              placeholder="Min"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-bmw-blue"
              value={mileageMin}
              onChange={(e) => setMileageMin(e.target.value)}
              disabled={isLoading}
            />
            <input
              type="number"
              id="mileage-max"
              placeholder="Max"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-bmw-blue"
              value={mileageMax}
              onChange={(e) => setMileageMax(e.target.value)}
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700" htmlFor="color">
            Krāsa
          </label>
          <select
            id="color"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-bmw-blue"
            value={color}
            onChange={(e) => setColor(e.target.value)}
            disabled={isLoading}
          >
            <option value="">Jebkura</option>
            <option value="Melna">Melna</option>
            <option value="Melnametālika">Melnametālika</option>
            <option value="Balta">Balta</option>
            <option value="Baltametālika">Baltametālika</option>
            <option value="Brūna">Brūna</option>
            <option value="Brūnametālika">Brūnametālika</option>
            <option value="Dzeltena">Dzeltena</option>
            <option value="Dzeltenametālika">Dzeltenametālika</option>
            <option value="Gaiši zila">Gaiši zila</option>
            <option value="Gaiši zilametālika">Gaiši zilametālika</option>
            <option value="Oranža">Oranža</option>
            <option value="Oranžametālika">Oranžametālika</option>
            <option value="Pelēka">Pelēka</option>
            <option value="Pelēkametālika">Pelēkametālika</option>
            <option value="Sarkana">Sarkana</option>
            <option value="Sarkanametālika">Sarkanametālika</option>
            <option value="Sudraba">Sudraba</option>
            <option value="Sudrabametālika">Sudrabametālika</option>
            <option value="Tumši sarkana">Tumši sarkana</option>
            <option value="Tumši sarkanametālika">Tumši sarkanametālika</option>
          </select>
        </div>
      </div>

      <div className="flex justify-center pt-6">
        <Button
          type="submit"
          disabled={isLoading}
          className="w-48 h-12 bg-blue-600 hover:bg-blue-700 text-white text-lg font-semibold rounded-lg shadow-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-6 w-6 animate-spin" />
              <span>Meklēju...</span>
            </>
          ) : (
            <>
              <Search className="h-6 w-6" />
              <span>Meklēt</span>
            </>
          )}
        </Button>
      </div>
    </form>
  );
};

export default SearchForm;

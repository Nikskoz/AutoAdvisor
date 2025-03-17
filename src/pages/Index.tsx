import React, { useState } from 'react';
import SearchForm from '@/components/SearchForm';
import CarCard from '@/components/CarCard';
import LoadingIndicator from '@/components/LoadingIndicator';
import { SearchFilters, AIRecommendation } from '@/lib/types';
import { searchCarListings } from '@/lib/api';
import { Info, Car } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

const Index = () => {
  const [results, setResults] = useState<AIRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (filters: SearchFilters) => {
    setIsLoading(true);
    setError(null);
    setResults([]);
    
    try {
      console.log('Searching with filters:', filters);
      const data = await searchCarListings(filters);
      console.log('Received data:', data);
      setResults(data);
      setHasSearched(true);
    } catch (err) {
      console.error('Error searching car listings:', err);
      setError('An error occurred while searching. Please try again.');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-center items-center">
            <Car className="h-8 w-8 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900 ml-2">AutoAdvisor</h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <section className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Atrodiet savu ideālo lietoto automašīnu</h2>
            <p className="text-gray-600 mb-6">
              Pastāstiet mums, ko meklējat, un mūsu mākslīgais intelekts analizēs tūkstošiem sludinājumu, lai atrastu jums piemērotākos.
            </p>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 text-left">
              <div className="flex">
                <Info size={24} className="text-blue-600 mr-3 flex-shrink-0" />
                <p className="text-sm text-gray-700">
                  Izmantojiet tālāk esošos filtrus, lai sašaurinātu meklēšanu. Filtru varat atstāt tukšu, ja jums nav noteiktas preferences. Meklēšana tiks uzsākta, ja tiks izmantots vismaz viens filtrs.
                </p>
              </div>
            </div>
          </div>
          
          <SearchForm onSearch={handleSearch} isLoading={isLoading} />
        </section>

        <section className="space-y-6">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <LoadingIndicator />
              <p className="mt-4 text-gray-600">Meklējam jums piemērotākos sludinājumus...</p>
            </div>
          ) : error ? (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          ) : results.length > 0 ? (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Jums ieteiktie sludinājumi</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.map((recommendation, index) => (
                  <CarCard 
                    key={recommendation.carDetails.id} 
                    recommendation={recommendation}
                    index={index}
                  />
                ))}
              </div>
            </div>
          ) : hasSearched ? (
            <div className="text-center py-12">
              <h3 className="text-xl font-medium text-gray-900 mb-2">Nav atrastas atbilstības</h3>
              <p className="text-gray-600">Mēģiniet pielāgot meklēšanas kritērijus, lai redzētu vairāk rezultātu.</p>
            </div>
          ) : null}
        </section>
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-500 text-sm">
            AutoAdvisor - Palīdzēs jums atrast lietotu automašīnu ar MI ieteikumiem
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;

import React, { useState } from 'react';
import { AIRecommendation } from '@/lib/types';
import ReactMarkdown from 'react-markdown';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { ChevronDown, ChevronUp, CheckCircle2, AlertTriangle, Gauge, Award, ExternalLink } from 'lucide-react';
import { Badge } from './ui/badge';

interface CarCardProps {
  recommendation: AIRecommendation;
  index: number;
}

const CarCard: React.FC<CarCardProps> = ({ recommendation, index }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const { carDetails, aiAnalysis, specifications, prosAndCons, checklistItems, comparison, summary } = recommendation;
  
  const title = carDetails.title || `${carDetails.make} ${carDetails.model}`;

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  return (
    <Card className="overflow-hidden bg-white shadow-lg rounded-xl">
      <div className="relative aspect-[16/9]">
        <img
          src={carDetails.imageUrl}
          alt={carDetails.title}
          className="w-full h-full object-cover"
        />
        {carDetails.technicalInspection && (
          <div className="absolute top-4 right-4">
            <Badge variant="secondary" className="flex items-center gap-1 bg-green-100 text-green-700">
              <CheckCircle2 className="h-3 w-3" />
              TA līdz {carDetails.technicalInspection}
            </Badge>
          </div>
        )}
      </div>

      <div className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-xl font-bold text-gray-900">{title}</h3>
            <p className="text-2xl font-bold text-bmw-blue">{formatPrice(carDetails.price)}</p>
          </div>
          <div className="text-right">
            <Badge variant="outline" className="mb-2">{carDetails.sellerType}</Badge>
            {aiAnalysis.matchScore && (
              <div className="flex items-center gap-1 text-green-600">
                <Award className="h-4 w-4" />
                <span className="font-medium">{aiAnalysis.matchScore}% sakritība</span>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
          <div>
            <p className="text-gray-600">Gads</p>
            <p className="font-medium">{carDetails.year}</p>
          </div>
          <div>
            <p className="text-gray-600">Nobraukums</p>
            <p className="font-medium">{carDetails.mileage.toLocaleString()} km</p>
          </div>
          <div>
            <p className="text-gray-600">Motors un transmisija</p>
            <p className="font-medium">{carDetails.fuelType}, {carDetails.transmission}</p>
          </div>
          <div>
            <p className="text-gray-600">Lokācija</p>
            <p className="font-medium">{carDetails.location}</p>
          </div>
        </div>

        {carDetails.bodyType && (
          <p className="text-sm text-gray-600 mb-4">
            <span className="font-medium">Virsbūves tips:</span> {carDetails.bodyType}
          </p>
        )}

        <div className="mb-4">
          <h4 className="text-sm font-semibold mb-2">Aprīkojums:</h4>
          <div className="flex flex-wrap gap-2">
            {carDetails.features.slice(0, isExpanded ? undefined : 6).map((feature, i) => (
              <Badge key={i} variant="secondary" className="text-xs">
                {feature}
              </Badge>
            ))}
            {carDetails.features.length > 6 && !isExpanded && (
              <Badge variant="outline" className="text-xs cursor-pointer hover:bg-gray-100" onClick={() => setIsExpanded(true)}>
                +{carDetails.features.length - 6} vairāk
              </Badge>
            )}
          </div>
        </div>

        <Button
          onClick={() => setIsExpanded(!isExpanded)}
          variant="outline"
          className="w-full mb-4"
        >
          {isExpanded ? (
            <span className="flex items-center">
              Apskatīt mazāk <ChevronUp className="ml-2 h-4 w-4" />
            </span>
          ) : (
            <span className="flex items-center">
              Apskatīt vairāk <ChevronDown className="ml-2 h-4 w-4" />
            </span>
          )}
        </Button>

        {isExpanded && (
          <div className="space-y-6">
            <section>
              <h4 className="text-lg font-semibold mb-2">1. Sludinājuma apraksts</h4>
              <div className="prose prose-sm max-w-none">
                <p className="text-sm text-gray-600 whitespace-pre-line">{carDetails.description}</p>
              </div>
            </section>

            <section>
              <h4 className="text-lg font-semibold mb-2">2. Der zināt</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-green-50 p-4 rounded-lg">
                  <h5 className="font-medium mb-2 text-green-700 flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4" />
                    Stiprās puses
                  </h5>
                  <ul className="list-none space-y-2">
                    {aiAnalysis.strengths.map((strength, i) => (
                      <li key={i} className="text-sm text-green-600 flex items-start gap-2">
                        <span className="mt-1">•</span>
                        {strength}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="bg-amber-50 p-4 rounded-lg">
                  <h5 className="font-medium mb-2 text-amber-700 flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    Apdomā
                  </h5>
                  <ul className="list-none space-y-2">
                    {aiAnalysis.considerations.map((consideration, i) => (
                      <li key={i} className="text-sm text-amber-600 flex items-start gap-2">
                        <span className="mt-1">•</span>
                        {consideration}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h4 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-500" />
                3. Bieži sastopamās problēmas
              </h4>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{checklistItems}</ReactMarkdown>
                  {aiAnalysis.commonProblems && (
                    <>
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <h5 className="font-medium mb-2">Papildus informācija par modeļa problēmām:</h5>
                        <ReactMarkdown>{aiAnalysis.commonProblems}</ReactMarkdown>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </section>

            <section>
              <h4 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <Gauge className="h-5 w-5 text-red-500" />
                4. Bieži sastopamās liela nobraukuma problēmas
              </h4>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{comparison}</ReactMarkdown>
                  {aiAnalysis.highMileageConcerns && (
                    <>
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <h5 className="font-medium mb-2">Papildus informācija par liela nobraukuma problēmām:</h5>
                        <ReactMarkdown>{aiAnalysis.highMileageConcerns}</ReactMarkdown>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </section>

            <section>
              <h4 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <Award className="h-5 w-5 text-green-500" />
                5. Kāpēc šis auto tika izvēlēts
              </h4>
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <div className="text-2xl font-bold text-green-600">{aiAnalysis.matchScore}%</div>
                  <div className="text-sm text-green-700">Sakritības līmenis</div>
                </div>
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{summary}</ReactMarkdown>
                </div>
              </div>
            </section>
          </div>
        )}

        <div className="mt-6 border-t pt-6">
          <Button
            variant="outline"
            className="w-full flex items-center justify-center gap-2 text-bmw-blue hover:bg-bmw-blue/10"
            onClick={() => window.open(carDetails.url, '_blank')}
          >
            <span>Skatīt pilnu sludinājumu</span>
            <ExternalLink className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default CarCard;

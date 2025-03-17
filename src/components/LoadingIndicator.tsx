import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingIndicator = () => {
  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative">
        <Loader2 className="h-12 w-12 animate-spin text-bmw-blue" />
      </div>
      <div className="mt-4 space-y-2 text-center">
        <div className="animate-pulse space-y-2">
          <div className="h-2 w-24 bg-gray-200 rounded mx-auto"></div>
          <div className="h-2 w-32 bg-gray-200 rounded mx-auto"></div>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;

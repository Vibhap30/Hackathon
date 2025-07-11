import React from 'react';
import EnergyMap from '../components/EnergyMap';

const EnergyMapPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <EnergyMap />
      </div>
    </div>
  );
};

export default EnergyMapPage;

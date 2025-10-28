'use client';

import axios from 'axios';
import React, { useEffect, useState } from 'react';

interface TierInfo {
  tier: number;
  disciplines: string[];
  connection_count?: number;
  average_connections?: number;
}

const CrossTierNavigator: React.FC = () => {
  const [tiers, setTiers] = useState<TierInfo[]>([]);
  const [selectedTier, setSelectedTier] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

  const tierNames: Record<number, string> = {
    1: 'Creative Arts',
    2: 'Philosophy & Theory',
    3: 'Ethics & AI',
    4: 'Business & Economics',
    5: 'Science & Research',
    6: 'Healthcare & Medicine',
    7: 'Law & Governance',
    8: 'Arts & Humanities',
    9: 'Technology & Engineering',
    10: 'Education & Learning',
    11: 'Social & Behavioral',
    12: 'Environment & Sustainability',
  };

  // Fetch tier information
  useEffect(() => {
    const fetchTierData = async () => {
      setLoading(true);
      setError(null);
      try {
        const tierPromises = Array.from({ length: 12 }, (_, i) =>
          axios.get(`${API_URL}/tier/${i + 1}/connections`)
        );

        const responses = await Promise.all(tierPromises);
        const tierData: TierInfo[] = responses.map((response, index) => ({
          tier: index + 1,
          disciplines: response.data.data.disciplines || [],
          connection_count: response.data.data.connection_count,
          average_connections: response.data.data.average_connections,
        }));

        setTiers(tierData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch tier information');
        console.error('Error fetching tiers:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTierData();
  }, []);

  const currentTier = tiers.find((t) => t.tier === selectedTier);

  return (
    <div className="w-full max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Cross-Tier Navigator</h1>
        <p className="text-gray-600">Explore relationships and connections across knowledge tiers</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          Error: {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="inline-block">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
          <p className="mt-4 text-gray-600">Loading tier information...</p>
        </div>
      )}

      {/* Main Content */}
      {!loading && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Tier List */}
          <div className="lg:col-span-1 bg-white rounded-lg shadow">
            <div className="p-4 border-b border-gray-200">
              <h2 className="font-bold text-gray-900">Knowledge Tiers</h2>
            </div>
            <div className="divide-y">
              {tiers.map((tier) => (
                <button
                  key={tier.tier}
                  onClick={() => setSelectedTier(tier.tier)}
                  className={`w-full text-left p-4 hover:bg-blue-50 transition ${
                    selectedTier === tier.tier ? 'bg-blue-100 border-l-4 border-blue-500' : ''
                  }`}
                >
                  <div className="font-medium text-gray-900">Tier {tier.tier}</div>
                  <div className="text-sm text-gray-600 mt-1">{tierNames[tier.tier]}</div>
                  <div className="text-xs text-gray-500 mt-2">
                    {tier.disciplines.length} disciplines
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Tier Details */}
          <div className="lg:col-span-3">
            {currentTier ? (
              <div className="space-y-6">
                {/* Tier Header */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">
                    Tier {currentTier.tier}: {tierNames[currentTier.tier]}
                  </h2>
                  <p className="text-gray-600">
                    Containing {currentTier.disciplines.length} disciplines
                  </p>
                </div>

                {/* Statistics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white rounded-lg shadow p-4">
                    <label className="text-xs font-semibold text-gray-500 uppercase">Disciplines</label>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {currentTier.disciplines.length}
                    </p>
                  </div>
                  <div className="bg-white rounded-lg shadow p-4">
                    <label className="text-xs font-semibold text-gray-500 uppercase">
                      Connections
                    </label>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {currentTier.connection_count || 0}
                    </p>
                  </div>
                </div>

                {/* Disciplines List */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="font-bold text-gray-900 mb-4">Disciplines in This Tier</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
                    {currentTier.disciplines.slice(0, 20).map((discipline, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-gray-50 border border-gray-200 rounded hover:border-blue-300 transition"
                      >
                        <p className="text-sm font-medium text-gray-900">{discipline}</p>
                      </div>
                    ))}
                  </div>
                  {currentTier.disciplines.length > 20 && (
                    <p className="text-xs text-gray-500 mt-3">
                      +{currentTier.disciplines.length - 20} more disciplines
                    </p>
                  )}
                </div>

                {/* Cross-Tier Connections */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="font-bold text-gray-900 mb-4">Cross-Tier Connections</h3>
                  <p className="text-sm text-gray-600">
                    This tier has {currentTier.connection_count || 0} semantic connections to other tiers,
                    averaging {(currentTier.average_connections || 0).toFixed(2)} connections per discipline.
                  </p>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <p className="text-gray-500">Select a tier to view details</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CrossTierNavigator;

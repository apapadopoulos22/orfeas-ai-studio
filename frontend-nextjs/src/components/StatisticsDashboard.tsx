'use client';

import axios from 'axios';
import React, { useEffect, useState } from 'react';

interface PhaseStatistics {
  phase: string;
  total_disciplines: number;
  total_knowledge_items: number;
  total_relationships: number;
  average_items_per_discipline: number;
  tier_breakdown: Array<{
    tier: number;
    discipline_count: number;
    item_count: number;
    average_relationships: number;
  }>;
}

interface ChartData {
  label: string;
  value: number;
}

const StatisticsDashboard: React.FC = () => {
  const [stats, setStats] = useState<PhaseStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

  // Fetch statistics
  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get(`${API_URL}/statistics/phase3`);
        setStats(response.data.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch statistics');
        console.error('Error fetching stats:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="w-full max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Statistics Dashboard</h1>
        <p className="text-gray-600">Comprehensive overview of Phase 3 knowledge system metrics</p>
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
          <p className="mt-4 text-gray-600">Loading statistics...</p>
        </div>
      )}

      {/* Main Content */}
      {!loading && stats && (
        <div className="space-y-8">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-semibold text-gray-500 uppercase">Phase</div>
              <p className="text-3xl font-bold text-gray-900 mt-2">{stats.phase}</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-semibold text-gray-500 uppercase">Total Disciplines</div>
              <p className="text-3xl font-bold text-blue-600 mt-2">{stats.total_disciplines}</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-semibold text-gray-500 uppercase">Knowledge Items</div>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {stats.total_knowledge_items.toLocaleString()}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-semibold text-gray-500 uppercase">Relationships</div>
              <p className="text-3xl font-bold text-purple-600 mt-2">{stats.total_relationships}</p>
            </div>
          </div>

          {/* Average Metrics */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Average Metrics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="text-sm font-semibold text-gray-500 uppercase">
                  Items Per Discipline
                </label>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {stats.average_items_per_discipline.toFixed(1)}
                </p>
              </div>
            </div>
          </div>

          {/* Tier Breakdown */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Tier Breakdown</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Tier</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Disciplines</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Items</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Avg Relationships</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.tier_breakdown.map((tier) => (
                    <tr key={tier.tier} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium text-gray-900">Tier {tier.tier}</td>
                      <td className="py-3 px-4 text-right text-gray-600">{tier.discipline_count}</td>
                      <td className="py-3 px-4 text-right text-gray-600">
                        {tier.item_count.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right text-gray-600">
                        {tier.average_relationships.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Summary */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow p-6 border border-blue-200">
            <h3 className="font-bold text-gray-900 mb-3">System Summary</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>
                ✓ {stats.total_disciplines} disciplines organized across 12 knowledge tiers
              </li>
              <li>
                ✓ {stats.total_knowledge_items.toLocaleString()} knowledge items indexed and cross-referenced
              </li>
              <li>
                ✓ {stats.total_relationships} semantic relationships mapped for intelligent navigation
              </li>
              <li>
                ✓ Average of {stats.average_items_per_discipline.toFixed(0)} items per discipline
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatisticsDashboard;

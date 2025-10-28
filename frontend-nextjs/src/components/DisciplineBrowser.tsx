'use client';

import axios from 'axios';
import React, { useCallback, useEffect, useState } from 'react';

interface Discipline {
  name: string;
  category: string;
  tier: number;
  total_items: number;
  keywords: string[];
}

interface PaginationMeta {
  total: number;
  page: number;
  limit: number;
  pages: number;
}

const DisciplineBrowser: React.FC = () => {
  const [disciplines, setDisciplines] = useState<Discipline[]>([]);
  const [meta, setMeta] = useState<PaginationMeta>({
    total: 0,
    page: 1,
    limit: 20,
    pages: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDiscipline, setSelectedDiscipline] = useState<Discipline | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

  // Fetch disciplines with pagination
  const fetchDisciplines = useCallback(async (page: number = 1, limit: number = 20, query?: string) => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: ((page - 1) * limit).toString(),
      });

      const url = query
        ? `${API_URL}/disciplines?${params}&search=${encodeURIComponent(query)}`
        : `${API_URL}/disciplines?${params}`;

      const response = await axios.get(url);
      const { data, meta: responseMeta } = response.data;

      setDisciplines(data);
      setMeta(responseMeta || {
        total: data.length,
        page,
        limit,
        pages: Math.ceil((responseMeta?.total || data.length) / limit),
      });
      setSelectedDiscipline(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch disciplines');
      console.error('Error fetching disciplines:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchDisciplines(1, 20);
  }, []);

  // Handle search
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    fetchDisciplines(1, 20, query);
  };

  // Handle pagination
  const handlePageChange = (newPage: number) => {
    fetchDisciplines(newPage, meta.limit, searchQuery);
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Discipline Browser</h1>
        <p className="text-gray-600">Browse and explore 403 disciplines across 12 knowledge tiers</p>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <input
            type="text"
            placeholder="Search disciplines..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <svg
            className="absolute right-3 top-3 w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
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
          <p className="mt-4 text-gray-600">Loading disciplines...</p>
        </div>
      )}

      {/* Main Content */}
      {!loading && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Disciplines List */}
          <div className="lg:col-span-1 bg-white rounded-lg shadow">
            <div className="p-4 border-b border-gray-200">
              <h2 className="font-bold text-gray-900">
                Disciplines ({meta.total})
              </h2>
            </div>
            <div className="divide-y max-h-96 overflow-y-auto">
              {disciplines.length > 0 ? (
                disciplines.map((discipline, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedDiscipline(discipline)}
                    className={`w-full text-left p-3 hover:bg-blue-50 transition ${
                      selectedDiscipline?.name === discipline.name ? 'bg-blue-100 border-l-4 border-blue-500' : ''
                    }`}
                  >
                    <div className="font-medium text-sm text-gray-900">{discipline.name}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      Tier {discipline.tier} • {discipline.total_items} items
                    </div>
                  </button>
                ))
              ) : (
                <div className="p-4 text-center text-gray-500">No disciplines found</div>
              )}
            </div>

            {/* Pagination */}
            {meta.pages > 1 && (
              <div className="p-4 border-t border-gray-200 flex items-center justify-between">
                <button
                  onClick={() => handlePageChange(meta.page - 1)}
                  disabled={meta.page === 1}
                  className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 disabled:opacity-50 rounded"
                >
                  Previous
                </button>
                <span className="text-xs text-gray-600">
                  Page {meta.page} of {meta.pages}
                </span>
                <button
                  onClick={() => handlePageChange(meta.page + 1)}
                  disabled={meta.page === meta.pages}
                  className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 disabled:opacity-50 rounded"
                >
                  Next
                </button>
              </div>
            )}
          </div>

          {/* Details Panel */}
          <div className="lg:col-span-2">
            {selectedDiscipline ? (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">{selectedDiscipline.name}</h3>

                <div className="space-y-4">
                  <div>
                    <label className="text-xs font-semibold text-gray-500 uppercase">Category</label>
                    <p className="text-gray-900 mt-1">{selectedDiscipline.category}</p>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-gray-500 uppercase">Tier</label>
                    <p className="text-gray-900 mt-1">Tier {selectedDiscipline.tier}</p>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-gray-500 uppercase">Knowledge Items</label>
                    <p className="text-gray-900 mt-1">{selectedDiscipline.total_items} items indexed</p>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-gray-500 uppercase">Keywords</label>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {selectedDiscipline.keywords.slice(0, 5).map((kw, idx) => (
                        <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                          {kw}
                        </span>
                      ))}
                      {selectedDiscipline.keywords.length > 5 && (
                        <span className="px-3 py-1 text-gray-600 text-sm">
                          +{selectedDiscipline.keywords.length - 5} more
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <p className="text-gray-500">Select a discipline to view details</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DisciplineBrowser;

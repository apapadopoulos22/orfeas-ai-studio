'use client';

import axios from 'axios';
import React, { useState } from 'react';

interface QueryResult {
  query_type: string;
  success: boolean;
  results?: unknown;
  error?: string;
  execution_time_ms?: number;
}

type QueryType = 'pathfinding' | 'related' | 'semantic_search' | 'tier_analysis';

const SemanticQueryBuilder: React.FC = () => {
  const [queryType, setQueryType] = useState<QueryType>('pathfinding');
  const [params, setParams] = useState({
    from_discipline: '',
    to_discipline: '',
    query: '',
    tier: '1',
  });
  const [results, setResults] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

  const handleParamChange = (key: string, value: string) => {
    setParams((prev) => ({ ...prev, [key]: value }));
  };

  const executeQuery = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      let url = `${API_URL}/query`;
      const body: Record<string, unknown> = { query_type: queryType };

      switch (queryType) {
        case 'pathfinding':
          body.from_discipline = params.from_discipline;
          body.to_discipline = params.to_discipline;
          break;
        case 'related':
          body.discipline = params.from_discipline;
          break;
        case 'semantic_search':
          body.query = params.query;
          break;
        case 'tier_analysis':
          body.tier = parseInt(params.tier);
          break;
      }

      const response = await axios.post(url, body);
      setResults(response.data.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Query execution failed');
    } finally {
      setLoading(false);
    }
  };

  const renderQueryForm = () => {
    switch (queryType) {
      case 'pathfinding':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">From Discipline</label>
              <input
                type="text"
                placeholder="e.g., Physics"
                value={params.from_discipline}
                onChange={(e) => handleParamChange('from_discipline', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">To Discipline</label>
              <input
                type="text"
                placeholder="e.g., Chemistry"
                value={params.to_discipline}
                onChange={(e) => handleParamChange('to_discipline', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        );

      case 'related':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Discipline</label>
            <input
              type="text"
              placeholder="e.g., Mathematics"
              value={params.from_discipline}
              onChange={(e) => handleParamChange('from_discipline', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        );

      case 'semantic_search':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search Query</label>
            <textarea
              placeholder="e.g., machine learning and neural networks"
              value={params.query}
              onChange={(e) => handleParamChange('query', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 h-24"
            />
          </div>
        );

      case 'tier_analysis':
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Tier Number</label>
            <select
              value={params.tier}
              onChange={(e) => handleParamChange('tier', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {Array.from({ length: 12 }, (_, i) => (
                <option key={i + 1} value={i + 1}>
                  Tier {i + 1}
                </option>
              ))}
            </select>
          </div>
        );

      default:
        return null;
    }
  };

  const renderResults = () => {
    if (!results) return null;

    return (
      <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-gray-900">Query Results</h3>
          {results.execution_time_ms && (
            <span className="text-xs text-gray-600">
              Executed in {results.execution_time_ms}ms
            </span>
          )}
        </div>

        {results.success ? (
          <div className="bg-white p-4 rounded border border-green-200">
            <pre className="text-xs text-gray-700 overflow-auto max-h-64">
              {JSON.stringify(results.results, null, 2)}
            </pre>
          </div>
        ) : (
          <div className="bg-white p-4 rounded border border-red-200 text-red-700">
            Error: {results.error || 'Unknown error'}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Semantic Query Builder</h1>
        <p className="text-gray-600">Execute complex queries across the knowledge graph</p>
      </div>

      {/* Query Type Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">Query Type</label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {(['pathfinding', 'related', 'semantic_search', 'tier_analysis'] as const).map((type) => (
            <button
              key={type}
              onClick={() => {
                setQueryType(type);
                setResults(null);
              }}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                queryType === type
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {type.replace('_', ' ').charAt(0).toUpperCase() + type.replace('_', ' ').slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Query Form */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="font-bold text-gray-900 mb-4">Query Parameters</h2>
        {renderQueryForm()}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          Error: {error}
        </div>
      )}

      {/* Execute Button */}
      <div className="mb-6">
        <button
          onClick={executeQuery}
          disabled={loading}
          className="w-full px-6 py-3 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {loading ? 'Executing Query...' : 'Execute Query'}
        </button>
      </div>

      {/* Results */}
      {renderResults()}
    </div>
  );
};

export default SemanticQueryBuilder;

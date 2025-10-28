'use client';

import CrossTierNavigator from '@/components/CrossTierNavigator';
import DisciplineBrowser from '@/components/DisciplineBrowser';
import KnowledgeGraphViewer from '@/components/KnowledgeGraphViewer';
import SemanticQueryBuilder from '@/components/SemanticQueryBuilder';
import StatisticsDashboard from '@/components/StatisticsDashboard';
import { useState } from 'react';

type TabType = 'browser' | 'graph' | 'query' | 'navigator' | 'stats';

export default function KnowledgeSystemPage() {
  const [activeTab, setActiveTab] = useState<TabType>('browser');

  const tabs: Array<{ id: TabType; label: string; icon: string }> = [
    { id: 'browser', label: 'Disciplines', icon: '📚' },
    { id: 'graph', label: 'Knowledge Graph', icon: '🔗' },
    { id: 'query', label: 'Query Builder', icon: '🔍' },
    { id: 'navigator', label: 'Tier Navigator', icon: '🗂️' },
    { id: 'stats', label: 'Statistics', icon: '📊' },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'browser':
        return <DisciplineBrowser />;
      case 'graph':
        return <KnowledgeGraphViewer />;
      case 'query':
        return <SemanticQueryBuilder />;
      case 'navigator':
        return <CrossTierNavigator />;
      case 'stats':
        return <StatisticsDashboard />;
      default:
        return <DisciplineBrowser />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <h1 className="text-3xl font-bold text-gray-900">BOB AI - Knowledge System</h1>
          <p className="text-gray-600 mt-1">
            403 disciplines | 51,672 knowledge items | 64 semantic relationships
          </p>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6">
          <nav className="flex space-x-8" aria-label="Main navigation">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="min-h-screen bg-gray-100 py-12">
        {renderContent()}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-bold text-gray-900">About</h3>
              <p className="text-sm text-gray-600 mt-2">
                BOB AI v10.0 - Enterprise knowledge platform with 403 disciplines and advanced semantic navigation.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-gray-900">Statistics</h3>
              <ul className="text-sm text-gray-600 mt-2 space-y-1">
                <li>403 Total Disciplines</li>
                <li>51,672 Knowledge Items</li>
                <li>64 Semantic Relationships</li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-gray-900">Version</h3>
              <p className="text-sm text-gray-600 mt-2">
                Phase 4.5 - Frontend Integration<br />
                October 28, 2025
              </p>
            </div>
          </div>
          <div className="border-t border-gray-200 mt-8 pt-8 text-center text-sm text-gray-600">
            <p>&copy; 2025 BOB AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

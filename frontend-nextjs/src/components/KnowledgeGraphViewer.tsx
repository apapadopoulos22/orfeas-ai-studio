'use client';

import axios from 'axios';
import React, { useEffect, useRef, useState } from 'react';

interface Node {
  id: string;
  label: string;
  tier?: number;
}

interface Edge {
  source: string;
  target: string;
  weight?: number;
}

interface GraphData {
  nodes: Node[];
  edges: Edge[];
  stats?: {
    total_nodes: number;
    total_edges: number;
    average_degree: number;
  };
}

const KnowledgeGraphViewer: React.FC = () => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [showStats, setShowStats] = useState(true);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

  // Fetch knowledge graph data
  useEffect(() => {
    const fetchGraph = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get(`${API_URL}/knowledge-graph?include_stats=true`);
        setGraphData(response.data.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch knowledge graph');
        console.error('Error fetching graph:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
  }, []);

  // Simple force-directed graph visualization
  useEffect(() => {
    if (!graphData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Draw graph
    const nodes = graphData.nodes;
    const edges = graphData.edges;

    // Simple circular layout for demo
    const radius = Math.min(canvas.width, canvas.height) / 3;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Draw edges first (so they appear behind nodes)
    ctx.strokeStyle = 'rgba(150, 150, 150, 0.3)';
    ctx.lineWidth = 1;

    edges.forEach((edge) => {
      const source = nodes.find((n) => n.id === edge.source);
      const target = nodes.find((n) => n.id === edge.target);

      if (source && target) {
        const sourceIndex = nodes.indexOf(source);
        const targetIndex = nodes.indexOf(target);

        const sx = centerX + radius * Math.cos((sourceIndex / nodes.length) * Math.PI * 2);
        const sy = centerY + radius * Math.sin((sourceIndex / nodes.length) * Math.PI * 2);
        const tx = centerX + radius * Math.cos((targetIndex / nodes.length) * Math.PI * 2);
        const ty = centerY + radius * Math.sin((targetIndex / nodes.length) * Math.PI * 2);

        ctx.beginPath();
        ctx.moveTo(sx, sy);
        ctx.lineTo(tx, ty);
        ctx.stroke();
      }
    });

    // Draw nodes
    nodes.forEach((node, index) => {
      const x = centerX + radius * Math.cos((index / nodes.length) * Math.PI * 2);
      const y = centerY + radius * Math.sin((index / nodes.length) * Math.PI * 2);

      const isSelected = selectedNode?.id === node.id;
      const size = isSelected ? 8 : 5;

      // Draw node circle
      ctx.fillStyle = isSelected ? '#3b82f6' : '#6366f1';
      ctx.beginPath();
      ctx.arc(x, y, size, 0, Math.PI * 2);
      ctx.fill();

      // Draw label for selected node
      if (isSelected) {
        ctx.fillStyle = '#1f2937';
        ctx.font = '12px sans-serif';
        ctx.fillText(node.label, x + 10, y);
      }
    });
  }, [graphData, selectedNode]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!graphData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const radius = Math.min(canvas.width, canvas.height) / 3;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Find clicked node
    const nodes = graphData.nodes;
    for (let i = 0; i < nodes.length; i++) {
      const nx = centerX + radius * Math.cos((i / nodes.length) * Math.PI * 2);
      const ny = centerY + radius * Math.sin((i / nodes.length) * Math.PI * 2);
      const distance = Math.sqrt((x - nx) ** 2 + (y - ny) ** 2);

      if (distance < 10) {
        setSelectedNode(nodes[i]);
        break;
      }
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Knowledge Graph</h1>
        <p className="text-gray-600">Visualize semantic relationships between 403 disciplines</p>
      </div>

      {/* Controls */}
      <div className="mb-6 flex gap-4">
        <button
          onClick={() => setShowStats(!showStats)}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
        >
          {showStats ? 'Hide' : 'Show'} Statistics
        </button>
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
          <p className="mt-4 text-gray-600">Loading knowledge graph...</p>
        </div>
      )}

      {/* Main Content */}
      {!loading && graphData && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Graph Canvas */}
          <div className="lg:col-span-3 bg-white rounded-lg shadow p-4">
            <canvas
              ref={canvasRef}
              onClick={handleCanvasClick}
              className="w-full bg-gray-50 rounded cursor-pointer border border-gray-200"
              style={{ minHeight: '400px' }}
            />
            <p className="text-xs text-gray-500 mt-2">Click on nodes to select them</p>
          </div>

          {/* Stats Sidebar */}
          <div className="lg:col-span-1">
            {showStats && (
              <div className="bg-white rounded-lg shadow p-6 space-y-4">
                <h3 className="font-bold text-gray-900">Graph Statistics</h3>

                <div>
                  <label className="text-xs font-semibold text-gray-500 uppercase">Total Nodes</label>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {graphData.stats?.total_nodes || 0}
                  </p>
                </div>

                <div>
                  <label className="text-xs font-semibold text-gray-500 uppercase">Total Edges</label>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {graphData.stats?.total_edges || 0}
                  </p>
                </div>

                <div>
                  <label className="text-xs font-semibold text-gray-500 uppercase">Average Degree</label>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {graphData.stats?.average_degree.toFixed(2) || 0}
                  </p>
                </div>

                {selectedNode && (
                  <div className="pt-4 border-t border-gray-200">
                    <label className="text-xs font-semibold text-gray-500 uppercase">Selected Node</label>
                    <p className="text-sm font-medium text-gray-900 mt-2">{selectedNode.label}</p>
                    {selectedNode.tier && (
                      <p className="text-xs text-gray-600 mt-1">Tier {selectedNode.tier}</p>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default KnowledgeGraphViewer;

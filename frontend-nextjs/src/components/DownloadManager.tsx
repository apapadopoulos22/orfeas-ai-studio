'use client'

import { Download, ExternalLink, FileText, Package, Settings } from 'lucide-react'
import { useState } from 'react'

interface DownloadManagerProps {
  modelUrl: string
  fileName: string
  format: string
}

export default function DownloadManager({ modelUrl, fileName, format }: DownloadManagerProps) {
  const [isDownloading, setIsDownloading] = useState(false)

  const handleDownload = async () => {
    setIsDownloading(true)

    try {
      const response = await fetch(modelUrl)
      const blob = await response.blob()

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.style.display = 'none'
      a.href = url
      a.download = fileName

      document.body.appendChild(a)
      a.click()

      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

    } catch (error) {
      console.error('Download failed:', error)
    } finally {
      setIsDownloading(false)
    }
  }

  const handleViewRaw = () => {
    window.open(modelUrl, '_blank')
  }

  const getFormatInfo = (format: string) => {
    switch (format.toLowerCase()) {
      case 'stl':
        return {
          name: 'STL',
          description: 'Standard 3D printing format',
          icon: '🗃️',
          usage: 'Compatible with most 3D printers and slicing software'
        }
      case 'obj':
        return {
          name: 'OBJ',
          description: 'Wavefront 3D object format',
          icon: '📦',
          usage: 'Widely supported by 3D graphics software'
        }
      case 'gbl':
        return {
          name: 'GBL',
          description: 'Gerber format for PCB manufacturing',
          icon: '🔧',
          usage: 'Used for printed circuit board fabrication'
        }
      default:
        return {
          name: format.toUpperCase(),
          description: '3D model format',
          icon: '📄',
          usage: 'Generic 3D model file'
        }
    }
  }

  const formatInfo = getFormatInfo(format)

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-3">
        <Download className="w-6 h-6 text-green-400" />
        <h3 className="text-xl font-semibold text-white">Download 3D Model</h3>
      </div>

      {/* Format Information */}
      <div className="bg-white/5 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <div className="text-2xl">{formatInfo.icon}</div>
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <h4 className="font-semibold text-white">{formatInfo.name} Format</h4>
              <span className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded text-xs font-medium">
                {format.toUpperCase()}
              </span>
            </div>
            <p className="text-white/70 text-sm mb-2">{formatInfo.description}</p>
            <p className="text-white/50 text-xs">{formatInfo.usage}</p>
          </div>
        </div>
      </div>

      {/* File Information */}
      <div className="bg-white/5 rounded-lg p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-white/60">File Name:</span>
            <span className="text-white font-mono text-xs">{fileName}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-white/60">Format:</span>
            <span className="text-white">{formatInfo.name}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-white/60">Status:</span>
            <span className="text-green-400">Ready</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-white/60">Generated:</span>
            <span className="text-white">{new Date().toLocaleTimeString()}</span>
          </div>
        </div>
      </div>

      {/* Download Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <button
          onClick={handleDownload}
          disabled={isDownloading}
          className="flex items-center justify-center space-x-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200"
        >
          {isDownloading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Downloading...</span>
            </>
          ) : (
            <>
              <Download className="w-4 h-4" />
              <span>Download {formatInfo.name}</span>
            </>
          )}
        </button>

        <button
          onClick={handleViewRaw}
          className="flex items-center justify-center space-x-2 bg-white/10 hover:bg-white/20 text-white font-medium py-3 px-4 rounded-lg transition-colors border border-white/20"
        >
          <ExternalLink className="w-4 h-4" />
          <span>View Raw File</span>
        </button>
      </div>

      {/* Additional Options */}
      <div className="space-y-2">
        <div className="text-white/60 text-sm font-medium">Additional Options:</div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          <button className="flex items-center justify-center space-x-2 bg-white/5 hover:bg-white/10 text-white/70 hover:text-white text-sm py-2 px-3 rounded transition-colors">
            <FileText className="w-3 h-3" />
            <span>Export Info</span>
          </button>
          <button className="flex items-center justify-center space-x-2 bg-white/5 hover:bg-white/10 text-white/70 hover:text-white text-sm py-2 px-3 rounded transition-colors">
            <Package className="w-3 h-3" />
            <span>Convert Format</span>
          </button>
          <button className="flex items-center justify-center space-x-2 bg-white/5 hover:bg-white/10 text-white/70 hover:text-white text-sm py-2 px-3 rounded transition-colors">
            <Settings className="w-3 h-3" />
            <span>Print Settings</span>
          </button>
        </div>
      </div>

      {/* Usage Tips */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <div className="text-blue-400 text-sm">💡</div>
          <div>
            <div className="text-blue-300 font-medium text-sm mb-1">Usage Tips</div>
            <ul className="text-blue-200/80 text-xs space-y-1">
              <li>• Check your slicer settings before printing</li>
              <li>• Recommended layer height: 0.2mm for FDM, 0.05mm for SLA</li>
              <li>• Consider supports for overhanging features</li>
              <li>• Verify model dimensions match your printer build volume</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

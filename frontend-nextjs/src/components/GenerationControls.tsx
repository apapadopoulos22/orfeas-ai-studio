'use client'

import { Layers, Printer, Settings, Zap } from 'lucide-react'
import { useState } from 'react'

interface GenerationParams {
  format: 'stl' | 'obj' | 'gbl'
  dimensions: {
    width: number
    height: number
    depth: number
  }
  quality: number
  printerType: 'fdm' | 'sla'
  slaModel?: string
}

interface GenerationControlsProps {
  params: GenerationParams
  onChange: (params: GenerationParams) => void
  disabled?: boolean
}

const FORMAT_OPTIONS = [
  { value: 'stl', label: 'STL', icon: '🗃️', description: 'Standard 3D printing format' },
  { value: 'obj', label: 'OBJ', icon: '📦', description: 'Wavefront OBJ format' },
  { value: 'gbl', label: 'GBL', icon: '🔧', description: 'Gerber format' }
] as const

const PRINTER_TYPES = [
  { value: 'fdm', label: 'FDM', icon: '🏗️', description: 'Fused Deposition Modeling' },
  { value: 'sla', label: 'SLA', icon: '🔬', description: 'Stereolithography (Resin)' }
] as const

const SLA_MODELS = [
  { value: 'halot-one-x1', label: 'Creality Halot-One X1', specs: '192×120×200mm, 50μm XY' }
] as const

const QUALITY_LABELS = [
  'Draft', 'Low', 'Basic', 'Standard', 'Good', 'High', 'Very High', 'Ultra', 'Maximum', 'Perfect'
]

export default function GenerationControls({ params, onChange, disabled = false }: GenerationControlsProps) {
  const [aspectLocked, setAspectLocked] = useState(true)

  const updateParams = (updates: Partial<GenerationParams>) => {
    onChange({ ...params, ...updates })
  }

  const updateDimension = (key: 'width' | 'height' | 'depth', value: number) => {
    const newDimensions = { ...params.dimensions }

    if (aspectLocked && (key === 'width' || key === 'height')) {
      // Keep aspect ratio for width and height only
      if (key === 'width') {
        newDimensions.width = value
        newDimensions.height = value
      } else {
        newDimensions.height = value
        newDimensions.width = value
      }
    } else {
      newDimensions[key] = value
    }

    updateParams({ dimensions: newDimensions })
  }

  return (
    <div className="space-y-6">
      {/* Output Format */}
      <div className="space-y-3">
        <label className="flex items-center space-x-2 text-white font-medium">
          <Settings className="w-4 h-4" />
          <span>Output Format</span>
        </label>
        <div className="grid grid-cols-3 gap-2">
          {FORMAT_OPTIONS.map((format) => (
            <button
              key={format.value}
              onClick={() => updateParams({ format: format.value })}
              disabled={disabled}
              className={`
                p-3 rounded-lg border transition-all text-center
                ${params.format === format.value
                  ? 'border-purple-400 bg-purple-500/20 text-white'
                  : 'border-white/20 bg-white/5 text-white/70 hover:border-purple-400/50 hover:bg-purple-500/10'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              <div className="text-lg mb-1">{format.icon}</div>
              <div className="font-medium text-sm">{format.label}</div>
              <div className="text-xs opacity-70">{format.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Printer Type */}
      <div className="space-y-3">
        <label className="flex items-center space-x-2 text-white font-medium">
          <Printer className="w-4 h-4" />
          <span>Target Printer</span>
        </label>
        <div className="grid grid-cols-2 gap-2">
          {PRINTER_TYPES.map((printer) => (
            <button
              key={printer.value}
              onClick={() => updateParams({ printerType: printer.value })}
              disabled={disabled}
              className={`
                p-3 rounded-lg border transition-all text-center
                ${params.printerType === printer.value
                  ? 'border-purple-400 bg-purple-500/20 text-white'
                  : 'border-white/20 bg-white/5 text-white/70 hover:border-purple-400/50 hover:bg-purple-500/10'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              <div className="text-lg mb-1">{printer.icon}</div>
              <div className="font-medium text-sm">{printer.label}</div>
              <div className="text-xs opacity-70">{printer.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* SLA Model Selection (only show if SLA is selected) */}
      {params.printerType === 'sla' && (
        <div className="space-y-3">
          <label className="flex items-center space-x-2 text-white font-medium">
            <Zap className="w-4 h-4" />
            <span>SLA Printer Model</span>
          </label>
          <div className="space-y-2">
            {SLA_MODELS.map((model) => (
              <button
                key={model.value}
                onClick={() => updateParams({ slaModel: model.value })}
                disabled={disabled}
                className={`
                  w-full p-3 rounded-lg border transition-all text-left
                  ${params.slaModel === model.value
                    ? 'border-purple-400 bg-purple-500/20 text-white'
                    : 'border-white/20 bg-white/5 text-white/70 hover:border-purple-400/50 hover:bg-purple-500/10'
                  }
                  ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                `}
              >
                <div className="font-medium">{model.label}</div>
                <div className="text-xs opacity-70">{model.specs}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Dimensions */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="flex items-center space-x-2 text-white font-medium">
            <Layers className="w-4 h-4" />
            <span>Dimensions (mm)</span>
          </label>
          <button
            onClick={() => setAspectLocked(!aspectLocked)}
            disabled={disabled}
            className={`
              text-xs px-2 py-1 rounded transition-colors
              ${aspectLocked
                ? 'bg-purple-500/20 text-purple-300 border border-purple-400/50'
                : 'bg-white/5 text-white/60 border border-white/20'
              }
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            🔗 {aspectLocked ? 'Locked' : 'Unlocked'}
          </button>
        </div>

        <div className="grid grid-cols-3 gap-3">
          {[
            { key: 'width', label: 'Width', min: 1, max: 1000 },
            { key: 'height', label: 'Height', min: 1, max: 1000 },
            { key: 'depth', label: 'Depth', min: 0.5, max: 500 }
          ].map((dim) => (
            <div key={dim.key} className="space-y-1">
              <label className="text-white/70 text-xs">{dim.label}</label>
              <input
                type="number"
                min={dim.min}
                max={dim.max}
                step={dim.key === 'depth' ? 0.5 : 1}
                value={params.dimensions[dim.key as keyof typeof params.dimensions]}
                onChange={(e) => updateDimension(
                  dim.key as 'width' | 'height' | 'depth',
                  parseFloat(e.target.value) || dim.min
                )}
                disabled={disabled}
                className="w-full bg-white/5 border border-white/20 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-400 focus:ring-1 focus:ring-purple-400 disabled:opacity-50"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Quality Slider */}
      <div className="space-y-3">
        <label className="flex items-center justify-between text-white font-medium">
          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4" />
            <span>Generation Quality</span>
          </div>
          <span className="text-sm text-purple-300">
            {QUALITY_LABELS[params.quality - 1]} ({params.quality})
          </span>
        </label>

        <div className="space-y-2">
          <input
            type="range"
            min={1}
            max={10}
            step={1}
            value={params.quality}
            onChange={(e) => updateParams({ quality: parseInt(e.target.value) })}
            disabled={disabled}
            className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer slider-thumb"
          />
          <div className="flex justify-between text-xs text-white/50">
            <span>Fast</span>
            <span>Balanced</span>
            <span>Perfect</span>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="bg-white/5 rounded-lg p-4 space-y-2">
        <h4 className="text-white font-medium text-sm">Generation Summary</h4>
        <div className="space-y-1 text-xs text-white/70">
          <div>Format: {FORMAT_OPTIONS.find(f => f.value === params.format)?.label}</div>
          <div>Printer: {PRINTER_TYPES.find(p => p.value === params.printerType)?.label}</div>
          {params.printerType === 'sla' && params.slaModel && (
            <div>Model: {SLA_MODELS.find(m => m.value === params.slaModel)?.label}</div>
          )}
          <div>Size: {params.dimensions.width}×{params.dimensions.height}×{params.dimensions.depth}mm</div>
          <div>Quality: {QUALITY_LABELS[params.quality - 1]}</div>
        </div>
      </div>

      <style jsx>{`
        .slider-thumb::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #a855f7;
          cursor: pointer;
          border: 2px solid #ffffff;
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
        }

        .slider-thumb::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #a855f7;
          cursor: pointer;
          border: 2px solid #ffffff;
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
        }
      `}</style>
    </div>
  )
}

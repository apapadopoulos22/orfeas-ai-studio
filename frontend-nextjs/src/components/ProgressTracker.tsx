'use client'

import { AlertCircle, CheckCircle, Clock, Loader } from 'lucide-react'

interface GenerationJob {
  id: string
  status: 'idle' | 'uploading' | 'generating' | 'completed' | 'failed'
  progress: number
  message?: string
  error?: string
}

interface ProgressTrackerProps {
  job: GenerationJob
}

export default function ProgressTracker({ job }: ProgressTrackerProps) {
  const getStatusColor = () => {
    switch (job.status) {
      case 'generating':
        return 'text-blue-400'
      case 'completed':
        return 'text-green-400'
      case 'failed':
        return 'text-red-400'
      default:
        return 'text-white/60'
    }
  }

  const getStatusIcon = () => {
    switch (job.status) {
      case 'generating':
        return <Loader className="w-5 h-5 animate-spin" />
      case 'completed':
        return <CheckCircle className="w-5 h-5" />
      case 'failed':
        return <AlertCircle className="w-5 h-5" />
      default:
        return <Clock className="w-5 h-5" />
    }
  }

  const getStatusText = () => {
    switch (job.status) {
      case 'generating':
        return 'Generating 3D Model...'
      case 'completed':
        return 'Generation Complete!'
      case 'failed':
        return 'Generation Failed'
      default:
        return 'Ready'
    }
  }

  const getProgressSteps = () => {
    const progress = job.progress || 0

    if (job.status === 'generating') {
      if (progress < 20) return 'Initializing AI model...'
      if (progress < 40) return 'Analyzing input image...'
      if (progress < 60) return 'Generating depth map...'
      if (progress < 80) return 'Creating 3D mesh...'
      if (progress < 95) return 'Applying textures...'
      return 'Finalizing model...'
    }

    return job.message || getStatusText()
  }

  return (
    <div className="space-y-4">
      {/* Status Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className={getStatusColor()}>
            {getStatusIcon()}
          </div>
          <div>
            <h3 className={`font-semibold ${getStatusColor()}`}>
              {getStatusText()}
            </h3>
            <p className="text-white/60 text-sm">
              {getProgressSteps()}
            </p>
          </div>
        </div>

        {job.status === 'generating' && (
          <div className={`text-sm font-mono ${getStatusColor()}`}>
            {job.progress}%
          </div>
        )}
      </div>

      {/* Progress Bar */}
      {(job.status === 'generating' || job.status === 'completed') && (
        <div className="space-y-2">
          <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ease-out ${
                job.status === 'completed'
                  ? 'bg-gradient-to-r from-green-500 to-emerald-500'
                  : 'bg-gradient-to-r from-purple-500 to-pink-500'
              }`}
              style={{ width: `${job.progress}%` }}
            />
          </div>

          {/* Progress Steps Visualization */}
          <div className="grid grid-cols-5 gap-1 mt-3">
            {[
              { label: 'Init', threshold: 20 },
              { label: 'Analyze', threshold: 40 },
              { label: 'Depth', threshold: 60 },
              { label: 'Mesh', threshold: 80 },
              { label: 'Finish', threshold: 100 }
            ].map((step, index) => (
              <div key={index} className="text-center">
                <div
                  className={`w-full h-1 rounded mb-1 transition-colors ${
                    job.progress >= step.threshold
                      ? job.status === 'completed'
                        ? 'bg-green-500'
                        : 'bg-purple-500'
                      : 'bg-white/20'
                  }`}
                />
                <div className={`text-xs ${
                  job.progress >= step.threshold
                    ? 'text-white'
                    : 'text-white/40'
                }`}>
                  {step.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error Display */}
      {job.status === 'failed' && job.error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
          <div className="flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
            <div>
              <div className="text-red-400 font-medium text-sm">Error Details</div>
              <div className="text-red-300 text-sm mt-1">{job.error}</div>
            </div>
          </div>
        </div>
      )}

      {/* Success Details */}
      {job.status === 'completed' && (
        <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3">
          <div className="flex items-start space-x-2">
            <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
            <div>
              <div className="text-green-400 font-medium text-sm">Generation Successful</div>
              <div className="text-green-300 text-sm mt-1">
                Your 3D model has been generated and is ready for download.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Job Info */}
      {job.id && (
        <div className="bg-white/5 rounded-lg p-3">
          <div className="flex items-center justify-between text-xs">
            <span className="text-white/40">Job ID:</span>
            <span className="text-white/60 font-mono">{job.id}</span>
          </div>
        </div>
      )}
    </div>
  )
}

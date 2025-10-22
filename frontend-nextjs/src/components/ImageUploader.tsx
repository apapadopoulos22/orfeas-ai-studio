'use client'

import { Upload, X } from 'lucide-react'
import NextImage from 'next/image'
import { useCallback, useRef, useState } from 'react'

interface ImageUploaderProps {
  onUpload: (file: File) => void
  currentImage?: string
  isUploading?: boolean
}

const SUPPORTED_FORMATS = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

export default function ImageUploader({ onUpload, currentImage, isUploading = false }: ImageUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false)
  const [error, setError] = useState<string>('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const validateFile = (file: File): string | null => {
    if (!SUPPORTED_FORMATS.includes(file.type)) {
      return `Unsupported format. Please use: ${SUPPORTED_FORMATS.map(f => f.split('/')[1].toUpperCase()).join(', ')}`
    }

    if (file.size > MAX_FILE_SIZE) {
      return `File too large. Maximum size is ${MAX_FILE_SIZE / (1024 * 1024)}MB`
    }

    return null
  }

  const handleFileSelect = useCallback((file: File) => {
    setError('')

    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      return
    }

    onUpload(file)
  }, [onUpload])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)

    const files = e.dataTransfer.files
    if (files && files[0]) {
      handleFileSelect(files[0])
    }
  }, [handleFileSelect])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files[0]) {
      handleFileSelect(files[0])
    }
  }, [handleFileSelect])

  const handleClick = () => {
    if (!isUploading) {
      fileInputRef.current?.click()
    }
  }

  const clearImage = () => {
    setError('')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200
          ${isDragOver
            ? 'border-purple-400 bg-purple-500/10'
            : 'border-white/20 hover:border-purple-400/50'
          }
          ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
          ${currentImage ? 'border-green-400/50' : ''}
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
      >
        {isUploading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-xl">
            <div className="flex flex-col items-center space-y-2">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400"></div>
              <span className="text-white text-sm">Uploading...</span>
            </div>
          </div>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept={SUPPORTED_FORMATS.join(',')}
          onChange={handleFileInputChange}
          className="hidden"
          disabled={isUploading}
        />

        {currentImage ? (
          <div className="space-y-4">
            <div className="relative max-w-xs mx-auto">
              <NextImage
                src={currentImage}
                alt="Uploaded"
                width={300}
                height={200}
                className="w-full h-auto rounded-lg border border-white/10"
              />
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  clearImage()
                }}
                className="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 text-white rounded-full p-1 transition-colors"
                disabled={isUploading}
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <p className="text-green-400 text-sm">Image uploaded successfully</p>
            <p className="text-white/60 text-xs">Click to upload a different image</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-center w-16 h-16 mx-auto bg-purple-500/20 rounded-full">
              <Upload className="w-8 h-8 text-purple-400" />
            </div>

            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                {isDragOver ? 'Drop your image here' : 'Upload Image'}
              </h3>
              <p className="text-white/60 text-sm">
                Drag & drop or click to select
              </p>
              <p className="text-white/40 text-xs mt-1">
                Supports: JPEG, PNG, WebP (max 10MB)
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {/* Sample Images */}
      <div className="space-y-3">
        <p className="text-white/60 text-sm">Or try these sample shapes:</p>
        <div className="grid grid-cols-3 gap-2">
          {[
            { name: 'Geometric', emoji: '🔷', desc: 'Complex geometric patterns' },
            { name: 'Organic', emoji: '🍎', desc: 'Natural flowing shapes' },
            { name: 'Mechanical', emoji: '⚙️', desc: 'Technical components' }
          ].map((sample) => (
            <button
              key={sample.name}
              onClick={(e) => {
                e.stopPropagation()
                // Here you could generate sample images or load presets
                console.log(`Loading sample: ${sample.name}`)
              }}
              className="bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg p-3 text-center transition-colors"
              disabled={isUploading}
            >
              <div className="text-2xl mb-1">{sample.emoji}</div>
              <div className="text-white text-xs font-medium">{sample.name}</div>
              <div className="text-white/40 text-xs">{sample.desc}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

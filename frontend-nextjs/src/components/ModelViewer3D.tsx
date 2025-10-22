'use client'

import { Environment, Grid, OrbitControls, Text } from '@react-three/drei'
import { Canvas, useFrame, useLoader } from '@react-three/fiber'
import { AlertCircle, Download, RotateCcw, ZoomIn, ZoomOut } from 'lucide-react'
import { Suspense, useEffect, useRef, useState } from 'react'
import { BufferGeometry, Mesh, MeshStandardMaterial, TextureLoader, Vector3 } from 'three'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js'

interface ModelViewer3DProps {
  modelUrl?: string
  imageUrl?: string
  status: 'idle' | 'uploading' | 'generating' | 'completed' | 'failed'
}

function STLModel({ url }: { url: string }) {
  const mesh = useRef<Mesh<BufferGeometry, MeshStandardMaterial>>(null)
  const geometry = useLoader(STLLoader, url)

  useFrame(() => {
    if (mesh.current) {
      mesh.current.rotation.y += 0.01
    }
  })

  useEffect(() => {
    if (geometry && mesh.current) {
      // Center and scale the geometry
      geometry.computeBoundingBox()
      const box = geometry.boundingBox
      if (box) {
        const center = box.getCenter(new Vector3())
        const size = box.getSize(new Vector3())
        const maxDim = Math.max(size.x, size.y, size.z)

        geometry.translate(-center.x, -center.y, -center.z)
        geometry.scale(2 / maxDim, 2 / maxDim, 2 / maxDim)
      }
    }
  }, [geometry])

  return (
    <mesh ref={mesh} geometry={geometry}>
      <meshStandardMaterial
        color="#8B5CF6"
        roughness={0.3}
        metalness={0.1}
      />
    </mesh>
  )
}

function ImagePlane({ url }: { url: string }) {
  return (
    <mesh position={[0, 0, -2]}>
      <planeGeometry args={[3, 3]} />
      <meshBasicMaterial
        map={new TextureLoader().load(url)}
        transparent
        opacity={0.3}
      />
    </mesh>
  )
}

function PlaceholderContent({ status }: { status: string }) {
  const messages = {
    idle: 'Upload an image to start',
    uploading: 'Uploading image...',
    generating: 'Generating 3D model...',
    completed: '3D model ready!',
    failed: 'Generation failed'
  }

  const colors = {
    idle: '#6B7280',
    uploading: '#F59E0B',
    generating: '#8B5CF6',
    completed: '#10B981',
    failed: '#EF4444'
  }

  return (
    <group>
      <Text
        position={[0, 0.5, 0]}
        fontSize={0.3}
        color={colors[status as keyof typeof colors] || '#6B7280'}
        anchorX="center"
        anchorY="middle"
      >
        {messages[status as keyof typeof messages] || 'Ready'}
      </Text>

      {status === 'generating' && (
        <mesh>
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial color="#8B5CF6" wireframe />
        </mesh>
      )}

      {status === 'idle' && (
        <mesh>
          <boxGeometry args={[1.5, 1.5, 1.5]} />
          <meshStandardMaterial color="#374151" wireframe opacity={0.3} transparent />
        </mesh>
      )}
    </group>
  )
}

function Scene({ modelUrl, imageUrl, status }: ModelViewer3DProps) {
  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <pointLight position={[-10, -10, -5]} intensity={0.5} color="#8B5CF6" />

      <Suspense fallback={null}>
        {modelUrl && status === 'completed' ? (
          <STLModel url={modelUrl} />
        ) : (
          <PlaceholderContent status={status} />
        )}

        {imageUrl && status !== 'completed' && (
          <ImagePlane url={imageUrl} />
        )}
      </Suspense>

      <Grid
        infiniteGrid
        cellSize={1.5}
        cellThickness={0.5}
        sectionSize={10}
        sectionThickness={1}
        fadeDistance={10}
        fadeStrength={0.5}
      />

      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        maxDistance={10}
        minDistance={1}
      />

      <Environment preset="studio" />
    </>
  )
}

export default function ModelViewer3D(props: ModelViewer3DProps) {
  const [error] = useState<string>('')

  // Error handling is managed by React Three Fiber internally
  // const handleError = (error: Error) => {
  //   console.error('3D Viewer Error:', error)
  //   setError(error.message)
  // }

  return (
    <div className="w-full h-full relative">
      {/* Viewer Controls */}
      <div className="absolute top-4 right-4 z-10 flex space-x-2">
        <button
          className="bg-black/50 hover:bg-black/70 text-white p-2 rounded-lg transition-colors backdrop-blur-sm"
          title="Reset view"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
        <button
          className="bg-black/50 hover:bg-black/70 text-white p-2 rounded-lg transition-colors backdrop-blur-sm"
          title="Zoom in"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          className="bg-black/50 hover:bg-black/70 text-white p-2 rounded-lg transition-colors backdrop-blur-sm"
          title="Zoom out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        {props.modelUrl && (
          <button
            className="bg-purple-600/70 hover:bg-purple-600/90 text-white p-2 rounded-lg transition-colors backdrop-blur-sm"
            title="Download model"
            onClick={() => props.modelUrl && window.open(props.modelUrl, '_blank')}
          >
            <Download className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Status Indicator */}
      {props.status !== 'idle' && (
        <div className="absolute top-4 left-4 z-10">
          <div className={`
            px-3 py-1 rounded-full text-sm font-medium backdrop-blur-sm
            ${props.status === 'completed'
              ? 'bg-green-500/20 text-green-300 border border-green-500/30'
              : props.status === 'failed'
              ? 'bg-red-500/20 text-red-300 border border-red-500/30'
              : props.status === 'generating'
              ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
              : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
            }
          `}>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                props.status === 'generating' ? 'animate-pulse' : ''
              } ${
                props.status === 'completed' ? 'bg-green-400' :
                props.status === 'failed' ? 'bg-red-400' :
                props.status === 'generating' ? 'bg-purple-400' : 'bg-blue-400'
              }`} />
              <span className="capitalize">{props.status}</span>
            </div>
          </div>
        </div>
      )}

      {/* Canvas */}
      {error ? (
        <div className="flex items-center justify-center h-full text-red-400">
          <div className="text-center">
            <AlertCircle className="w-8 h-8 mx-auto mb-2" />
            <div className="text-sm">Viewer Error</div>
            <div className="text-xs text-red-300">{error}</div>
          </div>
        </div>
      ) : (
        <Canvas
          camera={{ position: [3, 3, 3], fov: 60 }}
          onCreated={({ gl }) => {
            gl.setSize(gl.domElement.clientWidth, gl.domElement.clientHeight)
          }}
        >
          <Scene {...props} />
        </Canvas>
      )}

      {/* Help Text */}
      <div className="absolute bottom-4 left-4 right-4 text-center">
        <div className="bg-black/50 backdrop-blur-sm text-white/60 text-xs py-2 px-3 rounded-lg">
          {props.modelUrl ? 'Drag to rotate • Scroll to zoom • Right-click to pan' : 'Upload an image to begin 3D generation'}
        </div>
      </div>
    </div>
  )
}

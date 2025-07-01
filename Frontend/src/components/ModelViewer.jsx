// ModelViewer.jsx
import React, { useMemo, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF } from '@react-three/drei';
import * as THREE from 'three';
import './ModelViewer.css';

function Model({ url }) {
  const { scene } = useGLTF(url);

  useMemo(() => {
    scene.traverse((child) => {
      if (child.isMesh && !child.material) {
        child.material = new THREE.MeshStandardMaterial({ color: 'orange' });
      }
    });
  }, [scene]);

  return <primitive object={scene} />;
}

export default function ModelViewer({ glbBase64 }) {
  const { blobUrl, blob } = useMemo(() => {
    if (!glbBase64) return { blobUrl: null, blob: null };
    const byteCharacters = atob(glbBase64);
    const byteArray = new Uint8Array(
      Array.from(byteCharacters).map((char) => char.charCodeAt(0))
    );
    const blob = new Blob([byteArray], { type: 'model/gltf-binary' });
    return { blobUrl: URL.createObjectURL(blob), blob };
  }, [glbBase64]);

  const handleDownload = () => {
    if (!blob) return;
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'model.glb';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="model-viewer-container">
      {blob && (
        <button className="download-button" onClick={handleDownload}>
          ⬇ Download .glb
        </button>
      )}

      <div className="model-viewer-canvas">
        <h2 className="model-viewer-title">3D Model</h2>
        {blobUrl ? (
          <Canvas
            camera={{ position: [3, 3, 3], fov: 45 }}
            gl={{ physicallyCorrectLights: true }}
            onCreated={({ gl }) => {
              gl.toneMappingExposure = 10;
            }}
          >
            <color attach="background" args={['#f8fafc']} />
            <ambientLight intensity={1} />
            <directionalLight position={[5, 5, 5]} intensity={5} />
            {/* <directionalLight position={[0, 0, 5]} intensity={5} /> */}
            <directionalLight position={[-5,-5,-5]} intensity={5} />
           
            <Suspense fallback={null}>
              <Model url={blobUrl} />
            </Suspense>
            <OrbitControls target={[0, 0, 0]} />
              <OrbitControls enableDamping dampingFactor={0.5} />

            <OrbitControls />
          </Canvas>
        ) : (
          <p>No model available</p>
        )}
      </div>
    </div>
  );
}

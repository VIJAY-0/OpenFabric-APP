// ModelViewer.jsx
import React, { useMemo, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF } from '@react-three/drei';
import * as THREE from 'three';

function Model({ url }) {
  const { scene } = useGLTF(url);

  // Optional fallback material if model lacks one
  scene.traverse((child) => {
    if (child.isMesh && !child.material) {
      child.material = new THREE.MeshStandardMaterial({ color: 'orange' });
    }
  });

  return <primitive object={scene} />;
}

export default function ModelViewer({ glbBase64, imageBase64 }) {
  // Convert GLB Base64 to blob URL for rendering
  const { blobUrl, blob } = useMemo(() => {
    if (!glbBase64) return { blobUrl: null, blob: null };
    const byteCharacters = atob(glbBase64);
    const byteArray = new Uint8Array([...byteCharacters].map(c => c.charCodeAt(0)));
    const blob = new Blob([byteArray], { type: 'model/gltf-binary' });
    return { blobUrl: URL.createObjectURL(blob), blob };
  }, [glbBase64]);

  // Trigger download
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
    <div style={styles.container}>
       {blob && (
          <button style={styles.button} onClick={handleDownload}>
            ⬇ Download .glb
          </button>
        )}


      <div style={styles.right}>
        <h2 style={styles.title}>3D Model</h2>
        {blobUrl ? (
          <Canvas
            camera={{ position: [0, 0, 4], fov: 45 }}
            gl={{ physicallyCorrectLights: true }}
            onCreated={({ gl }) => {gl.toneMappingExposure = 1.7; }}
          >
            <color attach="background" args={['#f8fafc']} />
            <ambientLight intensity={0.7} />
            <directionalLight position={[3, 3, 3]} intensity={2.5} />
            <Suspense fallback={null}>
            <Model url={blobUrl} />
            </Suspense>
            <OrbitControls />
          </Canvas>


        ) : (
          <p>No model available</p>
        )}
      </div>
    </div>
  );
}

// ✨ Modern clean styles
const styles = {
  container: {
    display: 'flex',
    flexWrap: 'wrap',
    padding: '2rem',
    backgroundColor: '#f1f5f9',
    gap: '2rem',
    fontFamily: "'Inter', sans-serif",
    justifyContent: 'center',
    alignItems: 'flex-start',
    minHeight: '100vh',
  },
  left: {
    flex: '1 1 300px',
    maxWidth: '400px',
    textAlign: 'center',
  },
  right: {
    flex: '1 1 600px',
    height: '500px',
    maxWidth: '700px',
    backgroundColor: '#fff',
    borderRadius: '1rem',
    boxShadow: '0 0 20px rgba(0,0,0,0.1)',
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    maxHeight: '400px',
    objectFit: 'contain',
    borderRadius: '1rem',
    boxShadow: '0 0 10px rgba(0,0,0,0.1)',
  },
  title: {
    fontSize: '1.25rem',
    color: '#1e293b',
    marginBottom: '1rem',
  },
  button: {
    marginTop: '1rem',
    padding: '0.6rem 1.2rem',
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '0.5rem',
    fontSize: '1rem',
    cursor: 'pointer',
    boxShadow: '0 2px 8px rgba(59,130,246,0.3)',
  },
};

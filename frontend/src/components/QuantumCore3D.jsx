import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Float } from '@react-three/drei';
import * as THREE from 'three';

function ProceduralQuantumEngine() {
  const coreRef = useRef();
  const innerRef = useRef();
  const ring1Ref = useRef();
  const ring2Ref = useRef();
  const ring3Ref = useRef();
  const particlesRef = useRef();

  // Create floating ambient telemetry particles tightly bound
  const particleCount = 40;
  const particles = useMemo(() => {
    const p = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      const radius = 1.2 + Math.random() * 0.6;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      p[i] = radius * Math.sin(phi) * Math.cos(theta);
      p[i + 1] = radius * Math.sin(phi) * Math.sin(theta);
      p[i + 2] = radius * Math.cos(phi);
    }
    return p;
  }, []);

  useFrame((state, delta) => {
    if (coreRef.current) {
      coreRef.current.rotation.y += delta * 0.35;
      coreRef.current.rotation.x += delta * 0.18;
    }
    if (innerRef.current) {
      innerRef.current.rotation.y -= delta * 0.5;
      innerRef.current.rotation.z += delta * 0.25;
      const s = 0.48 + Math.sin(state.clock.elapsedTime * 2.5) * 0.03;
      innerRef.current.scale.set(s, s, s);
    }
    if (ring1Ref.current) {
      ring1Ref.current.rotation.x += delta * 0.4;
      ring1Ref.current.rotation.y += delta * 0.18;
    }
    if (ring2Ref.current) {
      ring2Ref.current.rotation.y += delta * 0.5;
      ring2Ref.current.rotation.z += delta * 0.22;
    }
    if (ring3Ref.current) {
      ring3Ref.current.rotation.z += delta * 0.35;
      ring3Ref.current.rotation.x += delta * 0.28;
    }
    if (particlesRef.current) {
      particlesRef.current.rotation.y += delta * 0.12;
    }
  });

  return (
    <group scale={0.88}>
      {/* Outer Faceted Icosahedron Crystal (Translucent Sapphire Glass) */}
      <mesh ref={coreRef}>
        <icosahedronGeometry args={[0.9, 0]} />
        <meshPhysicalMaterial
          color="#0f172a"
          emissive="#E5A93C"
          emissiveIntensity={0.25}
          roughness={0.08}
          metalness={0.15}
          transmission={0.88}
          thickness={1.5}
          transparent={true}
          opacity={0.85}
        />
      </mesh>

      {/* Outer Wireframe Octahedron Accent */}
      <mesh rotation={[0.4, 0.2, 0]}>
        <octahedronGeometry args={[1.05, 0]} />
        <meshBasicMaterial color="#E5A93C" wireframe={true} transparent={true} opacity={0.3} />
      </mesh>

      {/* Inner Glowing Amber Quantum Core (Dodecahedron) */}
      <mesh ref={innerRef}>
        <dodecahedronGeometry args={[0.48, 0]} />
        <meshStandardMaterial
          color="#E5A93C"
          emissive="#E5A93C"
          emissiveIntensity={2.5}
          roughness={0.2}
          metalness={0.8}
        />
      </mesh>

      {/* Orbital Gold Ring 1 */}
      <mesh ref={ring1Ref} rotation={[Math.PI / 4, 0, 0]}>
        <torusGeometry args={[1.25, 0.03, 24, 80]} />
        <meshStandardMaterial color="#E5A93C" metalness={0.95} roughness={0.15} />
      </mesh>

      {/* Orbital Gold Ring 2 */}
      <mesh ref={ring2Ref} rotation={[0, Math.PI / 3, Math.PI / 6]}>
        <torusGeometry args={[1.42, 0.03, 24, 80]} />
        <meshStandardMaterial color="#E5A93C" metalness={0.95} roughness={0.15} />
      </mesh>

      {/* Orbital Gold Ring 3 */}
      <mesh ref={ring3Ref} rotation={[Math.PI / 3, Math.PI / 4, 0]}>
        <torusGeometry args={[1.58, 0.03, 24, 80]} />
        <meshStandardMaterial color="#E5A93C" metalness={0.95} roughness={0.15} />
      </mesh>

      {/* Floating Amber Data Particles */}
      <points ref={particlesRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={particleCount}
            array={particles}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.035}
          color="#E5A93C"
          transparent={true}
          opacity={0.75}
          sizeAttenuation={true}
        />
      </points>
    </group>
  );
}

export default function QuantumCore3D() {
  return (
    <div className="w-full h-[460px] sm:h-[500px] relative select-none flex items-center justify-center overflow-visible">
      <Canvas
        camera={{ position: [0, 0, 6.2], fov: 38 }}
        gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
      >
        <ambientLight intensity={0.8} />
        <directionalLight position={[8, 12, 6]} intensity={2.2} color="#ffffff" />
        <directionalLight position={[-8, -10, -6]} intensity={0.8} color="#E5A93C" />
        <pointLight position={[0, 0, 0]} intensity={3.0} color="#E5A93C" distance={6} />

        <Float speed={1.8} rotationIntensity={0.15} floatIntensity={0.3}>
          <ProceduralQuantumEngine />
        </Float>

        <OrbitControls
          enableZoom={false}
          enablePan={false}
          autoRotate={false}
          rotateSpeed={0.6}
        />
      </Canvas>
    </div>
  );
}

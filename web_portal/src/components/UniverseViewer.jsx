import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function UniverseViewer() {
  const mountRef = useRef(null);

  useEffect(() => {
    const width = mountRef.current.clientWidth;
    const height = mountRef.current.clientHeight;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(width, height);
    mountRef.current.appendChild(renderer.domElement);

    // Example: Add a sphere for a planet
    const geometry = new THREE.SphereGeometry(1, 32, 32);
    const material = new THREE.MeshBasicMaterial({ color: 0x0077ff });
    const sphere = new THREE.Mesh(geometry, material);
    scene.add(sphere);

    camera.position.z = 5;

    function animate() {
      requestAnimationFrame(animate);
      sphere.rotation.y += 0.01;
      renderer.render(scene, camera);
    }
    animate();

    return () => {
      mountRef.current.removeChild(renderer.domElement);
    };
  }, []);

  return <div style={{ width: '100vw', height: '100vh' }} ref={mountRef}></div>;
} 
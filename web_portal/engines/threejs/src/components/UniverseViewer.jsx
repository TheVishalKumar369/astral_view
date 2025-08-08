import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import cosmicData from './cosmicData.json';

export default function EnhancedUniverseViewer() {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const [selectedObject, setSelectedObject] = useState(null);
  const [cameraSpeed, setCameraSpeed] = useState(1);

  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000011);
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      10000
    );
    camera.position.set(0, 0, 50);
    cameraRef.current = camera;

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    mountRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Create starfield background
    createStarfield(scene);

    // Create main cosmic objects
    createStars(scene);
    createPlanets(scene);

    // Controls
    const keys = {};
    let mouseX = 0;
    let mouseY = 0;

    // Event listeners
    const handleKeyDown = (event) => {
      keys[event.code] = true;
    };

    const handleKeyUp = (event) => {
      keys[event.code] = false;
    };

    const handleMouseMove = (event) => {
      mouseX = (event.clientX - window.innerWidth / 2) * 0.001;
      mouseY = (event.clientY - window.innerHeight / 2) * 0.001;
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);
    document.addEventListener('mousemove', handleMouseMove);

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);

      // Camera movement
      const speed = cameraSpeed;
      if (keys['KeyW']) {
        camera.position.add(
          new THREE.Vector3(0, 0, -speed).applyQuaternion(camera.quaternion)
        );
      }
      if (keys['KeyS']) {
        camera.position.add(
          new THREE.Vector3(0, 0, speed).applyQuaternion(camera.quaternion)
        );
      }
      if (keys['KeyA']) {
        camera.position.add(
          new THREE.Vector3(-speed, 0, 0).applyQuaternion(camera.quaternion)
        );
      }
      if (keys['KeyD']) {
        camera.position.add(
          new THREE.Vector3(speed, 0, 0).applyQuaternion(camera.quaternion)
        );
      }
      if (keys['Space']) {
        camera.position.y += speed;
      }
      if (keys['ShiftLeft']) {
        camera.position.y -= speed;
      }

      // Mouse look
      camera.rotation.y = -mouseX;
      camera.rotation.x = -mouseY;

      renderer.render(scene, camera);
    };

    animate();

    // Cleanup
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
      document.removeEventListener('mousemove', handleMouseMove);
      
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [cameraSpeed]);

  // Create starfield background
  const createStarfield = (scene) => {
    const starGeometry = new THREE.BufferGeometry();
    const starMaterial = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.1,
      sizeAttenuation: false
    });

    const starVertices = [];
    for (let i = 0; i < 10000; i++) {
      const x = (Math.random() - 0.5) * 2000;
      const y = (Math.random() - 0.5) * 2000;
      const z = (Math.random() - 0.5) * 2000;
      starVertices.push(x, y, z);
    }

    starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3));
    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);
  };

  // Create main catalog stars
  const createStars = (scene) => {
    cosmicData.stars.forEach((starData, index) => {
      const geometry = new THREE.SphereGeometry(starData.size, 16, 16);
      const material = new THREE.MeshBasicMaterial({
        color: new THREE.Color(starData.color.r, starData.color.g, starData.color.b)
      });

      const star = new THREE.Mesh(geometry, material);
      star.position.set(starData.position.x, starData.position.y, starData.position.z);

      // Add glow effect for bright stars
      if (starData.magnitude < 8) {
        const glowGeometry = new THREE.SphereGeometry(starData.size * 2, 16, 16);
        const glowMaterial = new THREE.MeshBasicMaterial({
          color: new THREE.Color(starData.color.r, starData.color.g, starData.color.b),
          transparent: true,
          opacity: 0.3
        });
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        glow.position.copy(star.position);
        scene.add(glow);
      }

      // Store metadata for interaction
      star.userData = starData;
      scene.add(star);
    });
  };

  // Create exoplanets (placeholder)
  const createPlanets = (scene) => {
    // This would be populated with actual exoplanet data
    console.log('Creating exoplanet systems...');
  };

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh' }}>
      <div ref={mountRef} style={{ width: '100%', height: '100%' }} />
      
      {/* UI Overlay */}
      <div style={{
        position: 'absolute',
        top: 20,
        left: 20,
        color: 'white',
        fontFamily: 'monospace',
        background: 'rgba(0,0,0,0.7)',
        padding: '10px',
        borderRadius: '5px'
      }}>
        <div>Controls: WASD to move, Mouse to look</div>
        <div>Space/Shift for up/down</div>
        <div>Speed: 
          <input 
            type="range" 
            min="0.1" 
            max="10" 
            step="0.1"
            value={cameraSpeed}
            onChange={(e) => setCameraSpeed(parseFloat(e.target.value))}
            style={{ marginLeft: '10px' }}
          />
          {cameraSpeed.toFixed(1)}
        </div>
        {selectedObject && (
          <div style={{ marginTop: '10px', borderTop: '1px solid white', paddingTop: '10px' }}>
            <strong>{selectedObject.display_name}</strong><br/>
            Type: {selectedObject.star_type}<br/>
            Distance: {selectedObject.distance_ly?.toFixed(1)} ly
          </div>
        )}
      </div>
    </div>
  );
}

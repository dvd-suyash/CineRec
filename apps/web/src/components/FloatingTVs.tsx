"use client";

import { useRef, useMemo, Suspense } from "react";
import { Canvas, useFrame, useLoader } from "@react-three/fiber";
import { Float, Environment, Plane } from "@react-three/drei";
import * as THREE from "three";

const POSTERS = [
"https://image.tmdb.org/t/p/w500/6rpvddXbaQPOi0fB2HKWbZ3uUSg.jpg",
"https://image.tmdb.org/t/p/w500/6Q6Zo6GNXMLP600OJSh6MhW21um.jpg",
"https://image.tmdb.org/t/p/w500/bArhvjRHl535XMaSh9VjInF2mSZ.jpg",
"https://image.tmdb.org/t/p/w500/lNBxToxHWrzmkqeFnf1XADUTxQq.jpg",
"https://image.tmdb.org/t/p/w500/4LwvU9SZc8QQzW1X1FAPhNbXnEU.jpg",
"https://image.tmdb.org/t/p/w500/2Abt2GgscAGtGAXTrhH44qPhugI.jpg",
"https://image.tmdb.org/t/p/w500/iOb2fjXLbpJgyQXe46n1WtGCnaa.jpg",
"https://image.tmdb.org/t/p/w500/yBKMAIj7clP42UkFejhGDBBoTpb.jpg",
"https://image.tmdb.org/t/p/w500/a2SnSbRxMB4vktOxZapaspY2fTC.jpg",
"https://image.tmdb.org/t/p/w500/rhGx6E3qRNMgj3i5su2oukNHwIQ.jpg",
"https://image.tmdb.org/t/p/w500/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg",
"https://image.tmdb.org/t/p/w500/yvirUYrva23IudARHn3mMGVxWqM.jpg",
"https://image.tmdb.org/t/p/w500/bAbBNVplg7h79sm94OyHeKk8Phz.jpg",
"https://image.tmdb.org/t/p/w500/oaZbbcJUKgw95EGIT7VTPLEzuB3.jpg",
"https://image.tmdb.org/t/p/w500/lmrulvLbmaejTix1YaMxo1oGhH1.jpg",
"https://image.tmdb.org/t/p/w500/oLld47ZT1I3iecM3OWhIphohQUJ.jpg",
"https://image.tmdb.org/t/p/w500/uxCaBoYXsDC4A0SqTm3SISj0OwK.jpg",
"https://image.tmdb.org/t/p/w500/321rzg1B6RRhcuRgsFHjQ7Xl3XX.jpg",
"https://image.tmdb.org/t/p/w500/Lr0Ng7Gg02RW1AyfYEL6P0WUvd.jpg",
"https://image.tmdb.org/t/p/w500/qnin56Syy5rbG7KCaxWY7SPuy6p.jpg",
"https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg",
"https://image.tmdb.org/t/p/w500/alpf5v4UqSFawPmG9RX03Or4BDk.jpg",
"https://image.tmdb.org/t/p/w500/AnJ8IQJI23hNpYXVNaythu061Ru.jpg",
"https://image.tmdb.org/t/p/w500/uwMKWjcNID0D9jjplsjkQS2OrB4.jpg",
"https://image.tmdb.org/t/p/w500/rsHEVjzxU8cxz1sm3vboj99daNv.jpg",
"https://image.tmdb.org/t/p/w500/3r0O6BW9USoZ9mteCVyNKMQriRL.jpg",
"https://image.tmdb.org/t/p/w500/13MmRwmG5NmaMfU8qNrtgGXisiD.jpg",
"https://image.tmdb.org/t/p/w500/3sgnSfNT27Bx5O5ukr7B26mhEQq.jpg",
"https://image.tmdb.org/t/p/w500/bRBeSHfGHwkEpImlhxPmOcUsaeg.jpg",
"https://image.tmdb.org/t/p/w500/oJ7g2CifqpStmoYQyaLQgEU32qO.jpg",
"https://image.tmdb.org/t/p/w500/9fbZdiOI9fRinl44mNm3CYgEtYR.jpg",
"https://image.tmdb.org/t/p/w500/yQvGrMoipbRoddT0ZR8tPoR7NfX.jpg",
"https://image.tmdb.org/t/p/w500/40jN1UgNAYEkGt2M0i81ghLF3cc.jpg",
"https://image.tmdb.org/t/p/w500/cHKo3m8N1fwvEy2ZEr0xGmmMODV.jpg",
"https://image.tmdb.org/t/p/w500/3PWJqDfygN0YNNjWsDUOXclCp3h.jpg",
"https://image.tmdb.org/t/p/w500/3HSov8EW2fI3oQbUJxOvnf684ej.jpg",
"https://image.tmdb.org/t/p/w500/7X5VhHwDaSLkrDoifRbfvGZJxFP.jpg",
"https://image.tmdb.org/t/p/w500/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg",
"https://image.tmdb.org/t/p/w500/fgSm5ylwiXbIHn8UbUXDjk9RRu4.jpg",
"https://image.tmdb.org/t/p/w500/sKnwnnmBpjo9BEskHtja6ToXUV1.jpg",
];

function TV({ url, position, rotation, speed }: any) {
  // Use our Next.js API proxy to bypass WebGL CORS restrictions on TMDB images
  const proxyUrl = `/api/image-proxy?url=${encodeURIComponent(url)}`;
  const texture = useLoader(THREE.TextureLoader, proxyUrl);
  texture.colorSpace = THREE.SRGBColorSpace;
  const mesh = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (!mesh.current) return;
    // Slowly float upwards
    mesh.current.position.y += speed;
    
    // Perfect grid wraparound logic
    // 5 rows total, spaced 14 units apart. Total height span = 70.
    if (mesh.current.position.y > 35) {
      mesh.current.position.y -= 70;
    }
  });

  return (
    <group ref={mesh} position={position} rotation={rotation}>
      <Float speed={1} rotationIntensity={0.1} floatIntensity={0.2}>
        {/* TV Bezel (CRT Box) */}
        <mesh castShadow receiveShadow>
          <boxGeometry args={[3.2, 4.4, 0.5]} />
          <meshStandardMaterial color="#0a0a0a" roughness={0.7} metalness={0.2} />
        </mesh>
        
        {/* Screen */}
        <mesh position={[0, 0, 0.26]}>
          <planeGeometry args={[2.8, 4.0]} />
          <meshBasicMaterial map={texture} toneMapped={false} />
        </mesh>
        
        {/* Screen Glass Glow/Reflection */}
        <mesh position={[0, 0, 0.27]}>
          <planeGeometry args={[2.8, 4.0]} />
          <meshPhysicalMaterial 
            transparent 
            opacity={0.3} 
            roughness={0.1} 
            metalness={0.9} 
            color="#a8b1ff"
          />
        </mesh>
      </Float>
    </group>
  );
}

function TVScene({ tvs }: { tvs: any[] }) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (!groupRef.current) return;
    // Parallax effect based on mouse movement
    groupRef.current.position.x = THREE.MathUtils.lerp(groupRef.current.position.x, (state.mouse.x * 2), 0.05);
    groupRef.current.position.y = THREE.MathUtils.lerp(groupRef.current.position.y, (state.mouse.y * 2), 0.05);
  });

  return (
    <group ref={groupRef}>
      <Suspense fallback={null}>
        {tvs.map((tv: any) => (
          <TV key={tv.id} {...tv} />
        ))}
        <Environment preset="night" />
      </Suspense>
    </group>
  );
}

export function FloatingTVs() {
  const tvs = useMemo(() => {
    return Array.from({ length: 45 }).map((_, i) => {
      const col = i % 9;
      const row = Math.floor(i / 9);
      
      // Calculate angles so the TVs slightly face the center Being
      const xPos = (col - 4) * 8; // Spaced by 8 units horizontally
      const yPos = (row - 2) * 14; // Spaced by 14 units vertically
      const rotY = xPos * -0.015; // The further left/right they are, the more they turn inward
      
      return {
        id: i,
        url: POSTERS[i % POSTERS.length],
        position: [
          xPos,
          yPos,
          -15 // Pushed back cleanly behind the Being
        ],
        rotation: [
          0,
          rotY,
          0
        ],
        speed: 0.04 // Fast unified movement
      };
    });
  }, []);

  return (
    <div className="absolute inset-0 z-0 pointer-events-none opacity-50">
      <Canvas camera={{ position: [0, 0, 10], fov: 60 }}>
        <ambientLight intensity={0.5} />
        <spotLight position={[10, 20, 10]} intensity={2} penumbra={1} color="#4338ca" />
        <spotLight position={[-10, -20, 10]} intensity={1.5} penumbra={1} color="#ec4899" />
        
        <TVScene tvs={tvs} />
      </Canvas>
    </div>
  );
}

"use client";

import React, { useEffect, useRef } from "react";
import gsap from "gsap";

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
"https://image.tmdb.org/t/p/w500/sKnwnnmBpjo9BEskHtja6ToXUV1.jpg"
];

export const InfiniteCanvas = ({
  imageSize = "10vw",
  numberOfImages = 150,
  gap = "2vw",
  className = "",
  isProcessing = false,
}: any) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const isProcessingRef = useRef(isProcessing);

  useEffect(() => {
    isProcessingRef.current = isProcessing;
  }, [isProcessing]);

  useEffect(() => {
    const container = containerRef.current;
    const wrapper = wrapperRef.current;
    if (!container || !wrapper) return;
    
    const items = gsap.utils.toArray(".canvas-item", container) as HTMLElement[];
    
    if (items.length === 0) return;

    let itemW = 0;
    let itemH = 0;
    let gapX = 0;
    let gapY = 0;
    let totalW = 0;
    let totalH = 0;
    let wrapX: any, wrapY: any;
    let cols = 0;
    let perfectCount = 0;
    let isMobile = false;

    const resize = () => {
      isMobile = window.innerWidth < 768;

      // Create a dummy element to measure exact gap in pixels
      const dummy = document.createElement("div");
      dummy.style.width = gap;
      dummy.style.height = gap;
      dummy.style.position = "absolute";
      container.appendChild(dummy);
      gapX = dummy.offsetWidth;
      gapY = dummy.offsetHeight;
      container.removeChild(dummy);

      itemW = items[0].offsetWidth;
      itemH = items[0].offsetHeight;

      if (isMobile) {
        // Mobile: use fixed pixel sizes for poster items to guarantee full coverage
        // We need enough columns * rows to tile the entire screen
        const mobileItemW = 80;  // px
        const mobileItemH = 120; // px
        const mobileGap = 8;     // px

        // Override measured values
        itemW = mobileItemW;
        itemH = mobileItemH;
        gapX = mobileGap;
        gapY = mobileGap;

        // Force items to be this size
        items.forEach(item => {
          item.style.width = `${mobileItemW}px`;
          item.style.height = `${mobileItemH}px`;
        });

        // Calculate cols/rows to tile at least 2x the screen in each direction for seamless wrapping
        cols = Math.ceil((window.innerWidth * 2) / (mobileItemW + mobileGap));
        cols = Math.min(cols, numberOfImages); // can't exceed total images
      } else {
        // Desktop: exact original math, untouched
        const screenAspect = window.innerWidth / window.innerHeight;
        const itemAspect = itemW / itemH;
        const targetCols = Math.sqrt(numberOfImages * screenAspect / itemAspect);
        cols = Math.round(targetCols);
        cols = Math.max(1, Math.min(cols, numberOfImages));
      }
      
      // Crucial fix: Floor the rows to ensure a perfect rectangle with no ragged remainder gaps
      const rows = Math.floor(numberOfImages / cols);
      perfectCount = cols * rows;

      totalW = cols * (itemW + gapX);
      totalH = rows * (itemH + gapY);

      wrapX = gsap.utils.wrap(-itemW - gapX / 2, totalW - itemW - gapX / 2);
      wrapY = gsap.utils.wrap(-itemH - gapY / 2, totalH - itemH - gapY / 2);

      items.forEach((item, i) => {
        if (i >= perfectCount) {
          gsap.set(item, { display: "none" });
          return;
        }
        gsap.set(item, { display: "block" });
        
        const col = i % cols;
        const row = Math.floor(i / cols);

        (item as any)._baseX = col * (itemW + gapX);
        (item as any)._baseY = row * (itemH + gapY);

        gsap.set(item, {
          x: (item as any)._baseX,
          y: (item as any)._baseY,
        });
      });
    };

    resize();
    window.addEventListener("resize", resize);

    let targetX = 0;
    let targetY = 0;
    let currentX = 0;
    let currentY = 0;

    let targetParallaxX = 0;
    let targetParallaxY = 0;
    let currentParallaxX = 0;
    let currentParallaxY = 0;

    let driftSpeedX = -0.7;
    let driftSpeedY = -0.7;

    const render = () => {
      // Dynamic high-speed spinning during AI processing
      if (isProcessingRef.current) {
        driftSpeedX += (-18 - driftSpeedX) * 0.02; // Spin fast horizontally
        driftSpeedY += (-2 - driftSpeedY) * 0.02;  // Slight vertical drift
      } else {
        driftSpeedX += (-0.7 - driftSpeedX) * 0.05; // Wind down gracefully
        driftSpeedY += (-0.7 - driftSpeedY) * 0.05;
      }

      targetX += driftSpeedX;
      targetY += driftSpeedY;

      currentX += (targetX - currentX) * 0.1;
      currentY += (targetY - currentY) * 0.1;

      currentParallaxX += (targetParallaxX - currentParallaxX) * 0.1;
      currentParallaxY += (targetParallaxY - currentParallaxY) * 0.1;

      if (wrapper) {
        gsap.set(wrapper, { x: currentParallaxX, y: currentParallaxY });
      }

      const centerX = window.innerWidth / 2;
      const centerY = window.innerHeight / 2;

      items.forEach((item, i) => {
        if (i >= perfectCount) return;

        const newX = wrapX((item as any)._baseX + currentX);
        const newY = wrapY((item as any)._baseY + currentY);

        if (isMobile) {
          // ===== MOBILE: Simple flat tiling, no 3D cylinder =====
          // Just position items in a flat infinite scrolling grid
          gsap.set(item, {
            display: "block",
            x: newX,
            y: newY,
            rotateX: 0,
            rotateY: 0,
            z: 0,
          });
        } else {
          // ===== DESKTOP: Original 3D Cylindrical Projection (UNTOUCHED) =====
          const circumference = totalW;
          const radius = circumference / (2 * Math.PI);
          
          const angleRad = (newX / circumference) * Math.PI * 2;
          
          const finalX = Math.sin(angleRad) * radius;
          const finalZ = -Math.cos(angleRad) * radius;
          
          // Original desktop culling
          if (finalZ > -100) {
            gsap.set(item, { display: "none" });
            return;
          }
          
          const offsetZ = -100;
          
          gsap.set(item, { 
            display: "block",
            x: centerX + finalX - (itemW / 2),
            y: newY,
            rotationY: angleRad * (180 / Math.PI),
            rotationX: 0,
            z: finalZ + offsetZ
          });
        }
      });
    };

    gsap.ticker.add(render);

    let isDragging = false;
    let startX = 0;
    let startY = 0;

    const onPointerDown = (e: PointerEvent) => {
      isDragging = true;
      startX = e.clientX;
      startY = e.clientY;
      container.style.cursor = "grabbing";
    };

    const onPointerMove = (e: PointerEvent) => {
      if (isDragging) {
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        targetX += dx;
        targetY += dy;
        startX = e.clientX;
        startY = e.clientY;
      } else {
        const { innerWidth, innerHeight } = window;
        targetParallaxX = (e.clientX / innerWidth - 0.5) * -50;
        targetParallaxY = (e.clientY / innerHeight - 0.5) * -50;
      }
    };

    const onPointerUp = () => {
      isDragging = false;
      container.style.cursor = "grab";
    };

    const onPointerLeave = () => {
      isDragging = false;
      container.style.cursor = "grab";
      targetParallaxX = 0;
      targetParallaxY = 0;
    };

    const onWheel = (e: WheelEvent) => {
      targetX -= e.deltaX;
      targetY -= e.deltaY;
    };

    container.addEventListener("pointerdown", onPointerDown);
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onPointerUp);
    container.addEventListener("pointerleave", onPointerLeave);
    container.addEventListener("wheel", onWheel, { passive: true });

    return () => {
      window.removeEventListener("resize", resize);
      gsap.ticker.remove(render);
      container.removeEventListener("pointerdown", onPointerDown);
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onPointerUp);
      container.removeEventListener("pointerleave", onPointerLeave);
      container.removeEventListener("wheel", onWheel);
    };
  }, [numberOfImages, gap]);

  return (
    <div
      ref={containerRef}
      className={`relative overflow-hidden w-full h-full bg-transparent cursor-grab select-none touch-none ${className}`}
      style={{ perspective: typeof window !== "undefined" && window.innerWidth >= 768 ? "1500px" : "none" }}
    >
      <div
        ref={wrapperRef}
        className="absolute top-0 left-0 w-full h-full pointer-events-none [transform-style:preserve-3d]" 
      >
        {Array.from({ length: numberOfImages }).map((_, i) => (
          <div
            key={i}
            className="canvas-item absolute top-0 left-0 overflow-visible"
            style={{
              width: imageSize,
              height: `calc(${imageSize} * 1.5)`, 
            }}
          >
            <div className="w-full h-full overflow-hidden rounded-xl transition-transform duration-500 ease-out shadow-[0_0_40px_rgba(0,0,0,0.8)]">
              <img
                src={`/api/image-proxy?url=${encodeURIComponent(POSTERS[i % POSTERS.length])}`}
                alt={`Movie poster ${i}`}
                className="w-full h-full object-cover pointer-events-auto opacity-[0.35] saturate-50 contrast-125 hover:saturate-100 hover:opacity-100 hover:scale-105 hover:z-50 transition-all duration-700 ease-out"
                draggable={false}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

"use client";

import { motion, Variants, useMotionValue, useTransform, useSpring } from "framer-motion";
import { useEffect, useRef } from "react";

export type OrbState = 
  | "IDLE"
  | "INPUT"
  | "PROCESSING"
  | "FOLLOW-UP"
  | "SEARCHING"
  | "SYNTHESIZING"
  | "RECOMMENDING"
  | "WAITING_FOR_FEEDBACK"
  | "REFINING"
  | "ERROR";

interface OrbProps {
  state: OrbState;
}

export function Orb({ state }: OrbProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  // gpt-taste / framer-motion-animator: Mouse tracking for 3D tilt
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  // Smooth springs for the 3D rotation (Slow In / Slow Out & Follow Through)
  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [10, -10]), { damping: 30, stiffness: 200 });
  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-15, 15]), { damping: 30, stiffness: 200 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      mouseX.set(e.clientX / window.innerWidth - 0.5);
      mouseY.set(e.clientY / window.innerHeight - 0.5);
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [mouseX, mouseY]);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.play().catch(e => console.log("Video autoplay prevented:", e));
    }
  }, []);

  // 12 Principles: Exaggeration (speeding up video when processing)
  useEffect(() => {
    if (videoRef.current) {
      if (state === "PROCESSING") {
        videoRef.current.playbackRate = 2.0; 
      } else {
        videoRef.current.playbackRate = 1.0; 
      }
    }
  }, [state]);

  // joy-delight & 12 principles physics
  const variants: Variants = {
    IDLE: {
      scale: 0.75,
      opacity: 1,
      y: [0, -15, 0], // Gentle floating (Follow Through)
      filter: "drop-shadow(0px 30px 60px rgba(0, 0, 0, 0.7))",
      transition: { 
        y: { repeat: Infinity, duration: 6, ease: "easeInOut" },
        scale: { duration: 0.8, ease: "easeOut" }
      },
    },
    INPUT: {
      scale: 1.0, // Anticipation - zooms up to full massive size
      y: -5,
      opacity: 1,
      filter: "drop-shadow(0px 20px 80px rgba(99, 102, 241, 0.5)) drop-shadow(0px 0px 20px rgba(99, 102, 241, 0.3))",
      transition: { type: "spring", stiffness: 400, damping: 25 },
    },
    PROCESSING: {
      scaleX: [1, 1.05, 0.95, 1], // Squash and Stretch around full size
      scaleY: [1, 0.95, 1.05, 1],
      opacity: 1,
      filter: [
        "drop-shadow(0px 0px 80px rgba(139, 92, 246, 0.8)) drop-shadow(0px 0px 20px rgba(139, 92, 246, 0.6))",
        "drop-shadow(0px 0px 120px rgba(236, 72, 153, 0.9)) drop-shadow(0px 0px 40px rgba(236, 72, 153, 0.7))",
        "drop-shadow(0px 0px 80px rgba(139, 92, 246, 0.8)) drop-shadow(0px 0px 20px rgba(139, 92, 246, 0.6))"
      ],
      transition: { repeat: Infinity, duration: 1.2, ease: "easeInOut" },
    },
    RECOMMENDING: {
      scale: 0.75, // Shrink back down to give space for the movie cards
      opacity: 1,
      filter: "drop-shadow(0px 20px 100px rgba(16, 185, 129, 0.6)) drop-shadow(0px 0px 40px rgba(16, 185, 129, 0.8))",
      transition: { type: "spring", stiffness: 350, damping: 15 },
    },
    ERROR: {
      scale: 0.7,
      opacity: 1,
      filter: "drop-shadow(0px 0px 80px rgba(239, 68, 68, 0.8))",
      x: [-20, 20, -20, 20, 0], // Exaggeration shake
      transition: { duration: 0.5 },
    },
    "FOLLOW-UP": {
      scale: 0.75,
      opacity: 1,
      y: [0, -15, 0],
      filter: "drop-shadow(0px 30px 60px rgba(0, 0, 0, 0.7))",
      transition: { 
        y: { repeat: Infinity, duration: 6, ease: "easeInOut" },
        scale: { duration: 0.8, ease: "easeOut" }
      },
    }
  };

  return (
    <div className="flex flex-col items-center justify-center py-4 relative z-50 pointer-events-none perspective-[1000px]">
      <motion.div
        className="relative w-96 md:w-[28rem] lg:w-[32rem] aspect-square transform-gpu"
        variants={variants}
        animate={state}
        initial="IDLE"
        style={{ rotateX, rotateY }} // Mouse parallax
      >
        <video 
          ref={videoRef}
          src="/ominous-being.webm" 
          loop
          muted 
          playsInline 
          // Solid Drawing: The video element maintains volume and bounds, no artificial cropping
          className="absolute inset-0 size-full object-contain pointer-events-none"
        />
      </motion.div>
    </div>
  );
}

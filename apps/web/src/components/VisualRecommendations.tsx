"use client";

import { motion, useMotionValue, useTransform, useSpring, AnimatePresence } from "framer-motion";
import { useState, useRef, useEffect, Fragment } from "react";
import { XIcon, StarIcon, PlayIcon } from "lucide-react";

interface Movie {
  title: string;
  year: string;
  tmdb_id: number;
  poster_path: string;
  justification: string;
  rating?: number;
}

interface VisualRecommendationsProps {
  vibeTitle: string;
  movies: Movie[];
  onModalChange?: (isOpen: boolean) => void;
}

function CinematicCard({ movie, index, onClick }: { movie: Movie; index: number; onClick: () => void }) {
  const ref = useRef<HTMLDivElement>(null);
  const mouseX = useMotionValue(0.5);
  const mouseY = useMotionValue(0.5);

  const rotateX = useSpring(useTransform(mouseY, [0, 1], [10, -10]), { damping: 30, stiffness: 200 });
  const rotateY = useSpring(useTransform(mouseX, [0, 1], [-10, 10]), { damping: 30, stiffness: 200 });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    mouseX.set((e.clientX - rect.left) / rect.width);
    mouseY.set((e.clientY - rect.top) / rect.height);
  };

  const handleMouseLeave = () => {
    mouseX.set(0.5);
    mouseY.set(0.5);
  };

  const posterUrl = movie.poster_path 
    ? `/api/image-proxy?url=${encodeURIComponent(`https://image.tmdb.org/t/p/w780${movie.poster_path}`)}`
    : "/placeholder.jpg";

  return (
    <motion.div
      ref={ref}
      layoutId={`card-${movie.tmdb_id || movie.title}`}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ rotateX, rotateY, perspective: 1000 }}
      variants={{
        hidden: { opacity: 0, y: 50, scale: 0.9, rotateX: -20 },
        visible: { opacity: 1, y: 0, scale: 1, rotateX: 0 }
      }}
      className="relative group cursor-pointer h-[14rem] md:h-[18rem] flex-1 min-w-[120px] rounded-xl overflow-hidden shadow-2xl border border-white/10 hover:z-40 transition-z"
    >
      <div className="absolute inset-0 bg-zinc-950" />
      
      {movie.poster_path ? (
        <motion.img
          layoutId={`poster-${movie.tmdb_id || movie.title}`}
          src={`/api/image-proxy?url=${encodeURIComponent(`https://image.tmdb.org/t/p/w780${movie.poster_path}`)}`}
          alt={movie.title}
          className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
        />
      ) : (
        <motion.div
          layoutId={`poster-${movie.tmdb_id || movie.title}`}
          className="absolute inset-0 w-full h-full bg-gradient-to-br from-zinc-800 via-zinc-900 to-black transition-transform duration-700 group-hover:scale-105 flex items-center justify-center p-8 text-center"
        >
          {/* Abstract noise overlay for missing posters */}
          <div className="absolute inset-0 opacity-20 mix-blend-overlay bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDAiIGhlaWdodD0iNDAwIj48ZmlsdGVyIGlkPSJuIj48ZmVUdXJidWxlbmNlIHR5cGU9ImZyYWN0YWxOb2lzZSIgYmFzZUZyZXF1ZW5jeT0iMC44IiBudW1PY3RhdmVzPSIzIiBzdGl0Y2hUaWxlcz0ic3RpdGNoIi8+PC9maWx0ZXI+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsdGVyPSJ1cmwoI24pIi8+PC9zdmc+')] pointer-events-none" />
          <div className="opacity-10 pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_center,white_0%,transparent_100%)]" />
        </motion.div>
      )}

      <motion.div
        className="absolute inset-0 pointer-events-none z-20 mix-blend-overlay opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{
          background: useTransform(
            [mouseX, mouseY],
            ([x, y]: number[]) => `radial-gradient(circle at ${x * 100}% ${y * 100}%, rgba(255,255,255,0.8) 0%, transparent 50%)`
          )
        }}
      />

      <motion.div 
        layoutId={`meta-${movie.tmdb_id || movie.title}`}
        className="absolute inset-x-0 bottom-0 p-6 pt-12 bg-gradient-to-t from-black/95 via-black/80 to-transparent backdrop-blur-[2px] transform translate-y-2 group-hover:translate-y-0 transition-all duration-500"
      >
        <div className="font-mono text-[10px] text-white/50 tracking-widest uppercase mb-2 flex items-center gap-2">
          <span>{movie.year}</span>
          {movie.rating && (
            <>
              <span>•</span>
              <span className="flex items-center text-amber-400 font-bold">
                <StarIcon className="size-3 mr-1 fill-amber-400" />
                {movie.rating}
              </span>
            </>
          )}
        </div>
        <h3 className="text-xl md:text-2xl font-black text-white tracking-tighter leading-none mb-2 line-clamp-2">
          {movie.title}
        </h3>
        <p className="text-xs md:text-sm text-white/70 line-clamp-2 leading-relaxed opacity-0 group-hover:opacity-100 transition-opacity duration-500 delay-75">
          {movie.justification}
        </p>
      </motion.div>
    </motion.div>
  );
}

export function VisualRecommendations({ vibeTitle, movies, onModalChange }: VisualRecommendationsProps) {
  const [selectedId, setSelectedId] = useState<number | string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    onModalChange?.(selectedId !== null);
    if (selectedId === null) {
      setIsPlaying(false);
    }
  }, [selectedId, onModalChange]);

  if (!movies || movies.length === 0) return null;

  const selectedMovie = movies.find(m => (m.tmdb_id || m.title) === selectedId);

  return (
    <>
      <div className="w-full my-8">
        <motion.h2 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-xl md:text-2xl font-bold text-[#CCFF00] tracking-widest mb-8 px-4 uppercase text-center"
        >
          {vibeTitle}
        </motion.h2>

        <motion.div 
          initial="hidden"
          animate="visible"
          variants={{
            hidden: { opacity: 0 },
            visible: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.1 } }
          }}
          className="flex justify-between items-center w-full relative z-10 px-2 md:px-8"
        >
          {/* Left Wing */}
          <div className="flex flex-wrap md:flex-nowrap gap-4 w-full md:w-[40%] justify-center md:justify-end">
            {movies.slice(0, Math.ceil(movies.length / 2)).map((movie, i) => (
              <CinematicCard 
                key={movie.tmdb_id || movie.title} 
                movie={movie} 
                index={i} 
                onClick={() => setSelectedId(movie.tmdb_id || movie.title)} 
              />
            ))}
          </div>

          {/* Central Void for Arachne */}
          <div className="hidden md:block w-[20%] pointer-events-none flex-shrink-0" />

          {/* Right Wing */}
          <div className="flex flex-wrap md:flex-nowrap gap-4 w-full md:w-[40%] justify-center md:justify-start">
            {movies.slice(Math.ceil(movies.length / 2)).map((movie, i) => (
              <CinematicCard 
                key={movie.tmdb_id || movie.title} 
                movie={movie} 
                index={i + Math.ceil(movies.length / 2)} 
                onClick={() => setSelectedId(movie.tmdb_id || movie.title)} 
              />
            ))}
          </div>
        </motion.div>
      </div>

      <AnimatePresence>
        {selectedId && selectedMovie && (
          <div key="modal" className="fixed inset-0 z-[200] flex items-center justify-center p-4 md:p-12">
            {/* Massive WebGL-like Background Blur */}
            <motion.div 
              initial={{ opacity: 0, backdropFilter: "blur(0px)" }}
              animate={{ opacity: 1, backdropFilter: "blur(40px)" }}
              exit={{ opacity: 0, backdropFilter: "blur(0px)" }}
              transition={{ duration: 0.5 }}
              className="absolute inset-0 bg-black/60 cursor-pointer"
              onClick={() => setSelectedId(null)}
            />

            {/* Gapless Editorial Popup */}
            <motion.div 
              layoutId={`card-${selectedMovie.tmdb_id}`}
              className="relative w-full max-w-6xl h-[85vh] bg-zinc-950 rounded-3xl overflow-hidden shadow-[0_0_100px_rgba(0,0,0,0.8)] border border-white/5 flex flex-col md:flex-row pointer-events-auto"
            >
              {/* Close Button */}
              <button 
                onClick={() => {
                  if (isPlaying) setIsPlaying(false);
                  else setSelectedId(null);
                }}
                className="absolute top-6 right-6 z-50 size-12 bg-black/50 hover:bg-white text-white hover:text-black backdrop-blur-xl rounded-full flex items-center justify-center transition-all"
              >
                <XIcon className="size-5" />
              </button>

              {isPlaying ? (
                <div className="w-full h-full bg-black relative flex items-center justify-center">
                  <iframe
                    src={`https://vidhive.lol/embed/movie/${selectedMovie.tmdb_id}?autoPlay=true&theme=CCFF00`}
                    className="absolute inset-0 w-full h-full"
                    frameBorder="0"
                    allowFullScreen
                    allow="autoplay; fullscreen; encrypted-media; picture-in-picture"
                  ></iframe>
                </div>
              ) : (
                <>
                  {/* Left Column: Poster Morph */}
                  <div className="w-full md:w-1/2 h-1/2 md:h-full relative bg-black group">
                    {selectedMovie.poster_path ? (
                      <motion.img
                        layoutId={`poster-${selectedMovie.tmdb_id || selectedMovie.title}`}
                        src={`/api/image-proxy?url=${encodeURIComponent(`https://image.tmdb.org/t/p/original${selectedMovie.poster_path}`)}`}
                        alt={selectedMovie.title}
                        className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                      />
                    ) : (
                      <motion.div
                        layoutId={`poster-${selectedMovie.tmdb_id || selectedMovie.title}`}
                        className="absolute inset-0 w-full h-full bg-gradient-to-br from-zinc-800 via-zinc-900 to-black flex items-center justify-center p-8 text-center"
                      >
                        <div className="absolute inset-0 opacity-20 mix-blend-overlay bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDAiIGhlaWdodD0iNDAwIj48ZmlsdGVyIGlkPSJuIj48ZmVUdXJidWxlbmNlIHR5cGU9ImZyYWN0YWxOb2lzZSIgYmFzZUZyZXF1ZW5jeT0iMC44IiBudW1PY3RhdmVzPSIzIiBzdGl0Y2hUaWxlcz0ic3RpdGNoIi8+PC9maWx0ZXI+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsdGVyPSJ1cmwoI24pIi8+PC9zdmc+')] pointer-events-none" />
                        <div className="opacity-10 pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_center,white_0%,transparent_100%)]" />
                      </motion.div>
                    )}
                    
                    {/* Play Button Overlay */}
                    <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity z-20 pointer-events-none">
                      <button 
                        onClick={() => setIsPlaying(true)}
                        className="size-24 rounded-full bg-[#CCFF00] pointer-events-auto hover:scale-110 flex items-center justify-center transition-transform shadow-[0_0_50px_rgba(204,255,0,0.4)]"
                      >
                        <PlayIcon className="size-10 text-black fill-black ml-2" />
                      </button>
                    </div>

                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-transparent to-zinc-950/80 hidden md:block pointer-events-none" />
                    <div className="absolute inset-0 bg-gradient-to-t from-zinc-950 via-transparent to-transparent md:hidden pointer-events-none" />
                  </div>

                  {/* Right Column: Editorial Typography */}
                  <motion.div 
                    layoutId={`meta-${selectedMovie.tmdb_id || selectedMovie.title}`}
                    className="w-full md:w-1/2 h-1/2 md:h-full p-6 md:p-16 flex flex-col justify-start md:justify-center relative bg-zinc-950 overflow-y-auto scrollbar-none"
                  >
                    <motion.div
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.2, duration: 0.5 }}
                    >
                      <div className="font-mono text-sm md:text-base text-white/40 tracking-[0.3em] uppercase mb-6 flex gap-4 items-center">
                        <span>{selectedMovie.year}</span>
                        <span>•</span>
                        {selectedMovie.rating && (
                          <>
                            <span className="flex items-center text-amber-400 font-bold">
                              <StarIcon className="size-4 mr-2 fill-amber-400" />
                              {selectedMovie.rating}
                            </span>
                            <span>•</span>
                          </>
                        )}
                        <span>CINEREC MATCH</span>
                      </div>
                      
                      <h2 className="text-4xl md:text-7xl font-black text-white tracking-tighter leading-[0.95] mb-6 md:mb-8">
                        {selectedMovie.title}
                      </h2>
                      
                      <div className="h-px w-24 bg-white/20 mb-8" />
                      
                      <p className="text-lg md:text-2xl font-light text-white/70 leading-relaxed max-w-lg mb-8 md:mb-12">
                        {selectedMovie.justification}
                      </p>

                      <button 
                        onClick={() => setIsPlaying(true)}
                        className="px-8 py-4 bg-[#CCFF00] hover:bg-white text-black font-black uppercase tracking-widest text-sm rounded-full transition-colors flex items-center justify-center gap-3 w-fit"
                      >
                        <PlayIcon className="size-5 fill-black" />
                        Watch Film
                      </button>
                    </motion.div>
                  </motion.div>
                </>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}

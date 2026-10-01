"use client";

import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeftIcon, PlayIcon, XIcon, CheckIcon, HistoryIcon } from "lucide-react";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Dashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [playingId, setPlayingId] = useState<string | null>(null);

  const fetchDashboard = async () => {
    if (status !== "authenticated") return;
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/dashboard/`, {
        headers: {
          "Authorization": `Bearer ${(session as any).accessToken}`
        }
      });
      if (res.ok) {
        const json = await res.json();
        setData(json.data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, [status]);

  const markAsWatched = async (e: React.MouseEvent, dbId: string) => {
    e.stopPropagation();
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/history/movies/${dbId}`, {
        method: 'POST',
        headers: {
          "Authorization": `Bearer ${(session as any).accessToken}`
        }
      });
      if (res.ok) {
        fetchDashboard();
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (status === "loading") {
    return <div className="min-h-screen bg-black text-white flex items-center justify-center font-bold uppercase tracking-widest text-xs">Loading...</div>;
  }

  if (status === "unauthenticated") {
    router.push("/");
    return null;
  }

  return (
    <main className="min-h-screen bg-black text-white selection:bg-[#CCFF00] selection:text-black overflow-x-hidden">
      {/* NAV */}
      <nav className="fixed top-0 left-0 w-full z-50 p-6 md:p-12 pointer-events-none flex justify-between items-center mix-blend-difference">
        <Link href="/" className="pointer-events-auto flex items-center gap-4 group">
          <div className="size-10 rounded-full border border-white/20 flex items-center justify-center group-hover:bg-white group-hover:text-black transition-all">
            <ArrowLeftIcon className="size-4" />
          </div>
          <span className="font-bold uppercase tracking-widest text-xs opacity-50 group-hover:opacity-100 transition-opacity">Back to Weave</span>
        </Link>
      </nav>

      <div className="max-w-[1600px] mx-auto px-6 md:px-12 pt-32 pb-24">
        
        {/* HEADER */}
        <header className="mb-24 mt-12 md:mt-24">
          <h1 className="text-6xl md:text-[8vw] font-black tracking-tighter leading-none mb-6">
            Neural <br/> <span className="text-[#CCFF00]">Footprint.</span>
          </h1>
          <p className="text-xl md:text-2xl font-light text-white/50 max-w-2xl leading-relaxed">
            A comprehensive mapping of your cinematic psychology, aesthetic preferences, and watch history.
          </p>
        </header>

        {/* BENTO GRID */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-32">
          
          {/* Card 1: DNA */}
          <motion.div 
            whileHover={{ scale: 0.98 }}
            className="md:col-span-2 md:row-span-2 bg-white/5 border border-white/10 rounded-3xl p-6 md:p-12 flex flex-col justify-between aspect-square md:aspect-auto overflow-hidden relative group"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-[#CCFF00]/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
            <div className="relative z-10">
              <h2 className="text-4xl font-bold tracking-tight mb-2">Taste Signature</h2>
              <p className="text-white/50 text-sm">Derived from interactions</p>
            </div>
            
            <div className="relative z-10 mt-12 space-y-6 w-full max-w-md">
              {(data?.dna || []).map((item: any) => (
                <div key={item.trait}>
                  <div className="flex justify-between text-xs font-bold uppercase tracking-widest text-white/70 mb-3">
                    <span>{item.trait}</span>
                    <span>{item.percentage}%</span>
                  </div>
                  <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      whileInView={{ width: `${item.percentage}%` }}
                      viewport={{ once: true }}
                      transition={{ duration: 1.5, ease: "easeOut", delay: 0.2 }}
                      className="h-full bg-[#CCFF00]"
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Card 2: Recent Memory */}
          <motion.div 
            whileHover={{ scale: 0.98 }}
            className="bg-zinc-900 border border-white/10 rounded-3xl p-6 md:p-8 flex flex-col justify-between group relative overflow-hidden"
          >
             <div className="absolute -right-10 -top-10 size-40 bg-white/5 rounded-full blur-3xl group-hover:bg-[#CCFF00]/20 transition-colors duration-1000" />
            <div className="relative z-10">
              <h3 className="text-2xl font-bold mb-4">Core Memory</h3>
              <p className="text-white/60 text-base leading-relaxed italic line-clamp-4">
                &quot;{data?.memories?.[0] || 'Arachne is watching. Your cinematic essence is still forming.'}&quot;
              </p>
            </div>
          </motion.div>

          {/* Card 3: Stat Box */}
          <motion.div 
            whileHover={{ scale: 0.98 }}
            className="bg-[#CCFF00] text-black border border-[#CCFF00]/50 rounded-3xl p-6 md:p-8 flex flex-col justify-end min-h-[240px] group relative overflow-hidden"
          >
            <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 mix-blend-overlay transition-opacity duration-500" />
            <div className="relative z-10">
              <div className="text-5xl md:text-7xl font-black tracking-tighter leading-none mb-2">{data?.stats?.watchlist_count || 0}</div>
              <div className="text-sm font-bold uppercase tracking-widest opacity-70">Watchlist Size</div>
              <div className="mt-4 pt-4 border-t border-black/10">
                 <div className="text-3xl font-black tracking-tighter leading-none mb-1">{data?.stats?.history_count || 0}</div>
                 <div className="text-xs font-bold uppercase tracking-widest opacity-70">Movies Watched</div>
              </div>
            </div>
          </motion.div>

          {/* Card 4: Most Explored Director */}
          <motion.div 
            whileHover={{ scale: 0.98 }}
            className="md:col-span-2 bg-gradient-to-r from-zinc-900 to-black border border-white/10 rounded-3xl p-6 md:p-12 flex items-center justify-between overflow-hidden relative group"
          >
            <div className="absolute right-0 top-0 bottom-0 w-2/3 md:w-1/2 opacity-20 mix-blend-luminosity bg-cover bg-center transition-transform duration-1000 group-hover:scale-110" style={{ backgroundImage: `url('${data?.fixation?.image || ''}')` }} />
            <div className="absolute inset-0 bg-gradient-to-r from-zinc-900 via-zinc-900/80 to-transparent" />
            
            <div className="relative z-10 w-full md:w-2/3">
              <h3 className="text-xs font-bold uppercase tracking-widest text-white/50 mb-3">Frequent Fixation</h3>
              <div className="text-4xl md:text-5xl font-black tracking-tighter text-white mb-4 leading-none">{data?.fixation?.name || 'Unknown'}</div>
              <p className="text-white/60 text-base">{data?.fixation?.stat || ''}</p>
            </div>
          </motion.div>
        </section>

        {/* HORIZONTAL SCROLL WATCHLIST */}
        <section className="mb-32">
          <div className="flex items-end justify-between mb-12">
            <h2 className="text-4xl md:text-5xl font-black tracking-tighter">Your Watchlist</h2>
          </div>
          
          <div className="flex gap-6 overflow-x-auto pb-12 snap-x snap-mandatory scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
            {(!data?.watchlist || data.watchlist.length === 0) && (
                <div className="text-white/30 italic">Your watchlist is currently empty.</div>
            )}
            {(data?.watchlist || []).map((movie: any) => (
              <motion.div 
                key={movie.id}
                className="shrink-0 w-[280px] md:w-[320px] snap-center group cursor-pointer"
                whileHover={{ y: -10 }}
              >
                <div className="w-full aspect-[2/3] rounded-2xl overflow-hidden relative mb-5 shadow-2xl border border-white/10 group-hover:border-white/30 transition-colors">
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity z-10 flex flex-col items-center justify-center backdrop-blur-sm gap-4">
                    
                    <button 
                        onClick={() => setPlayingId(movie.id)}
                        className="bg-[#CCFF00] text-black w-40 py-3 rounded-full font-bold uppercase tracking-widest text-xs flex items-center justify-center gap-2 scale-75 group-hover:scale-100 transition-all duration-300 hover:bg-white"
                    >
                        <PlayIcon className="size-4 fill-black" />
                        Watch Movie
                    </button>

                    <button 
                        onClick={(e) => markAsWatched(e, movie.db_id)}
                        className="bg-zinc-900 text-white border border-white/20 w-40 py-3 rounded-full font-bold uppercase tracking-widest text-xs flex items-center justify-center gap-2 scale-75 group-hover:scale-100 transition-all duration-300 hover:bg-white hover:text-black hover:border-white delay-75"
                    >
                        <CheckIcon className="size-4" />
                        Watched
                    </button>

                  </div>
                  <img src={movie.poster} alt={movie.title} className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110" />
                </div>
                <h3 className="text-xl font-bold tracking-tight mb-1">{movie.title}</h3>
                <p className="text-white/50 text-sm font-medium">{movie.year}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* HISTORY SECTION */}
        <section className="mb-32">
          <div className="flex items-end justify-between mb-12">
            <h2 className="text-4xl md:text-5xl font-black tracking-tighter flex items-center gap-4">
              <HistoryIcon className="size-10 text-white/30" />
              Viewing History
            </h2>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
            {(!data?.history || data.history.length === 0) && (
                <div className="text-white/30 italic col-span-full">No viewing history yet.</div>
            )}
            {(data?.history || []).map((movie: any) => (
              <motion.div 
                key={movie.id}
                className="group cursor-pointer"
                whileHover={{ y: -5 }}
                onClick={() => setPlayingId(movie.id)}
              >
                <div className="w-full aspect-[2/3] rounded-xl overflow-hidden relative mb-3 shadow-xl border border-white/5 group-hover:border-[#CCFF00]/50 transition-colors">
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity z-10 flex items-center justify-center backdrop-blur-sm">
                    <div className="size-12 rounded-full bg-[#CCFF00] flex items-center justify-center scale-75 group-hover:scale-100 transition-transform duration-300">
                      <PlayIcon className="size-5 text-black fill-black ml-1" />
                    </div>
                  </div>
                  <img src={movie.poster} alt={movie.title} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105 opacity-60 group-hover:opacity-100" />
                  <div className="absolute top-2 right-2 bg-black/80 backdrop-blur-md size-6 rounded-full flex items-center justify-center border border-white/10">
                     <CheckIcon className="size-3 text-[#CCFF00]" />
                  </div>
                </div>
                <h3 className="text-sm font-bold tracking-tight mb-1 truncate text-white/70 group-hover:text-white transition-colors">{movie.title}</h3>
              </motion.div>
            ))}
          </div>
        </section>

      </div>

      {/* DASHBOARD VIDEO MODAL */}
      <AnimatePresence>
        {playingId && (
          <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 md:p-12">
            <motion.div 
              initial={{ opacity: 0, backdropFilter: "blur(0px)" }}
              animate={{ opacity: 1, backdropFilter: "blur(40px)" }}
              exit={{ opacity: 0, backdropFilter: "blur(0px)" }}
              className="absolute inset-0 bg-black/80 cursor-pointer"
              onClick={() => setPlayingId(null)}
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="relative w-full max-w-6xl aspect-video bg-black rounded-3xl overflow-hidden shadow-[0_0_100px_rgba(0,0,0,0.8)] border border-white/10 z-10"
            >
              <button 
                onClick={() => setPlayingId(null)}
                className="absolute top-6 right-6 z-50 size-12 bg-black/50 hover:bg-[#CCFF00] text-white hover:text-black backdrop-blur-xl rounded-full flex items-center justify-center transition-all"
              >
                <XIcon className="size-5" />
              </button>
              <iframe
                src={`https://vidhive.lol/embed/movie/${playingId}?autoPlay=true&theme=CCFF00`}
                className="w-full h-full"
                frameBorder="0"
                allowFullScreen
                allow="autoplay; fullscreen; encrypted-media; picture-in-picture"
              ></iframe>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </main>
  );
}

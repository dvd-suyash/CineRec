"use client";

import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeftIcon, PlayIcon, XIcon } from "lucide-react";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { useState, useEffect } from "react";

export default function DashboardPage() {
  const { data: session } = useSession();
  const getToken = () => (session as any)?.accessToken as string | undefined;
  
  const [playingId, setPlayingId] = useState<number | null>(null);
  const [data, setData] = useState<any>(null);
  
  useEffect(() => {
    async function fetchData() {
      const token = getToken();
      if (!token) return;
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/dashboard/`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (res.ok) {
        const json = await res.json();
        setData(json.data);
      }
    }
    fetchData();
  }, []);
  
  return (
    <main className="min-h-screen bg-[#050505] text-white selection:bg-[#CCFF00] selection:text-black overflow-x-hidden">
      {/* Background ambient noise */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] mix-blend-overlay bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />
      
      {/* Navigation */}
      <header className="fixed top-0 inset-x-0 z-50 flex items-center justify-between px-4 md:px-8 py-4 md:py-6 backdrop-blur-md bg-transparent border-b border-white/5">
        <Link href="/" className="flex items-center gap-4 group">
          <div className="p-2 -ml-2 text-white/50 group-hover:text-white transition-colors rounded-full group-hover:bg-white/5">
            <ArrowLeftIcon className="size-5" />
          </div>
          <div className="text-2xl font-bold tracking-tighter text-white">CineRec.</div>
        </Link>
        <div className="text-sm font-medium text-white/50 tracking-widest uppercase">
          My Cinema
        </div>
      </header>

      <div className="pt-32 px-8 pb-32 max-w-[100rem] mx-auto w-full relative z-10">
        {/* HERO: The DNA */}
        <section className="mb-32">
          <div className="max-w-6xl">
            <h1 className="text-6xl md:text-8xl lg:text-9xl font-black tracking-tighter leading-[0.9] text-white mb-8">
              The shape of your <br className="hidden md:block"/>
              <span className="text-[#CCFF00] italic pr-4">cinematic mind.</span>
            </h1>
            <p className="text-xl md:text-2xl text-white/50 max-w-2xl font-light leading-relaxed">
              Arachne has observed your choices. You lean heavily into atmospheric dread, structured around non-linear narratives. You seek out the neon noir.
            </p>
          </div>
        </section>

        {/* BENTO GRID: DNA Visualization & Stats */}
        <section className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 grid-flow-dense mb-32">
          {/* Card 1: Vibe Map (Spans 2x2) */}
          <motion.div 
            whileHover={{ scale: 0.98 }}
            className="md:col-span-2 md:row-span-2 bg-white/5 border border-white/10 rounded-3xl p-6 md:p-12 flex flex-col justify-between aspect-square md:aspect-auto overflow-hidden relative group"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-[#CCFF00]/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
            <div className="relative z-10">
              <h2 className="text-4xl font-bold tracking-tight mb-2">Taste Signature</h2>
              <p className="text-white/50 text-sm">Derived from 42 interactions</p>
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
              <p className="text-white/60 text-base leading-relaxed italic">
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
              <div className="text-5xl md:text-7xl font-black tracking-tighter leading-none mb-2">{data?.watchlist?.length || 0}</div>
              <div className="text-sm font-bold uppercase tracking-widest opacity-70">Watchlist Size</div>
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
            <button className="text-white/50 hover:text-white uppercase tracking-widest text-xs font-bold transition-colors">
              View All
            </button>
          </div>
          
          <div className="flex gap-6 overflow-x-auto pb-12 snap-x snap-mandatory scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
            {(data?.watchlist || []).map((movie: any) => (
              <motion.div 
                key={movie.id}
                className="shrink-0 w-[280px] md:w-[320px] snap-center group cursor-pointer"
                whileHover={{ y: -10 }}
                onClick={() => setPlayingId(movie.id)}
              >
                <div className="w-full aspect-[2/3] rounded-2xl overflow-hidden relative mb-5 shadow-2xl border border-white/10 group-hover:border-white/30 transition-colors">
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity z-10 flex items-center justify-center backdrop-blur-sm">
                    <div className="size-16 rounded-full bg-[#CCFF00] flex items-center justify-center scale-75 group-hover:scale-100 transition-transform duration-500 ease-out">
                      <PlayIcon className="size-6 text-black fill-black ml-1" />
                    </div>
                  </div>
                  <img src={movie.poster} alt={movie.title} className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110" />
                </div>
                <h3 className="text-xl font-bold tracking-tight mb-1">{movie.title}</h3>
                <p className="text-white/50 text-sm font-medium">{movie.year}</p>
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

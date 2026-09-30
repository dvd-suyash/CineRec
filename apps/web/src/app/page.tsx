"use client";

import { useState, useRef, useEffect, useMemo } from "react";
import Link from "next/link";
import { useSession, signIn, signOut } from "next-auth/react";
import { Orb, OrbState } from "@/components/Orb";
import { InfiniteCanvas } from "@/components/InfiniteCanvas";
import ReactMarkdown from "react-markdown";
import { motion, AnimatePresence } from "framer-motion";
import { VisualRecommendations } from "@/components/VisualRecommendations";
import { LogOutIcon, ArrowRightIcon } from "lucide-react";

export default function Home() {
  const { data: session } = useSession();
  const [input, setInput] = useState("");
  const [chatHistory, setChatHistory] = useState<{ role: string; content: string }[]>([]);
  const [orbState, setOrbState] = useState<OrbState>("IDLE");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoreOpen, setIsLoreOpen] = useState(false);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [isHoveringEntity, setIsHoveringEntity] = useState(false);
  const [isMovieModalOpen, setIsMovieModalOpen] = useState(false);
  
  const [activeIndex, setActiveIndex] = useState(0);
  const lastScrollTime = useRef(0);

  // Group chat into Pairs [user, assistant]
  const chatPairs = useMemo(() => {
    const pairs = [];
    for (let i = 0; i < chatHistory.length; i++) {
      if (chatHistory[i].role === 'user') {
        pairs.push({
          user: chatHistory[i],
          assistant: (i + 1 < chatHistory.length && chatHistory[i + 1].role === 'assistant') ? chatHistory[i + 1] : null
        });
      }
    }
    return pairs;
  }, [chatHistory]);

  // Always snap to the latest message when it arrives
  useEffect(() => {
    if (chatPairs.length > 0) {
      setActiveIndex(chatPairs.length - 1);
    }
  }, [chatPairs.length]);

  const handleWheel = (e: React.WheelEvent) => {
    if (isLoreOpen) return;
    const now = Date.now();
    if (now - lastScrollTime.current < 800) return; // Debounce 800ms
    
    if (e.deltaY < -20 && activeIndex > 0) {
      setActiveIndex(prev => prev - 1);
      lastScrollTime.current = now;
    } else if (e.deltaY > 20 && activeIndex < chatPairs.length - 1) {
      setActiveIndex(prev => prev + 1);
      lastScrollTime.current = now;
    }
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  const getToken = () => (session as any)?.accessToken as string | undefined;

  const startSession = async () => {
    const token = getToken();
    if (!token) {
      console.error("No access token available");
      return null;
    }
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/chat/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` }
      });
      if (!res.ok) {
        console.error("Session creation failed:", res.status, await res.text());
        return null;
      }
      const json = await res.json();
      // Backend returns DataResponse: { data: { session_id: "..." } }
      const newSessionId = json.data?.session_id || json.session_id || json.id;
      console.log("Created session:", newSessionId);
      setSessionId(newSessionId);
      return newSessionId;
    } catch (error) {
      console.error("Failed to start session:", error);
      return null;
    }
  };

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || !session) return;
    
    const userMessage = input.trim();
    setInput("");
    setChatHistory(prev => [...prev, { role: "user", content: userMessage }]);
    setOrbState("PROCESSING");

    let currentSessionId = sessionId;
    if (!currentSessionId) {
      currentSessionId = await startSession();
      if (!currentSessionId) {
        setOrbState("ERROR");
        return;
      }
    }

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/chat/sessions/${currentSessionId}/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${getToken()}` },
        body: JSON.stringify({ message: userMessage })
      });

      if (!res.ok) throw new Error("Failed to send message");

      const reader = res.body?.getReader();
      const decoder = new TextDecoder("utf-8");

      if (reader) {
        setChatHistory(prev => [...prev, { role: "assistant", content: "" }]);
        let done = false;
        let buffer = "";
        
        while (!done) {
          const { value, done: readerDone } = await reader.read();
          done = readerDone;
          if (value) {
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n\n");
            
            // Keep the last chunk in the buffer if it doesn't end with \n\n
            buffer = lines.pop() || "";
            
            for (const line of lines) {
              if (line.startsWith("data: ")) {
                try {
                  const data = JSON.parse(line.slice(6));
                  if (data.type === "text_delta") {
                    setChatHistory(prev => {
                      const newHistory = [...prev];
                      const lastIdx = newHistory.length - 1;
                      newHistory[lastIdx] = { 
                        ...newHistory[lastIdx], 
                        content: newHistory[lastIdx].content + data.content 
                      };
                      return newHistory;
                    });
                  } else if (data.type === "ui_movies") {
                    setChatHistory(prev => {
                      const newHistory = [...prev];
                      const lastIdx = newHistory.length - 1;
                      newHistory[lastIdx] = { 
                        ...newHistory[lastIdx], 
                        content: newHistory[lastIdx].content + "\n\n" + JSON.stringify(data)
                      };
                      return newHistory;
                    });
                  } else if (data.type === "done") {
                    setOrbState("RECOMMENDING");
                    setTimeout(() => setOrbState("IDLE"), 2000);
                  }
                } catch {
                  // Ignore incomplete JSON chunks
                }
              }
            }
          }
        }
      }
    } catch (error) {
      console.error(error);
      setOrbState("ERROR");
    } finally {
      setOrbState(current => current === "PROCESSING" ? "IDLE" : current);
    }
  };

  return (
    <main className="relative min-h-screen w-full max-w-full overflow-x-hidden flex flex-col">
      <div className="ambient-bg" />

      {/* THE DAUNTING VOID WITH INFINITE CANVAS */}
      <div className={`fixed inset-0 z-0 bg-black transition-opacity duration-1000 ${chatHistory.length > 0 ? 'opacity-60' : 'opacity-100'}`}>
        <InfiniteCanvas isProcessing={orbState === "PROCESSING"} />
        <div className="absolute inset-0 opacity-[0.15] mix-blend-screen pointer-events-none bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDAiIGhlaWdodD0iNDAwIj48ZmlsdGVyIGlkPSJuIj48ZmVUdXJidWxlbmNlIHR5cGU9ImZyYWN0YWxOb2lzZSIgYmFzZUZyZXF1ZW5jeT0iMC44IiBudW1PY3RhdmVzPSIzIiBzdGl0Y2hUaWxlcz0ic3RpdGNoIi8+PC9maWx0ZXI+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsdGVyPSJ1cmwoI24pIi8+PC9zdmc+')] animate-[grain_8s_steps(10)_infinite]" />
        
        {/* Cinematic Vignette & Edge Masking */}
        <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(to_right,#000_0%,transparent_15%,transparent_85%,#000_100%)]" />
        <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_center,transparent_30%,rgba(0,0,0,0.6)_80%,#000_100%)]" />
      </div>

      {/* LEVITATING BRUTALIST TYPOGRAPHY */}
      <motion.div 

        initial={false}
        animate={{ 
          y: chatHistory.length > 0 ? "-8vh" : "0vh",
          scale: chatHistory.length > 0 ? 0.9 : 1
        }}
        transition={{ type: "spring", stiffness: 200, damping: 30 }}
        className="fixed inset-0 z-[5] flex items-center justify-center pointer-events-none select-none pb-[42vh]"
      >
        <motion.div 
          initial={{ y: 20, rotate: -2, skewX: -5 }}
          animate={{ y: [0, -10, 0], rotate: [-2, -3, -2] }}
          transition={{ 
            y: { repeat: Infinity, duration: 6, ease: "easeInOut" },
            rotate: { repeat: Infinity, duration: 8, ease: "easeInOut" }
          }}
          className="relative group pointer-events-auto cursor-pointer"
          onClick={() => setIsLoreOpen(true)}
          onMouseEnter={() => setIsHoveringEntity(true)}
          onMouseLeave={() => setIsHoveringEntity(false)}
        >
          <div 
            className="text-7xl md:text-[8rem] font-black tracking-tighter text-[#CCFF00] uppercase leading-none opacity-100 transition-transform duration-500 group-hover:scale-105"
            style={{ textShadow: "5px 5px 0px #FF00FF, 10px 10px 0px #000000" }}
          >
            ARACHNE
          </div>
        </motion.div>
      </motion.div>

      {/* MASSIVE CENTRIC BEING */}
      <motion.div 

        initial={false}
        animate={{ 
          y: chatHistory.length > 0 ? "-8vh" : "0vh",
          scale: chatHistory.length > 0 ? 0.9 : 1
        }}
        transition={{ type: "spring", stiffness: 200, damping: 30 }}
        className="fixed inset-0 z-10 flex items-center justify-center pointer-events-none overflow-visible pt-32"
      >
        <div className="transform scale-[2] md:scale-[2.2] translate-y-12 relative pointer-events-none">
          <Orb state={orbState} />
          
          {/* INVISIBLE PRECISION HITBOX */}
          <div 
            className="absolute left-1/2 top-[45%] -translate-x-1/2 -translate-y-1/2 w-[35%] h-[65%] pointer-events-auto cursor-pointer group"
            onClick={() => setIsLoreOpen(true)}
            onMouseEnter={() => setIsHoveringEntity(true)}
            onMouseLeave={() => setIsHoveringEntity(false)}
          >
          </div>
        </div>
      </motion.div>

      
      {/* FLOATING CURSOR PILL */}
      <motion.div
        className="fixed top-0 left-0 z-[999] pointer-events-none"
        animate={{
          x: mousePos.x,
          y: mousePos.y,
          opacity: isHoveringEntity ? 1 : 0,
          scale: isHoveringEntity ? 1 : 0.8,
        }}
        transition={{ type: "spring", stiffness: 500, damping: 28, mass: 0.5 }}
      >
        <div className="absolute -left-1/2 mt-6 px-5 py-2 rounded-full bg-[#CCFF00] text-black text-[10px] font-black tracking-widest uppercase shadow-[0_0_30px_rgba(204,255,0,0.4)] whitespace-nowrap">
          Identify Entity
        </div>
      </motion.div>
      
      {/* Top Navigation - Minimalist & Glassmorphic */}
      <header className="fixed top-0 inset-x-0 z-50 flex items-center justify-between px-8 py-6 backdrop-blur-md bg-background/50 border-b border-white/5">
        <div className="text-2xl font-bold tracking-tighter text-white">CineRec.</div>
        <nav className="flex items-center gap-6">
          {session ? (
            <div className="flex items-center gap-6">
              <Link 
                href="/dashboard"
                className="text-sm font-bold uppercase tracking-widest text-[#CCFF00] hover:text-white transition-colors"
              >
                My Cinema
              </Link>
              <span className="text-sm font-medium text-white/70 hidden sm:inline-block border-l border-white/20 pl-6">
                {session.user?.name}
              </span>
              <button 
                onClick={() => signOut()}
                className="flex items-center gap-2 text-sm font-medium text-white/70 hover:text-white transition-colors"
              >
                <LogOutIcon className="size-4" />
                Sign Out
              </button>
            </div>
          ) : (
            <button 
              onClick={() => signIn("google")}
              className="px-6 py-2 rounded-full bg-white text-black text-sm font-bold hover:scale-105 transition-transform"
            >
              Sign In
            </button>
          )}
        </nav>
      </header>

      {/* Main Content Area - Snapshot Pagination */}
      <div 
        className={`fixed inset-0 flex flex-col items-center justify-center pointer-events-none ${isMovieModalOpen ? 'z-[60]' : 'z-20'}`}
        onWheel={handleWheel}
      >
        <AnimatePresence mode="wait">
          {chatPairs.length > 0 && chatPairs[activeIndex] && (
            <motion.div
              key={activeIndex}
              initial={{ opacity: 0, scale: 0.95, filter: "blur(10px)" }}
              animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
              exit={{ opacity: 0, scale: 1.05, filter: "blur(10px)" }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
              className="w-full max-w-7xl flex flex-col items-center gap-4 pointer-events-auto absolute"
            >
              {/* User Prompt */}
              <div className="w-full text-center px-4 mt-8 md:mt-16">
                <div className="inline-block max-w-3xl text-xl md:text-2xl font-light tracking-wide text-white/60 italic line-clamp-2 overflow-hidden drop-shadow-xl">
                  &quot;{chatPairs[activeIndex].user.content}&quot;
                </div>
              </div>

              {/* Assistant Response */}
              {chatPairs[activeIndex].assistant && (
                <div className="w-full relative">
                  {(() => {
                    const msg = chatPairs[activeIndex].assistant;
                    let textContent = msg.content;
                    let uiMoviesData = null;

                    // 1. If the whole thing is valid JSON
                    try {
                      const parsed = JSON.parse(textContent);
                      if (parsed.type === "ui_movies") {
                        uiMoviesData = parsed;
                        textContent = "";
                      }
                    } catch {
                      // 2. Otherwise, look for the JSON payload appended at the end
                      const jsonMatch = textContent.match(/\{"type":\s*"ui_movies"[\s\S]*\}$/);
                      if (jsonMatch) {
                        try {
                          uiMoviesData = JSON.parse(jsonMatch[0]);
                          textContent = textContent.replace(jsonMatch[0], "").trim();
                        } catch {}
                      }
                    }
                    
                    return (
                      <div className="flex flex-col items-center w-full px-4 mt-8 gap-8">
                        {!uiMoviesData && textContent && (
                          <div className="max-w-2xl w-full backdrop-blur-xl bg-black/40 border border-white/10 p-6 md:p-8 rounded-3xl shadow-2xl text-center max-h-[35vh] overflow-y-auto scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
                            <div className="prose prose-lg prose-invert max-w-none text-white/80 marker:text-white/40">
                              <ReactMarkdown>{textContent}</ReactMarkdown>
                            </div>
                          </div>
                        )}
                        {uiMoviesData && (
                          <div className="w-full">
                            <VisualRecommendations vibeTitle={uiMoviesData.vibe_title} movies={uiMoviesData.movies} onModalChange={setIsMovieModalOpen} />
                          </div>
                        )}
                      </div>
                    );
                  })()}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Premium Cinematic Input Bar */}
      <motion.form 
        layout
        onSubmit={handleSend}
        className="w-full max-w-3xl fixed bottom-12 left-1/2 -translate-x-1/2 z-50 px-6 group pointer-events-auto"
      >
        <div className="relative flex items-center bg-zinc-950/60 backdrop-blur-2xl border border-white/10 hover:border-white/20 focus-within:border-[#CCFF00]/50 focus-within:bg-zinc-950/90 rounded-full shadow-[0_0_50px_rgba(0,0,0,0.5)] transition-all duration-500 overflow-hidden pl-8 pr-2 py-2">
          <input 
            type="text" 
            placeholder={session ? "Ask Arachne of your binge troubles..." : "Sign in to begin..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!session || orbState === "PROCESSING"}
            onFocus={() => setOrbState("INPUT")}
            onBlur={() => setOrbState(chatHistory.length > 0 ? "FOLLOW-UP" : "IDLE")}
            className="flex-1 bg-transparent text-white/90 focus:text-white placeholder:text-white/30 text-lg md:text-xl font-medium tracking-wide outline-none disabled:opacity-50 h-12"
          />
          <button
            type="submit"
            disabled={!session || !input.trim() || orbState === "PROCESSING"}
            className="size-12 rounded-full bg-[#CCFF00] hover:bg-white text-black flex items-center justify-center transition-all duration-300 disabled:opacity-50 disabled:bg-white/10 disabled:text-white/30 disabled:shadow-none shadow-[0_0_20px_rgba(204,255,0,0.3)] ml-4 shrink-0"
          >
            <ArrowRightIcon className="size-5" />
          </button>
        </div>
      </motion.form>

      {/* LORE MODAL */}
      <AnimatePresence>
        {isLoreOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md"
            onClick={() => setIsLoreOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.95, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 20 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              onClick={(e) => e.stopPropagation()}
              className="max-w-2xl w-full bg-[#111] border border-white/10 rounded-2xl p-10 md:p-16 shadow-2xl relative overflow-hidden"
            >
              {/* Decorative Element */}
              <div className="absolute -top-32 -right-32 w-96 h-96 bg-[#CCFF00]/10 rounded-full blur-[100px] pointer-events-none" />
              
              <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight mb-8 uppercase">
                The Weaver
              </h2>
              
              <div className="space-y-4 text-white/70 text-base md:text-lg font-light leading-relaxed max-h-[55vh] overflow-y-auto pr-4 scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
                <p>Long ago, Arachne was mortal.</p>
                <p>Her hands could weave threads into stories so perfect that even the gods envied them. She dared to challenge Athena herself — and won.</p>
                <p>The gods did not forgive her.</p>
                <p>They cursed Arachne to weave for eternity, stripping away the life she once knew and leaving her to the shadows.</p>
                <p>And there she remained.</p>
                <p className="font-bold text-[#CCFF00]">Forgotten.</p>
                <p>Until now.</p>
                <p>CineRec found the thread that time had buried.</p>
                <p>We followed it through forgotten stories, lost memories, and the endless archive of human cinema.</p>
                <p>And somewhere within it, we found her.</p>
                <p className="font-bold text-[#CCFF00]">We brought Arachne back.</p>
                <p>She has returned to her loom after centuries of silence.</p>
                <p>But the world has changed.</p>
                <p>She no longer weaves silk.</p>
                <p className="font-bold text-[#CCFF00]">She weaves stories.</p>
                <p>Tell her what you seek — a feeling, a memory, a mood, a night you cannot quite put into words — and she will search the endless tapestry of cinema for the thread that leads to it.</p>
                <p>Perhaps she will find something you never knew you were looking for.</p>
                <p>Perhaps she will remember something you had forgotten.</p>
                <p>And perhaps you will wonder:</p>
                <p className="font-bold text-[#CCFF00]">How did CineRec bring Arachne back?</p>
                <p>That is a story even the Weaver refuses to tell.</p>
                <p className="text-xl md:text-2xl font-bold text-[#CCFF00] pt-4 tracking-wide uppercase">THE WEAVER HAS AWAKENED.</p>
              </div>

              <button 
                onClick={() => setIsLoreOpen(false)}
                className="mt-10 px-8 py-4 rounded-full bg-white text-black font-bold text-sm tracking-widest uppercase hover:bg-[#CCFF00] hover:scale-105 transition-all w-full md:w-auto"
              >
                ENTER THE WEAVE
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Right Side Pagination Timeline */}
      <div className="fixed right-6 top-1/2 -translate-y-1/2 z-[60] flex flex-col gap-3 items-end pointer-events-auto">
        {chatPairs.length === 0 && (
           <div className="w-5 h-[2px] bg-white/20 rounded-full" />
        )}
        {chatPairs.map((pair, idx) => (
          <div key={idx} className="relative group/line flex items-center justify-end">
            {/* Tooltip on hover (pops out to the LEFT of the line) */}
            <div className="absolute right-10 px-3 py-1.5 bg-zinc-900 border border-white/10 rounded-lg text-[10px] uppercase font-bold tracking-widest text-white opacity-0 group-hover/line:opacity-100 pointer-events-none transition-opacity whitespace-nowrap shadow-2xl">
              {pair.user.content.length > 30 ? pair.user.content.slice(0, 30) + "..." : pair.user.content}
            </div>
            
            {/* The line */}
            <button 
              onClick={() => setActiveIndex(idx)}
              className={`h-[2px] rounded-full transition-all duration-300 ${activeIndex === idx ? 'w-8 bg-[#CCFF00] shadow-[0_0_10px_rgba(204,255,0,0.5)]' : 'w-4 bg-white/40 hover:bg-white hover:w-6'}`}
            />
          </div>
        ))}
      </div>

    </main>
  );
}

import React, { useState, useEffect } from 'react';
import { ShieldCheck, ArrowRight, Zap, CheckCircle2, DollarSign, Activity } from 'lucide-react';

export default function ProductHero({ onLaunchTerminal }) {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const translateY = scrollY * 0.12;

  return (
    <section className="relative w-full overflow-hidden bg-[#0a0806] pt-8 pb-24 border-b border-[#292524]/60">
      {/* Ambient Lighting Glow */}
      <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-[#E5A93C]/10 rounded-full blur-[160px] pointer-events-none" />
      <div className="absolute top-1/4 left-1/5 w-[500px] h-[500px] bg-[#0C65FF]/5 rounded-full blur-[140px] pointer-events-none" />

      {/* Top Navigation */}
      <nav className="relative z-20 flex items-center justify-between px-6 pb-12 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded bg-[#E5A93C]/10 border border-[#E5A93C]/30">
            <ShieldCheck className="h-5 w-5 text-[#E5A93C]" />
          </div>
          <div>
            <span className="font-extrabold tracking-tight text-white text-base tracking-wide">
              SHIELDEX
            </span>
            <span className="text-[10px] text-[#A8A29E] font-medium block uppercase tracking-wider">
              Autonomous Payment Risk Engine
            </span>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs text-[#FAFAF9]">
          <a href="#architecture" className="text-[#A8A29E] hover:text-white transition-colors">
            Architecture
          </a>
          <a href="#benchmarks" className="text-[#A8A29E] hover:text-white transition-colors">
            Cost & Benchmarks
          </a>
          <a href="#terminal-console" className="text-[#A8A29E] hover:text-white transition-colors">
            Live Terminal
          </a>
          <button
            onClick={onLaunchTerminal}
            className="rzp-button py-2 px-4 text-xs font-bold"
          >
            Launch Console
          </button>
        </div>
      </nav>

      {/* Hero Content: 2-Column Layout */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        {/* Left: Typography & Actions */}
        <div className="lg:col-span-7 space-y-6 text-left">
          <div className="inline-flex items-center gap-2 rzp-badge rzp-badge-gold">
            <span className="h-1.5 w-1.5 rounded-full bg-[#E5A93C] animate-pulse"></span>
            <span>SUB-15MS DEFENSE • 56,962 HELD-OUT TESTS • 0.8610 PR-AUC</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-[#FAFAF9] leading-[1.12]">
            Real-time AI risk defense for <br className="hidden sm:inline" />
            <span className="text-[#E5A93C]">high-velocity payment gateways.</span>
          </h1>

          <p className="text-sm sm:text-base text-[#A8A29E] max-w-xl leading-relaxed">
            A three-tier defense architecture uniting soft-voting gradient boosting (LightGBM + XGBoost), EWMA merchant rate anomaly tracking, and autonomous LangGraph dispute evidence drafters.
          </p>

          {/* Buttons */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3.5 pt-2">
            <button
              onClick={onLaunchTerminal}
              className="rzp-button px-6 py-3 text-xs font-bold flex items-center justify-center gap-2"
            >
              Open Live Operations Console <ArrowRight className="h-4 w-4" />
            </button>
            <a
              href="#architecture"
              className="rzp-button-secondary px-5 py-3 text-xs text-center font-semibold"
            >
              Explore 3-Tier Architecture
            </a>
          </div>

          {/* Key Metric Pills */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-6 border-t border-[#292524]">
            <div>
              <div className="text-[10px] text-[#78716C] uppercase font-semibold">Tested PR-AUC</div>
              <div className="mono text-lg font-bold text-[#FAFAF9] mt-0.5">0.8610</div>
              <div className="text-[10px] text-[#10B981] font-medium">+15.1% vs Baseline</div>
            </div>
            <div>
              <div className="text-[10px] text-[#78716C] uppercase font-semibold">₹ Loss Saved</div>
              <div className="mono text-lg font-bold text-[#10B981] mt-0.5">₹398,500</div>
              <div className="text-[10px] text-[#A8A29E]">on test set</div>
            </div>
            <div>
              <div className="text-[10px] text-[#78716C] uppercase font-semibold">Spike Latency</div>
              <div className="mono text-lg font-bold text-[#E5A93C] mt-0.5">1.0 Txn</div>
              <div className="text-[10px] text-[#10B981] font-medium">100% Rate Capture</div>
            </div>
            <div>
              <div className="text-[10px] text-[#78716C] uppercase font-semibold">P99 Latency</div>
              <div className="mono text-lg font-bold text-[#60a5fa] mt-0.5">&lt; 15 ms</div>
              <div className="text-[10px] text-[#A8A29E]">Ultra-Low Latency</div>
            </div>
          </div>
        </div>

        {/* Right: Stationary / Gentle Floating 3D Core */}
        <div className="lg:col-span-5 flex flex-col items-center justify-center relative select-none">
          <div
            className="relative transition-transform duration-100 ease-out will-change-transform"
            style={{
              transform: `translateY(${translateY}px)`,
            }}
          >
            <div className="animate-float-gentle">
              <div className="w-80 sm:w-[420px] drop-shadow-[0_35px_60px_rgba(229,169,60,0.2)]">
                <img
                  src="/assets/hero_gateway_core.png"
                  alt="Shieldex 3D Quantum Gateway Core"
                  className="w-full h-auto select-none pointer-events-none"
                />
              </div>
            </div>
          </div>
          <div className="mono text-[10px] text-[#78716C] mt-4 flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-[#E5A93C]"></span>
            <span>SHIELDEX QUANTUM DEFENSE CORE</span>
          </div>
        </div>
      </div>
    </section>
  );
}

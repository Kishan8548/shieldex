import React, { useState, useEffect } from 'react';
import { ShieldCheck, ArrowRight, Zap, CheckCircle2, DollarSign, Activity } from 'lucide-react';
import QuantumCore3D from './QuantumCore3D';

export default function ProductHero({ onLaunchTerminal }) {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const translateY = scrollY * 0.1;

  return (
    <section className="relative w-full min-h-screen h-screen flex flex-col justify-between overflow-hidden bg-[#0a0806] px-6 py-6 border-b border-[#292524]/60">
      {/* Ambient Lighting Glow */}
      <div className="absolute top-1/3 right-1/4 w-[650px] h-[650px] bg-[#E5A93C]/10 rounded-full blur-[180px] pointer-events-none" />
      <div className="absolute top-1/4 left-1/5 w-[500px] h-[500px] bg-[#0C65FF]/5 rounded-full blur-[160px] pointer-events-none" />

      {/* Top Navigation */}
      <nav className="relative z-20 flex items-center justify-between max-w-7xl mx-auto w-full">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#14110e] border border-[#E5A93C]/30 p-1.5 shadow-sm">
            <img src="/favicon.svg" alt="Shieldex Logo" className="h-full w-full object-contain" />
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

      {/* Center Body: 2-Column High-Trust Layout */}
      <div className="relative z-10 max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-center my-auto">
        {/* Left: Typography & Actions */}
        <div className="lg:col-span-7 space-y-6 text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#14110e] border border-[#E5A93C]/30 text-[11px] font-mono text-[#E5A93C]">
            <span className="h-1.5 w-1.5 rounded-full bg-[#E5A93C] animate-pulse"></span>
            <span>Sub-15ms Inference • 0.8610 PR-AUC • 56,962 Tests</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-[#FAFAF9] leading-[1.1]">
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
        </div>

        {/* Right: Live Interactive WebGL 3D Quantum Core */}
        <div className="lg:col-span-5 flex flex-col items-center justify-center relative">
          <div
            className="w-full transition-transform duration-100 ease-out will-change-transform"
            style={{
              transform: `translateY(${translateY}px)`,
            }}
          >
            <QuantumCore3D />
          </div>
          <div className="mono text-[10px] text-[#78716C] flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-[#E5A93C] animate-pulse"></span>
            <span>INTERACTIVE WEBGL 3D • DRAG TO ROTATE</span>
          </div>
        </div>
      </div>

      {/* Bottom: Key Metric Pills */}
      <div className="relative z-10 max-w-7xl mx-auto w-full pt-4 border-t border-[#292524]">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
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
    </section>
  );
}

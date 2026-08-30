import React, { useState, useEffect, useRef } from 'react';
import { ShieldCheck, Cpu, Radio, BrainCircuit, ArrowRight } from 'lucide-react';

export default function ProductArchitectureSection() {
  const [scrollY, setScrollY] = useState(0);
  const secRef1 = useRef(null);
  const secRef2 = useRef(null);
  const secRef3 = useRef(null);

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const getOffset = (ref) => {
    if (!ref.current) return 0;
    const rect = ref.current.getBoundingClientRect();
    const centerOffset = rect.top + rect.height / 2 - window.innerHeight / 2;
    return centerOffset * -0.14;
  };

  return (
    <section id="architecture" className="py-24 px-6 max-w-7xl mx-auto bg-[#0a0806] space-y-28">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-[#292524] pb-8">
        <div>
          <div className="mono text-[10px] text-[#E5A93C] tracking-widest uppercase font-bold mb-2">
            THREE-TIER DEFENSE ARCHITECTURE
          </div>
          <h2 className="text-3xl sm:text-5xl font-bold tracking-tight text-[#FAFAF9]">
            Three layers of <span className="text-[#E5A93C]">autonomous defense.</span>
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-[#A8A29E] max-w-md leading-relaxed">
          From sub-15ms tabular gradient boosting to real-time process control and regulatory policy agents.
        </p>
      </div>

      {/* Layer 1 (ZIG): 3D Shield on LEFT ➔ Content on RIGHT */}
      <div
        ref={secRef1}
        className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center"
      >
        {/* 3D Element 1 on LEFT */}
        <div className="lg:col-span-5 order-2 lg:order-1 flex flex-col items-center justify-center">
          <div
            className="w-64 sm:w-80 relative transition-transform duration-100 ease-out will-change-transform drop-shadow-[0_25px_35px_rgba(229,169,60,0.15)]"
            style={{
              transform: `translateY(${getOffset(secRef1)}px) rotate(${getOffset(secRef1) * -0.05}deg)`,
            }}
          >
            <img
              src="/assets/floating_shield_3d.png"
              alt="Shieldex 3D Defense Shield"
              className="w-full h-auto select-none pointer-events-none"
            />
          </div>
          <div className="mono text-[11px] text-[#78716C] mt-4">
            Layer 1: Cryptographic Risk Shield
          </div>
        </div>

        {/* Content on RIGHT */}
        <div className="lg:col-span-7 order-1 lg:order-2 space-y-5">
          <div className="inline-flex items-center gap-2 rzp-badge rzp-badge-gold">
            <span>LAYER 01 • CLASSIFICATION & SHAP</span>
          </div>
          <h3 className="text-2xl sm:text-3xl font-bold text-[#FAFAF9]">
            Sub-15ms Soft-Voting Ensemble
          </h3>
          <p className="text-sm text-[#A8A29E] leading-relaxed">
            Combines LightGBM and XGBoost gradient-boosted decision trees trained on 36 features with scale_pos_weight for extreme 0.17% class imbalance. TreeExplainer SHAP attribution provides instant real-time auditability for each score.
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2 text-xs">
            <div className="p-3 bg-[#14110e] rounded-lg border border-[#292524]">
              <div className="text-[10px] text-[#78716C]">PR-AUC Score</div>
              <div className="mono text-base font-bold text-[#10B981]">0.8610</div>
            </div>
            <div className="p-3 bg-[#14110e] rounded-lg border border-[#292524]">
              <div className="text-[10px] text-[#78716C]">Inference Speed</div>
              <div className="mono text-base font-bold text-[#FAFAF9]">12.4 ms</div>
            </div>
            <div className="p-3 bg-[#14110e] rounded-lg border border-[#292524]">
              <div className="text-[10px] text-[#78716C]">Explainability</div>
              <div className="mono text-base font-bold text-[#E5A93C]">TreeSHAP</div>
            </div>
          </div>
          <div className="pt-2">
            <a
              href="#terminal-console"
              className="text-xs font-bold text-[#E5A93C] hover:text-[#f59e0b] flex items-center gap-1"
            >
              Test in Transaction Simulator →
            </a>
          </div>
        </div>
      </div>

      {/* Layer 2 (ZAG): Content on LEFT ➔ 3D Neural Matrix on RIGHT */}
      <div
        ref={secRef2}
        className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center pt-8 border-t border-[#292524]/60"
      >
        {/* Content on LEFT */}
        <div className="lg:col-span-7 space-y-5">
          <div className="inline-flex items-center gap-2 rzp-badge rzp-badge-gold">
            <span>LAYER 02 • STATISTICAL PROCESS CONTROL</span>
          </div>
          <h3 className="text-2xl sm:text-3xl font-bold text-[#FAFAF9]">
            EWMA Dynamic Velocity Radar
          </h3>
          <p className="text-sm text-[#A8A29E] leading-relaxed">
            Maintains an exponentially weighted moving average (α=0.15) of fraud probability per merchant. Fires immediate critical alerts when the rolling Z-Score ≥ 3.0σ without waiting for bank chargeback feedback.
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2 text-xs">
            <div className="p-3 bg-[#14110e] rounded-lg border border-[#292524]">
              <div className="text-[10px] text-[#78716C]">Burst Detection</div>
              <div className="mono text-base font-bold text-[#10B981]">100% Rate</div>
            </div>
            <div className="p-3 bg-[#14110e] rounded-lg border border-[#292524]">
              <div className="text-[10px] text-[#78716C]">Detection Latency</div>
              <div className="mono text-base font-bold text-[#FAFAF9]">1.0 Txn</div>
            </div>
            <div className="p-3 bg-[#14110e] rounded-lg border border-[#292524]">
              <div className="text-[10px] text-[#78716C]">False Alarm Rate</div>
              <div className="mono text-base font-bold text-[#10B981]">0.0%</div>
            </div>
          </div>
          <div className="pt-2">
            <a
              href="#terminal-console"
              className="text-xs font-bold text-[#E5A93C] hover:text-[#f59e0b] flex items-center gap-1"
            >
              Monitor Live Spike Radar Stream →
            </a>
          </div>
        </div>

        {/* 3D Element 2 on RIGHT */}
        <div className="lg:col-span-5 flex flex-col items-center justify-center">
          <div
            className="w-64 sm:w-80 relative transition-transform duration-100 ease-out will-change-transform drop-shadow-[0_25px_35px_rgba(0,0,0,0.9)]"
            style={{
              transform: `translateY(${getOffset(secRef2)}px) rotate(${getOffset(secRef2) * 0.05}deg)`,
            }}
          >
            <img
              src="/assets/floating_neural_matrix.png"
              alt="3D Neural Decision Matrix"
              className="w-full h-auto select-none pointer-events-none"
            />
          </div>
          <div className="mono text-[11px] text-[#78716C] mt-4">
            Layer 2: Neural Decision Matrix
          </div>
        </div>
      </div>

      {/* Layer 3 (ZIG): 3D Biometric Key on LEFT ➔ Content on RIGHT */}
      <div
        ref={secRef3}
        className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center pt-8 border-t border-[#292524]/60"
      >
        {/* 3D Element 3 on LEFT */}
        <div className="lg:col-span-5 order-2 lg:order-1 flex flex-col items-center justify-center">
          <div
            className="w-64 sm:w-80 relative transition-transform duration-100 ease-out will-change-transform drop-shadow-[0_25px_35px_rgba(0,0,0,0.9)]"
            style={{
              transform: `translateY(${getOffset(secRef3)}px) rotate(${getOffset(secRef3) * -0.05}deg)`,
            }}
          >
            <img
              src="/assets/floating_biometric_card.png"
              alt="3D Biometric Card & Key"
              className="w-full h-auto select-none pointer-events-none"
            />
          </div>
          <div className="mono text-[11px] text-[#78716C] mt-4">
            Layer 3: Biometric & Dispute Key
          </div>
        </div>

        {/* Content on RIGHT */}
        <div className="lg:col-span-7 order-1 lg:order-2 space-y-5">
          <div className="inline-flex items-center gap-2 rzp-badge rzp-badge-gold">
            <span>LAYER 03 • REGULATORY RAG & DISPUTES</span>
          </div>
          <h3 className="text-2xl sm:text-3xl font-bold text-[#FAFAF9]">
            Autonomous LangGraph RAG Agent
          </h3>
          <p className="text-sm text-[#A8A29E] leading-relaxed">
            Invokes a 4-node LangGraph state machine backed by an in-memory RAG knowledge base of RBI Additional Factor of Authentication (AFA) mandates and Visa 10.4 / Mastercard 4837 dispute codes to draft chargeback defense packets.
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2 text-xs">
            <div className="p-3 bg-[#14110e] rounded-lg border border-[#292524]">
              <div className="text-[10px] text-[#78716C]">LLM Support</div>
              <div className="mono text-base font-bold text-[#FAFAF9]">Groq / Gemini</div>
            </div>
            <div className="p-3 bg-[#14110e] rounded-lg border border-[#292524]">
              <div className="text-[10px] text-[#78716C]">Policy Retrieval</div>
              <div className="mono text-base font-bold text-[#E5A93C]">RBI / Visa / MC</div>
            </div>
            <div className="p-3 bg-[#14110e] rounded-lg border border-[#292524]">
              <div className="text-[10px] text-[#78716C]">Dossier Output</div>
              <div className="mono text-base font-bold text-[#10B981]">Instant Draft</div>
            </div>
          </div>
          <div className="pt-2">
            <a
              href="#terminal-console"
              className="text-xs font-bold text-[#E5A93C] hover:text-[#f59e0b] flex items-center gap-1"
            >
              Open Autonomous Dispute Copilot →
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

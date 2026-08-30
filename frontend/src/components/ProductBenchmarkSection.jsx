import React from 'react';
import { DollarSign, TrendingUp, ShieldCheck, ArrowRight } from 'lucide-react';

export default function ProductBenchmarkSection({ onOpenCostOptimizer }) {
  return (
    <section id="benchmarks" className="py-24 px-6 max-w-7xl mx-auto bg-[#0a0806] border-t border-[#292524]">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-14 gap-4 border-b border-[#292524] pb-6">
        <div>
          <div className="mono text-[10px] text-[#E5A93C] tracking-widest uppercase font-bold mb-2">
            MEASURED MONETARY IMPACT
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-[#FAFAF9]">
            Honest metrics, <span className="text-[#E5A93C]">real rupee savings.</span>
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-[#A8A29E] max-w-md leading-relaxed">
          Evaluated against 56,962 held-out transactions with asymmetrical 33.3:1 false-negative to false-positive cost weighting.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Cost Optimization */}
        <div className="rzp-card p-6 space-y-4 bg-[#14110e] border-[#292524]">
          <div className="flex items-center justify-between">
            <span className="mono text-xs font-bold text-[#E5A93C]">33.3:1 RATIO</span>
            <DollarSign className="h-5 w-5 text-[#E5A93C]" />
          </div>
          <h3 className="text-base font-bold text-[#FAFAF9]">
            ₹ Cost-Aware Thresholding
          </h3>
          <p className="text-xs text-[#A8A29E] leading-relaxed">
            Standard classifiers default to a <code>0.5</code> probability cutoff. Shieldex dynamically sweeps the precision-recall frontier to pinpoint the exact operating threshold (<code>0.3596</code>) that minimizes net expected chargeback losses.
          </p>
          <div className="pt-2">
            <button
              onClick={onOpenCostOptimizer}
              className="text-xs font-bold text-[#E5A93C] hover:text-[#f59e0b] flex items-center gap-1"
            >
              Launch Threshold Simulator <ArrowRight className="h-3 w-3" />
            </button>
          </div>
        </div>

        {/* Card 2: PR-AUC Superiority */}
        <div className="rzp-card p-6 space-y-4 bg-[#14110e] border-[#292524]">
          <div className="flex items-center justify-between">
            <span className="mono text-xs font-bold text-[#10B981]">0.8610 PR-AUC</span>
            <TrendingUp className="h-5 w-5 text-[#10B981]" />
          </div>
          <h3 className="text-base font-bold text-[#FAFAF9]">
            Precision Over Accuracy
          </h3>
          <p className="text-xs text-[#A8A29E] leading-relaxed">
            With 99.83% legitimate transactions, raw accuracy is misleading. Shieldex achieves 88.89% precision and 81.63% recall on the frozen test partition without synthetic data leakage in evaluation.
          </p>
          <div className="text-xs text-[#78716C] mono pt-2">
            ROC-AUC: 0.9841 • F1: 0.8511
          </div>
        </div>

        {/* Card 3: Instantaneous Spike Latency */}
        <div className="rzp-card p-6 space-y-4 bg-[#14110e] border-[#292524]">
          <div className="flex items-center justify-between">
            <span className="mono text-xs font-bold text-[#60a5fa]">1.0 TXN LATENCY</span>
            <ShieldCheck className="h-5 w-5 text-[#60a5fa]" />
          </div>
          <h3 className="text-base font-bold text-[#FAFAF9]">
            Velocity Spike Interception
          </h3>
          <p className="text-xs text-[#A8A29E] leading-relaxed">
            Fraud rings execute burst attacks within minutes. Shieldex's Layer 2 EWMA detector flags the first abnormal transaction without waiting for days of bank settlement feedback.
          </p>
          <div className="text-xs text-[#10B981] mono font-semibold pt-2">
            0.0% False Alarm Rate Verified
          </div>
        </div>
      </div>
    </section>
  );
}

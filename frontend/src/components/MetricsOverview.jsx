import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, ReferenceLine } from 'recharts';
import { TrendingUp, AlertTriangle, ShieldCheck, DollarSign, CheckCircle2 } from 'lucide-react';

export default function MetricsOverview({ metrics, prCurveData }) {
  const m = metrics || {
    precision: 0.8889,
    recall: 0.8163,
    f1_score: 0.8511,
    pr_auc: 0.8610,
    roc_auc: 0.9841,
    threshold: 0.3596,
    true_positives: 80,
    false_positives: 10,
    true_negatives: 56854,
    false_negatives: 18,
    model_total_cost_inr: 91500,
    savings_vs_flag_nothing_inr: 398500,
    baselines: {
      flag_nothing_cost_inr: 490000,
      flag_everything_cost_inr: 8529600,
      'threshold_0.5_cost_inr': 96050
    }
  };

  const chartData = (prCurveData?.recall || []).map((rec, i) => ({
    recall: rec,
    precision: prCurveData?.precision[i] || 0,
  }));

  return (
    <div className="space-y-8">
      {/* KPI Highlights: Clean 4-Column Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: PR-AUC */}
        <div className="rzp-card p-5 bg-[#14110e] border-[#292524]">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-[#A8A29E] font-medium">Primary Metric (PR-AUC)</span>
            <TrendingUp className="h-4 w-4 text-[#E5A93C]" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="mono text-2xl font-bold text-[#FAFAF9]">
              {(m.pr_auc * 100).toFixed(2)}%
            </span>
            <span className="text-xs font-semibold text-[#10B981]">+15.1% vs Baseline</span>
          </div>
          <div className="mt-2 text-[10px] text-[#78716C] mono">
            ROC-AUC: {(m.roc_auc * 100).toFixed(2)}%
          </div>
        </div>

        {/* KPI 2: ₹ Savings */}
        <div className="rzp-card p-5 bg-[#14110e] border-[#292524]">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-[#A8A29E] font-medium">₹ Cost Saved</span>
            <DollarSign className="h-4 w-4 text-[#10B981]" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="mono text-2xl font-bold text-[#10B981]">
              ₹{(m.savings_vs_flag_nothing_inr / 1000).toFixed(1)}k
            </span>
            <span className="text-xs text-[#A8A29E]">on test set</span>
          </div>
          <div className="mt-2 text-[10px] text-[#78716C] mono">
            Model Net Loss: ₹{(m.model_total_cost_inr).toLocaleString()}
          </div>
        </div>

        {/* KPI 3: Precision / Recall */}
        <div className="rzp-card p-5 bg-[#14110e] border-[#292524]">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-[#A8A29E] font-medium">Precision / Recall</span>
            <ShieldCheck className="h-4 w-4 text-[#60a5fa]" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="mono text-2xl font-bold text-[#FAFAF9]">
              {(m.precision * 100).toFixed(1)}%
            </span>
            <span className="mono text-xs text-[#A8A29E]">/ {(m.recall * 100).toFixed(1)}%</span>
          </div>
          <div className="mt-2 text-[10px] text-[#78716C] mono">
            F1 Score: {(m.f1_score * 100).toFixed(2)}%
          </div>
        </div>

        {/* KPI 4: Operating Threshold */}
        <div className="rzp-card p-5 bg-[#14110e] border-[#292524]">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-[#A8A29E] font-medium">Operating Threshold</span>
            <span className="rzp-badge rzp-badge-gold text-[10px]">COST-TUNED</span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="mono text-2xl font-bold text-[#E5A93C]">
              {m.threshold.toFixed(4)}
            </span>
            <span className="text-xs text-[#78716C]">vs Naive 0.5</span>
          </div>
          <div className="mt-2 text-[10px] text-[#78716C] mono">
            Minimizes 33:1 FN to FP Cost Ratio
          </div>
        </div>
      </div>

      {/* Main Visual Evaluation Grid: PR Curve + Confusion Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left: PR Curve Chart */}
        <div className="lg:col-span-8 rzp-card p-6 bg-[#14110e] border-[#292524] space-y-4">
          <div className="flex items-center justify-between border-b border-[#292524] pb-3">
            <div>
              <h4 className="text-sm font-bold text-[#FAFAF9]">
                Precision-Recall Operating Curve
              </h4>
              <p className="text-[11px] text-[#A8A29E] mt-0.5">
                Evaluated on 56,962 transactions with extreme 0.17% class imbalance
              </p>
            </div>
            <span className="mono text-xs font-bold text-[#E5A93C]">
              PR-AUC: {(m.pr_auc * 100).toFixed(2)}%
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="goldGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#E5A93C" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#E5A93C" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="recall" stroke="#78716C" tick={{ fill: '#78716C', fontSize: 10 }} unit="%" />
                <YAxis stroke="#78716C" tick={{ fill: '#78716C', fontSize: 10 }} unit="%" domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0e0c0a', borderColor: '#292524', borderRadius: '8px', fontSize: '11px' }}
                />
                <Area type="monotone" dataKey="precision" stroke="#E5A93C" strokeWidth={2} fill="url(#goldGradient)" />
                <ReferenceLine x={m.recall * 100} stroke="#10B981" strokeDasharray="3 3" label={{ value: 'Operating Point', fill: '#10B981', fontSize: 10 }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right: Confusion Matrix & Baseline Comparisons */}
        <div className="lg:col-span-4 space-y-4">
          <div className="rzp-card p-5 bg-[#14110e] border-[#292524]">
            <h4 className="text-xs font-bold uppercase tracking-wider text-[#A8A29E] mb-3">
              Test Set Confusion Matrix
            </h4>
            <div className="grid grid-cols-2 gap-2.5">
              <div className="rounded bg-[#10B981]/10 border border-[#10B981]/20 p-3">
                <div className="text-[10px] text-[#A8A29E]">True Positives (TP)</div>
                <div className="mono text-xl font-bold text-[#10B981]">{m.true_positives}</div>
                <div className="text-[10px] text-[#78716C]">Fraud Blocked</div>
              </div>
              <div className="rounded bg-[#EF4444]/10 border border-[#EF4444]/20 p-3">
                <div className="text-[10px] text-[#A8A29E]">False Positives (FP)</div>
                <div className="mono text-xl font-bold text-[#EF4444]">{m.false_positives}</div>
                <div className="text-[10px] text-[#78716C]">Legit Blocked (Friction)</div>
              </div>
              <div className="rounded bg-[#EF4444]/10 border border-[#EF4444]/20 p-3">
                <div className="text-[10px] text-[#A8A29E]">False Negatives (FN)</div>
                <div className="mono text-xl font-bold text-[#EF4444]">{m.false_negatives}</div>
                <div className="text-[10px] text-[#78716C]">Missed Fraud Loss</div>
              </div>
              <div className="rounded bg-[#10B981]/10 border border-[#10B981]/20 p-3">
                <div className="text-[10px] text-[#A8A29E]">True Negatives (TN)</div>
                <div className="mono text-xl font-bold text-[#10B981]">{m.true_negatives.toLocaleString()}</div>
                <div className="text-[10px] text-[#78716C]">Legit Approved</div>
              </div>
            </div>
          </div>

          <div className="rzp-card p-5 bg-[#14110e] border-[#292524] text-xs">
            <h4 className="text-xs font-bold uppercase tracking-wider text-[#A8A29E] mb-3">
              ₹ Cost vs Naive Baselines
            </h4>
            <div className="space-y-2">
              <div className="flex justify-between py-1 border-b border-[#292524]">
                <span className="text-[#A8A29E]">Flag Nothing (Naive)</span>
                <span className="mono text-[#EF4444]">₹{m.baselines.flag_nothing_cost_inr.toLocaleString()}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#292524]">
                <span className="text-[#A8A29E]">Default 0.5 Threshold</span>
                <span className="mono text-[#A8A29E]">₹{(m.baselines?.['threshold_0.5_cost_inr'] || 96050).toLocaleString()}</span>
              </div>
              <div className="flex justify-between pt-1 text-[#10B981] font-bold">
                <span>Shieldex (Tuned)</span>
                <span className="mono">₹{m.model_total_cost_inr.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

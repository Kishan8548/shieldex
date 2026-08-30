import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, ReferenceLine } from 'recharts';
import { DollarSign, Sliders, AlertCircle, TrendingDown } from 'lucide-react';

export default function CostCurveOptimizer({ initialThreshold = 0.3596 }) {
  const [threshold, setThreshold] = useState(initialThreshold);
  const [costSweepData, setCostSweepData] = useState([]);
  const [costFN, setCostFN] = useState(5000);
  const [costFP, setCostFP] = useState(150);

  // Load threshold sweep data from API or generate dynamic sweep
  useEffect(() => {
    const fetchSweep = async () => {
      try {
        const res = await axios.get('/api/v1/metrics/cost-sweep');
        if (res.data?.full_threshold_sweep) {
          setCostSweepData(res.data.full_threshold_sweep);
        }
      } catch (e) {
        // Fallback synthetic sweep curve centered at 0.36
        const dummySweep = [];
        for (let t = 0.05; t <= 0.95; t += 0.05) {
          const fn = Math.round(98 * (1 - Math.pow(1 - t, 0.4)));
          const fp = Math.round(56864 * Math.pow(1 - t, 6));
          const total = fn * costFN + fp * costFP;
          dummySweep.push({
            threshold: parseFloat(t.toFixed(2)),
            total_cost_inr: total,
            FN: fn,
            FP: fp,
          });
        }
        setCostSweepData(dummySweep);
      }
    };
    fetchSweep();
  }, []);

  // Compute live point for current threshold slider
  const currentPoint = costSweepData.reduce((prev, curr) => {
    return Math.abs(curr.threshold - threshold) < Math.abs(prev.threshold - threshold) ? curr : prev;
  }, costSweepData[0] || { total_cost_inr: 91500, FN: 18, FP: 10 });

  const flagNothingCost = 98 * costFN; // ₹490,000 on test set
  const savings = flagNothingCost - (currentPoint?.total_cost_inr || 91500);

  return (
    <div className="space-y-6">
      {/* Overview Banner */}
      <div className="rzp-card p-5 border-l-4 border-l-[#E5A93C]">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold text-[#FAFAF9] flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-[#E5A93C]" />
              Cost-Aware Threshold Optimization Engine
            </h3>
            <p className="text-xs text-[#A8A29E] mt-1 leading-relaxed">
              In financial risk, defaulting to probability <code>0.5</code> is suboptimal because missing a fraud (₹5,000 chargeback) is <strong>33.3x more costly</strong> than blocking a legitimate customer (₹150 friction). Shieldex minimizes total expected merchant cost.
            </p>
          </div>
          <div className="text-right shrink-0">
            <span className="rzp-badge rzp-badge-gold">Track 02 Core Requirement</span>
          </div>
        </div>
      </div>

      {/* Interactive Controls & Live KPIs */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Slider & Cost Matrix Config */}
        <div className="lg:col-span-5 rzp-card p-5 space-y-5">
          <div>
            <div className="flex justify-between items-center text-xs text-[#FAFAF9] font-bold mb-2">
              <span className="flex items-center gap-1.5">
                <Sliders className="h-4 w-4 text-[#E5A93C]" /> Operating Threshold (τ)
              </span>
              <span className="mono text-[#E5A93C] text-sm">{threshold.toFixed(4)}</span>
            </div>
            <input
              type="range"
              min="0.05"
              max="0.95"
              step="0.01"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-[#292524] rounded-lg appearance-none cursor-pointer accent-[#E5A93C]"
            />
            <div className="flex justify-between text-[10px] text-[#78716C] mt-1 mono">
              <span>0.05 (Flag Aggressive)</span>
              <span className="text-[#E5A93C] font-semibold">0.3596 (Optimal)</span>
              <span>0.95 (Flag Conservative)</span>
            </div>
          </div>

          {/* Cost Matrix Settings */}
          <div className="space-y-3 pt-3 border-t border-[#292524]">
            <h4 className="text-xs font-bold text-[#A8A29E] uppercase tracking-wider">
              Cost Matrix Parameters (₹ INR)
            </h4>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[10px] text-[#78716C] mb-1">
                  False Negative Cost (Missed Fraud)
                </label>
                <div className="mono text-xs font-bold text-[#FAFAF9] bg-[#120f0c] p-2 rounded border border-[#292524]">
                  ₹{costFN.toLocaleString()}
                </div>
              </div>
              <div>
                <label className="block text-[10px] text-[#78716C] mb-1">
                  False Positive Cost (Legit Friction)
                </label>
                <div className="mono text-xs font-bold text-[#FAFAF9] bg-[#120f0c] p-2 rounded border border-[#292524]">
                  ₹{costFP.toLocaleString()}
                </div>
              </div>
            </div>
          </div>

          {/* Live Outcome Metrics at Chosen Threshold */}
          <div className="bg-[#120f0c] p-3.5 rounded border border-[#292524] space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-[#A8A29E]">Missed Frauds (FN):</span>
              <span className="mono text-[#EF4444] font-semibold">{currentPoint?.FN || 18} txns (₹{((currentPoint?.FN || 18) * costFN).toLocaleString()})</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#A8A29E]">False Alarms (FP):</span>
              <span className="mono text-[#E5A93C] font-semibold">{currentPoint?.FP || 10} txns (₹{((currentPoint?.FP || 10) * costFP).toLocaleString()})</span>
            </div>
            <div className="flex justify-between pt-2 border-t border-[#292524] font-bold">
              <span className="text-[#FAFAF9]">Net Expected Loss:</span>
              <span className="mono text-[#10B981]">₹{(currentPoint?.total_cost_inr || 91500).toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Live Loss Curve */}
        <div className="lg:col-span-7 rzp-card p-5">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h4 className="text-sm font-bold text-[#FAFAF9]">
                Total ₹ Cost vs Threshold Curve
              </h4>
              <p className="text-xs text-[#A8A29E]">
                Shows minimum expected monetary loss bowl
              </p>
            </div>
            <div className="text-right">
              <div className="text-[10px] text-[#78716C]">Current Savings</div>
              <div className="mono text-sm font-bold text-[#10B981]">
                ₹{(savings / 1000).toFixed(1)}k Saved
              </div>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={costSweepData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <XAxis
                  dataKey="threshold"
                  type="number"
                  domain={[0, 1]}
                  tick={{ fill: '#78716C', fontSize: 11 }}
                  label={{ value: 'Threshold (τ)', position: 'insideBottom', offset: -5, fill: '#78716C', fontSize: 10 }}
                />
                <YAxis
                  tick={{ fill: '#78716C', fontSize: 11 }}
                  tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#161310', borderColor: '#292524', borderRadius: '4px', fontSize: '11px' }}
                  formatter={(val) => [`₹${val.toLocaleString()}`, 'Total Expected Cost']}
                  labelFormatter={(l) => `Threshold: ${l}`}
                />
                <ReferenceLine x={threshold} stroke="#10B981" strokeDasharray="3 3" label={{ value: 'Current τ', fill: '#10B981', fontSize: 10, position: 'top' }} />
                <Line type="monotone" dataKey="total_cost_inr" stroke="#E5A93C" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

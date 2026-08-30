import React, { useState } from 'react';
import axios from 'axios';
import { Activity, ShieldAlert, ShieldCheck, Play, RotateCcw, AlertTriangle } from 'lucide-react';

const PRESET_TXNS = [
  {
    name: 'Sample 1: Clean E-Commerce Purchase',
    description: 'Normal buyer transaction matching historical merchant behavior',
    data: {
      Amount: 149.62,
      merchant_id: 'MERCH_001',
      V1: -1.3598, V2: -0.0728, V3: 2.5363, V4: 1.3782, V5: -0.3383,
      V6: 0.4624, V7: 0.2396, V8: 0.0987, V9: 0.3638, V10: 0.0908,
      V11: -0.5516, V12: -0.6178, V13: -0.9914, V14: -0.3112, V15: 1.4682,
      V16: -0.4704, V17: 0.2080, V18: 0.0258, V19: 0.4040, V20: 0.2514,
      V21: -0.0183, V22: 0.2778, V23: -0.1105, V24: 0.0669, V25: 0.1285,
      V26: -0.1891, V27: 0.1336, V28: -0.0211
    }
  },
  {
    name: 'Sample 2: Stolen Card Testing (High Risk)',
    description: 'Anomalous PCA features indicating card-not-present fraud attempt',
    data: {
      Amount: 4890.50,
      merchant_id: 'MERCH_003',
      V1: -4.3979, V2: 1.3584, V3: -2.5928, V4: 2.6798, V5: -1.1281,
      V6: -1.7065, V7: -3.4962, V8: -0.2488, V9: -0.2478, V10: -4.8016,
      V11: 3.4241, V12: -6.2164, V13: -0.4582, V14: -8.4908, V15: 0.1444,
      V16: -4.3168, V17: -6.9248, V18: -2.9832, V19: 0.9472, V20: -0.1716,
      V21: 0.5736, V22: 0.1769, V23: -0.4362, V24: -0.0535, V25: 0.2524,
      V26: 0.4133, V27: -0.1351, V28: -0.0773
    }
  },
  {
    name: 'Sample 3: High-Value Borderline Velocity',
    description: 'Large payment amount with moderate risk indicators',
    data: {
      Amount: 24500.00,
      merchant_id: 'MERCH_005',
      V1: 0.1254, V2: 0.8951, V3: -1.4521, V4: 1.1205, V5: 0.4512,
      V6: -0.8912, V7: 0.6521, V8: 0.1452, V9: -0.7812, V10: -0.9854,
      V11: 1.2541, V12: -1.1254, V13: 0.4512, V14: -2.1452, V15: -0.4512,
      V16: -1.1254, V17: -0.8954, V18: 0.2145, V19: 0.3541, V20: 0.4512,
      V21: 0.1245, V22: 0.3541, V23: -0.1245, V24: 0.4512, V25: -0.2145,
      V26: 0.1254, V27: 0.0451, V28: 0.0214
    }
  }
];

export default function TransactionSimulator({ onSelectForAgent }) {
  const [selectedPreset, setSelectedPreset] = useState(0);
  const [formData, setFormData] = useState(PRESET_TXNS[0].data);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSelectPreset = (index) => {
    setSelectedPreset(index);
    setFormData(PRESET_TXNS[index].data);
    setResult(null);
    setError(null);
  };

  const handleRunInference = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/v1/predict', formData);
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Inference call failed. Verify FastAPI backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Preset Selector */}
      <div className="rzp-card p-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-[#A8A29E] mb-3">
          Select Test Scenario Preset
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {PRESET_TXNS.map((preset, idx) => (
            <button
              key={idx}
              onClick={() => handleSelectPreset(idx)}
              className={`text-left p-3 rounded border transition-all ${
                selectedPreset === idx
                  ? 'border-[#E5A93C] bg-[#E5A93C]/10 text-[#FAFAF9]'
                  : 'border-[#292524] bg-[#120f0c] text-[#A8A29E] hover:border-[#44403c]'
              }`}
            >
              <div className="text-xs font-bold text-[#FAFAF9]">{preset.name}</div>
              <div className="text-[11px] text-[#78716C] mt-1 leading-snug">{preset.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Simulator Interface: Form Inputs & Real-Time Output */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Input Payload */}
        <div className="lg:col-span-5 rzp-card p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#292524]">
            <h4 className="text-sm font-bold text-[#FAFAF9]">Transaction Parameters</h4>
            <span className="mono text-xs text-[#E5A93C]">36 Total Features</span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-[#A8A29E] mb-1">
                Merchant ID
              </label>
              <input
                type="text"
                value={formData.merchant_id}
                onChange={(e) => setFormData({ ...formData, merchant_id: e.target.value })}
                className="w-full bg-[#120f0c] border border-[#292524] rounded px-2.5 py-1.5 text-xs text-[#FAFAF9] mono focus:border-[#E5A93C] focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-[#A8A29E] mb-1">
                Amount (₹ INR)
              </label>
              <input
                type="number"
                value={formData.Amount}
                onChange={(e) => setFormData({ ...formData, Amount: parseFloat(e.target.value) || 0 })}
                className="w-full bg-[#120f0c] border border-[#292524] rounded px-2.5 py-1.5 text-xs text-[#FAFAF9] mono focus:border-[#E5A93C] focus:outline-none"
              />
            </div>
          </div>

          {/* Collapsible Key PCA features preview */}
          <div>
            <label className="block text-[11px] font-semibold text-[#A8A29E] mb-1">
              Key PCA Vectors (V1 - V28 Normalized)
            </label>
            <div className="grid grid-cols-4 gap-2 bg-[#120f0c] p-2.5 rounded border border-[#292524] max-h-36 overflow-y-auto">
              {Object.keys(formData)
                .filter((k) => k.startsWith('V'))
                .slice(0, 16)
                .map((k) => (
                  <div key={k} className="text-[10px]">
                    <span className="text-[#78716C] mono">{k}: </span>
                    <span className="text-[#FAFAF9] mono">{formData[k]}</span>
                  </div>
                ))}
            </div>
          </div>

          <button
            onClick={handleRunInference}
            disabled={loading}
            className="w-full rzp-button py-2.5 text-xs"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <Activity className="h-4 w-4 animate-spin" /> Scoring Transaction...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Play className="h-4 w-4 fill-current" /> Execute Sub-15ms Defense Scoring
              </span>
            )}
          </button>

          {error && (
            <div className="rounded bg-[#EF4444]/10 border border-[#EF4444]/30 p-3 text-xs text-[#EF4444] flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Right: Scoring Verdict & SHAP Waterfall */}
        <div className="lg:col-span-7 rzp-card p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#292524]">
            <h4 className="text-sm font-bold text-[#FAFAF9]">Defense Verdict & SHAP Attribution</h4>
            {result && (
              <span className="mono text-xs text-[#10B981]">
                Latency: {result.latency_ms}ms
              </span>
            )}
          </div>

          {result ? (
            <div className="space-y-4">
              {/* Verdict Banner */}
              <div
                className={`rounded p-4 border flex items-center justify-between ${
                  result.is_fraud
                    ? 'bg-[#EF4444]/10 border-[#EF4444]/30 text-[#EF4444]'
                    : 'bg-[#10B981]/10 border-[#10B981]/30 text-[#10B981]'
                }`}
              >
                <div className="flex items-center gap-3">
                  {result.is_fraud ? (
                    <ShieldAlert className="h-6 w-6" />
                  ) : (
                    <ShieldCheck className="h-6 w-6" />
                  )}
                  <div>
                    <div className="text-sm font-bold tracking-tight">
                      {result.is_fraud ? 'HIGH RISK DETECTED — TRANSACTION BLOCKED' : 'CLEAN TRANSACTION — APPROVED'}
                    </div>
                    <div className="text-xs opacity-80 mt-0.5">
                      Merchant: {result.merchant_id} • Confidence: {result.confidence}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-[10px] uppercase font-semibold">Fraud Probability</div>
                  <div className="mono text-xl font-bold">
                    {(result.fraud_score * 100).toFixed(2)}%
                  </div>
                </div>
              </div>

              {/* Spike Alert if active */}
              {result.spike_alert && (
                <div className="rounded bg-[#E5A93C]/10 border border-[#E5A93C]/30 p-3 text-xs text-[#E5A93C] flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    <span>
                      <strong>EWMA Anomaly Active:</strong> Z-Score {result.spike_alert.z_score} exceeds baseline
                    </span>
                  </div>
                  <span className="rzp-badge rzp-badge-red text-[10px]">
                    {result.spike_alert.severity}
                  </span>
                </div>
              )}

              {/* SHAP Feature Attribution Waterfall */}
              <div>
                <div className="flex items-center justify-between text-xs text-[#A8A29E] mb-2 font-semibold">
                  <span>Top Feature Attribution (SHAP Importance)</span>
                  <span className="text-[10px] text-[#78716C]">TreeExplainer Ensemble</span>
                </div>
                <div className="space-y-2 bg-[#120f0c] p-3 rounded border border-[#292524]">
                  {(result.top_features || []).slice(0, 5).map((f, i) => {
                    const absVal = Math.min(Math.abs(f.shap_value) * 100, 100);
                    const isPositiveRisk = f.shap_value > 0;
                    return (
                      <div key={i} className="space-y-1">
                        <div className="flex justify-between text-xs mono">
                          <span className="text-[#FAFAF9]">{f.feature}</span>
                          <span className={isPositiveRisk ? 'text-[#EF4444]' : 'text-[#10B981]'}>
                            {isPositiveRisk ? '+' : ''}{f.shap_value.toFixed(4)}
                          </span>
                        </div>
                        <div className="h-1.5 w-full bg-[#1c1917] rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${isPositiveRisk ? 'bg-[#EF4444]' : 'bg-[#10B981]'}`}
                            style={{ width: `${Math.max(absVal, 5)}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Action Button to trigger LangGraph Copilot */}
              <div className="pt-2">
                <button
                  onClick={() => onSelectForAgent && onSelectForAgent(result, formData.Amount)}
                  className="w-full rzp-button-secondary py-2 text-xs justify-center"
                >
                  Inspect in LangGraph Autonomous Copilot →
                </button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-center text-[#78716C]">
              <Activity className="h-10 w-10 stroke-1 mb-3 text-[#44403c]" />
              <p className="text-xs">Select a scenario preset and click "Execute Defense Scoring"</p>
              <p className="text-[11px] text-[#57534e] mt-1">LightGBM + XGBoost weighted ensemble inference will execute in sub-15ms</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

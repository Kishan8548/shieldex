import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ProductHero from './components/ProductHero';
import ProductArchitectureSection from './components/ProductArchitectureSection';
import ProductBenchmarkSection from './components/ProductBenchmarkSection';
import MetricsOverview from './components/MetricsOverview';
import TransactionSimulator from './components/TransactionSimulator';
import CostCurveOptimizer from './components/CostCurveOptimizer';
import SpikeRadarTimeline from './components/SpikeRadarTimeline';
import LangGraphCopilot from './components/LangGraphCopilot';
import { TrendingUp, Activity, Sliders, Radio, BrainCircuit } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [metrics, setMetrics] = useState(null);
  const [prCurve, setPrCurve] = useState(null);
  const [selectedTxnForAgent, setSelectedTxnForAgent] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await axios.get('/api/v1/metrics');
        setMetrics(res.data);
        if (res.data?.pr_curve) {
          setPrCurve(res.data.pr_curve);
        }
      } catch (e) {
        setMetrics({
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
        });
      }
    };
    fetchMetrics();
  }, []);

  const handleOpenTab = (tabId) => {
    setActiveTab(tabId);
    const el = document.getElementById('terminal-console');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleSelectForAgent = (txnResult, amount) => {
    setSelectedTxnForAgent({
      merchant_id: txnResult.merchant_id,
      amount_inr: amount || 24500,
      fraud_score: txnResult.fraud_score,
      is_ml_fraud: txnResult.is_fraud,
      threshold_used: txnResult.threshold_used || 0.3596,
      top_features: txnResult.top_features || [],
      spike_alert: txnResult.spike_alert
    });
    setActiveTab('copilot');
    const el = document.getElementById('terminal-console');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const tabs = [
    { id: 'overview', label: 'Evaluation & KPIs', icon: TrendingUp },
    { id: 'simulator', label: 'Transaction Inspector & SHAP', icon: Activity },
    { id: 'cost', label: '₹ Cost Optimizer', icon: Sliders },
    { id: 'radar', label: 'Merchant Spike Radar', icon: Radio, badge: 2 },
    { id: 'copilot', label: 'LangGraph Autonomous Agent', icon: BrainCircuit },
  ];

  return (
    <div className="min-h-screen bg-[#0a0806] text-[#FAFAF9] selection:bg-[#E5A93C] selection:text-black">
      {/* 1. Shieldex Product Hero */}
      <ProductHero onLaunchTerminal={() => handleOpenTab('simulator')} />

      {/* 2. 3-Tier Stacked Architecture Rows with Vertical 3D Scroll Physics */}
      <ProductArchitectureSection />

      {/* 3. Measured Impact & Cost Philosophy */}
      <ProductBenchmarkSection onOpenCostOptimizer={() => handleOpenTab('cost')} />

      {/* 4. Live Shieldex Defense Operations Console (Single-View Tabbed Console) */}
      <div id="terminal-console" className="pt-20 pb-28 border-t border-[#292524] bg-[#0a0806]">
        <div className="max-w-7xl mx-auto px-6 mb-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <div className="mono text-xs text-[#E5A93C] uppercase tracking-widest font-bold">
                INTERACTIVE OPERATIONS CONSOLE
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-[#FAFAF9] mt-1">
                Live Risk & Defense Terminal
              </h2>
              <p className="text-xs sm:text-sm text-[#A8A29E] mt-1">
                Select a tab below to switch between model evaluation, real-time SHAP scoring, threshold optimizer, spike radar, and LangGraph copilot.
              </p>
            </div>

            <div className="flex items-center gap-2 text-[11px] mono text-[#10B981] bg-[#14110e] px-3 py-1.5 rounded-lg border border-[#292524]">
              <span className="h-2 w-2 rounded-full bg-[#10B981] animate-pulse"></span>
              <span>FastAPI Gateway: Active</span>
            </div>
          </div>

          {/* Clean Tab Switcher Bar */}
          <div className="mt-8 flex flex-wrap items-center gap-2 border-b border-[#292524] pb-3">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-[#14110e] text-[#E5A93C] border border-[#E5A93C]/40 shadow-sm'
                      : 'text-[#A8A29E] hover:text-[#FAFAF9] hover:bg-[#14110e]/40 border border-transparent'
                  }`}
                >
                  <Icon className={`h-4 w-4 ${isActive ? 'text-[#E5A93C]' : 'text-[#78716C]'}`} />
                  <span>{tab.label}</span>
                  {tab.badge ? (
                    <span className="ml-1 rounded-full bg-[#EF4444] px-1.5 py-0.2 text-[10px] font-bold text-white">
                      {tab.badge}
                    </span>
                  ) : null}
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab Viewport: Renders only the active tab in-place */}
        <main className="max-w-7xl mx-auto px-6">
          {activeTab === 'overview' && (
            <MetricsOverview metrics={metrics} prCurveData={prCurve} />
          )}

          {activeTab === 'simulator' && (
            <TransactionSimulator onSelectForAgent={handleSelectForAgent} />
          )}

          {activeTab === 'cost' && (
            <CostCurveOptimizer initialThreshold={metrics?.threshold || 0.3596} />
          )}

          {activeTab === 'radar' && (
            <SpikeRadarTimeline />
          )}

          {activeTab === 'copilot' && (
            <LangGraphCopilot initialTransaction={selectedTxnForAgent} />
          )}
        </main>
      </div>

      {/* Clean Footer */}
      <footer className="border-t border-[#292524] bg-[#070504] px-6 py-12 text-xs text-[#78716C]">
        <div className="mx-auto max-w-7xl flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <div className="font-bold text-[#FAFAF9] text-base mb-1">
              Shieldex <span className="text-[#E5A93C]">/</span> Autonomous Payment Risk Engine
            </div>
            <p className="text-[#A8A29E] max-w-md">
              Strictly defense-only payment security infrastructure. Evaluated on 56,962 held-out transactions with honest INR cost-benefit metrics.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row items-center gap-6 mono text-[11px]">
            <a
              href="https://github.com/Kishan8548/shieldex"
              target="_blank"
              rel="noreferrer"
              className="text-[#FAFAF9] hover:text-[#E5A93C] transition-colors"
            >
              GitHub: Kishan8548/shieldex
            </a>
            <span>•</span>
            <span className="text-[#A8A29E]">Sub-15ms Real-Time Inference</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

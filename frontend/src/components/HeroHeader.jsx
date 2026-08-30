import React from 'react';
import {
  TrendingUp,
  Activity,
  Sliders,
  Radio,
  BrainCircuit,
} from 'lucide-react';

export default function HeroHeader({ activeTab, setActiveTab, liveAlertsCount }) {
  const tabs = [
    { id: 'overview', label: 'Evaluation & KPIs', icon: TrendingUp },
    { id: 'simulator', label: 'Transaction Inspector & SHAP', icon: Activity },
    { id: 'cost', label: '₹ Cost-Curve Optimizer', icon: Sliders },
    { id: 'radar', label: 'Merchant Spike Radar', icon: Radio, badge: liveAlertsCount },
    { id: 'copilot', label: 'LangGraph Autonomous Agent', icon: BrainCircuit },
  ];

  return (
    <header className="border-b border-[#292524] bg-[#0a0806] px-6 py-4">
      <div className="mx-auto max-w-7xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Navigation Tabs */}
        <nav className="flex flex-wrap items-center gap-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
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
        </nav>

        {/* Live System Status Indicator */}
        <div className="flex items-center gap-4 text-[11px] mono">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-[#10B981] animate-pulse"></span>
            <span className="text-[#A8A29E]">FastAPI Gateway: <strong className="text-[#10B981]">Healthy</strong></span>
          </div>
          <span className="text-[#78716C]">•</span>
          <span className="text-[#78716C]">Sub-15ms Defense Engine</span>
        </div>
      </div>
    </header>
  );
}

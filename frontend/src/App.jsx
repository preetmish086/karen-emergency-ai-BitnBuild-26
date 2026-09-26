import React, { useState, useEffect } from 'react';
import {
  Flame,
  AlertOctagon,
  Car,
  HeartPulse,
  Building2,
  Waves,
  ShieldAlert,
  HelpCircle,
  Radio,
  RefreshCw,
  PlusCircle,
  Send,
  CheckCircle,
  Truck,
  RotateCcw,
  Search,
  MapPin,
  TrendingUp,
  Cpu,
  Layers,
  ChevronRight,
  Info
} from 'lucide-react';

const INCIDENT_ICONS = {
  fire: <Flame className="w-4 h-4 text-orange-400" />,
  explosion: <AlertOctagon className="w-4 h-4 text-red-500" />,
  accident: <Car className="w-4 h-4 text-amber-400" />,
  medical: <HeartPulse className="w-4 h-4 text-rose-400" />,
  collapse: <Building2 className="w-4 h-4 text-yellow-500" />,
  flood: <Waves className="w-4 h-4 text-blue-400" />,
  crime: <ShieldAlert className="w-4 h-4 text-purple-400" />,
  missing_person: <HelpCircle className="w-4 h-4 text-cyan-400" />,
  unknown: <Radio className="w-4 h-4 text-slate-400" />,
  other: <Radio className="w-4 h-4 text-slate-400" />,
};

const PRESET_SIMULATIONS = [
  {
    title: "🚨 Subway Explosion & Smoke",
    text: "Massive explosion and heavy smoke near 14th St subway station! Multiple commuters trapped and screaming for help.",
  },
  {
    title: "🔥 Commercial Warehouse Fire",
    text: "Three-story industrial warehouse on Elm Street is fully engulfed in flames. Chemical containers stored inside.",
  },
  {
    title: "🌊 Flash Flood with Trapped Cars",
    text: "Water level rapidly surging near River Boulevard. Two sedans are submerged with passengers on roofs.",
  },
  {
    title: "❓ Vague Unverified Rumor",
    text: "Heard something loud maybe 2 miles away near the industrial park, not sure what it was.",
  }
];

export default function App() {
  const [reports, setReports] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState(null);
  const [explanation, setExplanation] = useState(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');

  // Simulation Modal
  const [showSimulateModal, setShowSimulateModal] = useState(false);
  const [simText, setSimText] = useState('');
  const [simSubmitting, setSimSubmitting] = useState(false);

  // Dispatch Action State
  const [dispatchUnit, setDispatchUnit] = useState('Engine 1 (Fire)');

  const fetchData = async () => {
    try {
      const [repRes, statsRes] = await Promise.all([
        fetch('/api/reports'),
        fetch('/api/stats')
      ]);

      if (repRes.ok) {
        const data = await repRes.json();
        setReports(data);
        if (!selectedReport && data.length > 0) {
          selectReport(data[0]);
        } else if (selectedReport) {
          const updated = data.find(r => r.report_id === selectedReport.report_id);
          if (updated) setSelectedReport(updated);
        }
      }

      if (statsRes.ok) {
        const sData = await statsRes.json();
        setStats(sData);
      }
    } catch (err) {
      console.error("Error fetching emergency data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 8000);
    return () => clearInterval(interval);
  }, []);

  const selectReport = async (report) => {
    setSelectedReport(report);
    try {
      const res = await fetch(`/api/reports/${report.report_id}/explain`);
      if (res.ok) {
        const expData = await res.json();
        setExplanation(expData);
      }
    } catch (e) {
      console.error("Failed to fetch explanation:", e);
    }
  };

  const handleSimulateSubmit = async (textToSubmit) => {
    const content = textToSubmit || simText;
    if (!content.trim()) return;

    setSimSubmitting(true);
    try {
      const res = await fetch('/api/reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: content })
      });
      if (res.ok) {
        const newReport = await res.json();
        setSimText('');
        setShowSimulateModal(false);
        await fetchData();
        selectReport(newReport);
      }
    } catch (e) {
      console.error("Simulation error:", e);
    } finally {
      setSimSubmitting(false);
    }
  };

  const handleDispatchAction = async (reportId, newStatus, unit) => {
    try {
      const res = await fetch(`/api/reports/${reportId}/dispatch`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          dispatched_unit: unit || dispatchUnit
        })
      });
      if (res.ok) {
        await fetchData();
      }
    } catch (e) {
      console.error("Dispatch action error:", e);
    }
  };

  const handleResetData = async () => {
    try {
      await fetch('/api/reports/reset', { method: 'POST' });
      await fetchData();
    } catch (e) {
      console.error("Reset error:", e);
    }
  };

  // Filter logic
  const filteredReports = reports.filter(r => {
    if (selectedType !== 'all' && r.incident_type !== selectedType) return false;
    if (selectedSeverity !== 'all' && r.severity !== selectedSeverity) return false;
    if (selectedStatus !== 'all' && r.dispatch_status !== selectedStatus) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const inText = r.text.toLowerCase().includes(q);
      const inLoc = r.location && r.location.toLowerCase().includes(q);
      const inType = r.incident_type.toLowerCase().includes(q);
      return inText || inLoc || inType;
    }
    return true;
  });

  const getPriorityBadgeClass = (priority) => {
    if (priority >= 0.85) return 'bg-red-500/20 text-red-400 border-red-500/40 shadow-red-950/50';
    if (priority >= 0.70) return 'bg-orange-500/20 text-orange-400 border-orange-500/40 shadow-orange-950/50';
    if (priority >= 0.50) return 'bg-amber-500/20 text-amber-400 border-amber-500/40 shadow-amber-950/50';
    return 'bg-slate-700/40 text-slate-400 border-slate-600/40 shadow-none';
  };

  const getSeverityBadgeClass = (severity) => {
    switch (severity) {
      case 'critical': return 'bg-red-900/60 text-red-300 border-red-700';
      case 'high': return 'bg-orange-900/60 text-orange-300 border-orange-700';
      case 'medium': return 'bg-amber-900/60 text-amber-300 border-amber-700';
      default: return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col font-sans">
      {/* Top Mission Control Header */}
      <header className="border-b border-slate-800 bg-[#0d1322]/80 backdrop-blur sticky top-0 z-30 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-red-600 to-amber-600 flex items-center justify-center shadow-lg shadow-red-950/50 border border-red-500/40">
            <Radio className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-white m-0">Karen's Ear</h1>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                DISPATCH AI v1.0
              </span>
            </div>
            <p className="text-xs text-slate-400 m-0">Autonomous Emergency Prioritization & Triage Engine</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="hidden md:flex items-center space-x-2 text-xs text-emerald-400 bg-emerald-950/40 px-3 py-1.5 rounded-lg border border-emerald-800/40">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>Priority Engine Active</span>
          </div>

          <button
            onClick={() => setShowSimulateModal(true)}
            className="flex items-center space-x-1.5 text-xs font-semibold bg-red-600 hover:bg-red-500 text-white px-3.5 py-2 rounded-lg transition shadow-md shadow-red-950/60 cursor-pointer"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Simulate Emergency</span>
          </button>

          <button
            onClick={handleResetData}
            title="Reset to sample dataset"
            className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 px-3 py-2 rounded-lg border border-slate-700 transition cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Reset Data</span>
          </button>

          <button
            onClick={fetchData}
            title="Refresh feed"
            className="p-2 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition cursor-pointer"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* KPI Stats Bar */}
      <div className="px-6 py-4 grid grid-cols-2 md:grid-cols-4 gap-4 bg-[#0c111f] border-b border-slate-800/80">
        <div className="bg-[#111728] p-3.5 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Active Incidents</p>
            <h3 className="text-2xl font-bold text-white mt-0.5">{stats ? stats.total_reports : '--'}</h3>
          </div>
          <div className="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <Layers className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111728] p-3.5 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Critical Alerts</p>
            <h3 className="text-2xl font-bold text-red-400 mt-0.5">{stats ? stats.critical_count : '--'}</h3>
          </div>
          <div className="w-10 h-10 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400">
            <AlertOctagon className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111728] p-3.5 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Pending Dispatch</p>
            <h3 className="text-2xl font-bold text-amber-400 mt-0.5">{stats ? stats.pending_dispatch : '--'}</h3>
          </div>
          <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <Truck className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#111728] p-3.5 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Avg AI Priority</p>
            <h3 className="text-2xl font-bold text-emerald-400 mt-0.5">{stats ? (stats.average_priority * 100).toFixed(0) + '%' : '--'}</h3>
          </div>
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="flex-1 px-6 py-5 flex flex-col lg:flex-row gap-6 overflow-hidden">
        {/* Left Column: Triage Queue & Filters */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Controls & Filter Bar */}
          <div className="bg-[#111728] p-3 rounded-xl border border-slate-800 mb-4 flex flex-wrap gap-2.5 items-center justify-between">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search reports by text, landmark, incident..."
                className="w-full bg-[#0a0f1d] border border-slate-700/80 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-red-500"
              />
            </div>

            <div className="flex items-center space-x-2">
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="bg-[#0a0f1d] border border-slate-700 text-xs rounded-lg px-2.5 py-1.5 text-slate-300 focus:outline-none focus:border-red-500"
              >
                <option value="all">All Incident Types</option>
                <option value="fire">Fire</option>
                <option value="explosion">Explosion</option>
                <option value="accident">Accident</option>
                <option value="medical">Medical</option>
                <option value="collapse">Collapse</option>
                <option value="flood">Flood</option>
                <option value="crime">Crime</option>
                <option value="unknown">Unknown</option>
              </select>

              <select
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
                className="bg-[#0a0f1d] border border-slate-700 text-xs rounded-lg px-2.5 py-1.5 text-slate-300 focus:outline-none focus:border-red-500"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>

              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="bg-[#0a0f1d] border border-slate-700 text-xs rounded-lg px-2.5 py-1.5 text-slate-300 focus:outline-none focus:border-red-500"
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="dispatched">Dispatched</option>
                <option value="resolved">Resolved</option>
              </select>
            </div>
          </div>

          {/* Queue Count */}
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2 px-1">
            <span>TRIAGE QUEUE (SORTED BY AI PRIORITY)</span>
            <span>Showing {filteredReports.length} of {reports.length} Reports</span>
          </div>

          {/* Report Feed Cards */}
          <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 max-h-[calc(100vh-290px)]">
            {loading ? (
              <div className="text-center py-12 text-slate-500 text-sm">Loading emergency feed...</div>
            ) : filteredReports.length === 0 ? (
              <div className="text-center py-12 text-slate-500 bg-[#111728]/50 rounded-xl border border-slate-800">
                No emergency reports matching current filters.
              </div>
            ) : (
              filteredReports.map((report) => {
                const isSelected = selectedReport && selectedReport.report_id === report.report_id;
                return (
                  <div
                    key={report.report_id}
                    onClick={() => selectReport(report)}
                    className={`p-3.5 rounded-xl border transition cursor-pointer text-left ${
                      isSelected
                        ? 'bg-[#161f36] border-red-500/70 shadow-lg shadow-red-950/20 ring-1 ring-red-500/40'
                        : 'bg-[#101626] border-slate-800 hover:border-slate-700 hover:bg-[#131b2e]'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-xs font-semibold text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded">
                          {report.report_id}
                        </span>
                        <div className="flex items-center space-x-1.5 text-xs font-medium text-slate-200 capitalize">
                          {INCIDENT_ICONS[report.incident_type] || INCIDENT_ICONS.unknown}
                          <span>{report.incident_type.replace('_', ' ')}</span>
                        </div>
                        <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border ${getSeverityBadgeClass(report.severity)}`}>
                          {report.severity}
                        </span>
                      </div>

                      {/* Priority Score Tag */}
                      <div className={`px-2.5 py-1 rounded-lg border font-mono font-bold text-xs flex items-center space-x-1 ${getPriorityBadgeClass(report.priority)}`}>
                        <TrendingUp className="w-3.5 h-3.5" />
                        <span>{(report.priority * 100).toFixed(0)}% PRIORITY</span>
                      </div>
                    </div>

                    <p className="text-sm text-slate-200 mt-2 font-normal leading-relaxed">
                      {report.text}
                    </p>

                    <div className="mt-3 pt-2.5 border-t border-slate-800/70 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2">
                      <div className="flex items-center space-x-3">
                        <span className="flex items-center space-x-1 text-slate-300">
                          <MapPin className="w-3.5 h-3.5 text-red-400" />
                          <span>{report.location || 'Unknown location'}</span>
                        </span>
                        <span className="text-slate-500">•</span>
                        <span>Credibility: <strong className="text-slate-300 font-mono">{(report.credibility * 100).toFixed(0)}%</strong></span>
                      </div>

                      <div className="flex items-center space-x-2">
                        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded uppercase ${
                          report.dispatch_status === 'dispatched'
                            ? 'bg-blue-900/60 text-blue-300 border border-blue-700'
                            : report.dispatch_status === 'resolved'
                            ? 'bg-emerald-900/60 text-emerald-300 border border-emerald-700'
                            : 'bg-slate-800 text-slate-400'
                        }`}>
                          {report.dispatch_status} {report.dispatched_unit && `(${report.dispatched_unit})`}
                        </span>
                        <ChevronRight className="w-4 h-4 text-slate-500" />
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Column: AI Inspector & Dispatch Controls */}
        <div className="w-full lg:w-96 flex flex-col space-y-4">
          {/* Dispatch Control Station */}
          <div className="bg-[#111728] p-4 rounded-xl border border-slate-800">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
              <div className="flex items-center space-x-2">
                <Truck className="w-4 h-4 text-amber-400" />
                <h3 className="text-sm font-bold text-white m-0">Dispatcher Action Hub</h3>
              </div>
              {selectedReport && (
                <span className="font-mono text-xs text-slate-400">{selectedReport.report_id}</span>
              )}
            </div>

            {selectedReport ? (
              <div className="space-y-3">
                <div>
                  <label className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold block mb-1">
                    Assign Emergency Response Unit
                  </label>
                  <select
                    value={dispatchUnit}
                    onChange={(e) => setDispatchUnit(e.target.value)}
                    className="w-full bg-[#0a0f1d] border border-slate-700 text-xs rounded-lg p-2 text-slate-200 focus:outline-none focus:border-red-500"
                  >
                    <option value="Engine 1 (Fire & Rescue)">Engine 1 (Fire & Rescue)</option>
                    <option value="Engine 4 (Hazmat)">Engine 4 (Hazmat)</option>
                    <option value="Ambulance Medic 2">Ambulance Medic 2 (EMS)</option>
                    <option value="Ambulance Medic 7">Ambulance Medic 7 (Critical Care)</option>
                    <option value="Police Sector Unit 12">Police Sector Unit 12</option>
                    <option value="Urban Search & Rescue Team">Urban Search & Rescue Team</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-1">
                  <button
                    onClick={() => handleDispatchAction(selectedReport.report_id, 'dispatched')}
                    disabled={selectedReport.dispatch_status === 'dispatched'}
                    className={`py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center space-x-1.5 transition cursor-pointer ${
                      selectedReport.dispatch_status === 'dispatched'
                        ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                        : 'bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-950/50'
                    }`}
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>Dispatch Unit</span>
                  </button>

                  <button
                    onClick={() => handleDispatchAction(selectedReport.report_id, 'resolved')}
                    className="py-2 px-3 bg-emerald-700/80 hover:bg-emerald-600 text-white rounded-lg text-xs font-semibold flex items-center justify-center space-x-1.5 transition cursor-pointer"
                  >
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>Mark Resolved</span>
                  </button>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500 py-4 text-center">Select an incident from the queue to dispatch</p>
            )}
          </div>

          {/* AI Explainability Inspector */}
          <div className="bg-[#111728] p-4 rounded-xl border border-slate-800 flex-1 flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
              <div className="flex items-center space-x-2">
                <Cpu className="w-4 h-4 text-red-400" />
                <h3 className="text-sm font-bold text-white m-0">Priority AI Explainability</h3>
              </div>
              <span className="text-[10px] bg-red-950/60 text-red-300 border border-red-800 px-2 py-0.5 rounded">
                WEIGHTED MODEL
              </span>
            </div>

            {explanation ? (
              <div className="space-y-3.5 text-xs">
                <div className="p-3 rounded-lg bg-[#0a0f1d] border border-slate-800/80">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-slate-400">Recommendation</span>
                    <span className="font-bold font-mono text-red-400">{explanation.recommendation}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Total Priority</span>
                    <span className="font-bold font-mono text-white text-base">{(explanation.final_priority * 100).toFixed(0)}%</span>
                  </div>
                </div>

                {/* Component Breakdown Bars */}
                <div className="space-y-2.5">
                  <div>
                    <div className="flex justify-between text-slate-300 mb-1">
                      <span>Severity ({explanation.components.severity.level})</span>
                      <span className="font-mono text-slate-400">{(explanation.components.severity.contribution * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-2">
                      <div
                        className="bg-red-500 h-2 rounded-full"
                        style={{ width: `${(explanation.components.severity.contribution / 0.45) * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-300 mb-1">
                      <span>Actionability ({explanation.components.actionability.level})</span>
                      <span className="font-mono text-slate-400">{(explanation.components.actionability.contribution * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-2">
                      <div
                        className="bg-orange-400 h-2 rounded-full"
                        style={{ width: `${(explanation.components.actionability.contribution / 0.25) * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-300 mb-1">
                      <span>Credibility Assessment</span>
                      <span className="font-mono text-slate-400">{(explanation.components.credibility.contribution * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-2">
                      <div
                        className="bg-blue-400 h-2 rounded-full"
                        style={{ width: `${(explanation.components.credibility.contribution / 0.22) * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-300 mb-1">
                      <span>Corroboration Bonus</span>
                      <span className="font-mono text-slate-400">{(explanation.components.corroboration.contribution * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-2">
                      <div
                        className="bg-emerald-400 h-2 rounded-full"
                        style={{ width: `${(explanation.components.corroboration.contribution / 0.08) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                <div className="p-2.5 rounded bg-slate-800/40 text-[11px] text-slate-400 leading-normal flex items-start space-x-2">
                  <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                  <span>
                    Karen's Ear weights critical life-threatening conditions highest, boosting reports that have specific location data and corroborating cluster reports.
                  </span>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-slate-500 text-xs">
                Select an incident to view mathematical breakdown.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Simulate Incident Modal */}
      {showSimulateModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#111728] border border-slate-700 rounded-2xl max-w-lg w-full p-5 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <Radio className="w-5 h-5 text-red-500" />
                <h3 className="text-base font-bold text-white m-0">Simulate Incoming 911 Call / Report</h3>
              </div>
              <button
                onClick={() => setShowSimulateModal(false)}
                className="text-slate-400 hover:text-white text-lg font-bold px-2"
              >
                ✕
              </button>
            </div>

            <div>
              <p className="text-xs text-slate-400 mb-2 font-medium">Quick Scenarios (Click to test AI triage):</p>
              <div className="grid grid-cols-1 gap-2">
                {PRESET_SIMULATIONS.map((preset, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSimulateSubmit(preset.text)}
                    disabled={simSubmitting}
                    className="text-left text-xs p-2.5 rounded-lg bg-[#0a0f1d] hover:bg-slate-800 border border-slate-800 hover:border-slate-700 transition cursor-pointer flex flex-col space-y-1"
                  >
                    <span className="font-semibold text-slate-200">{preset.title}</span>
                    <span className="text-[11px] text-slate-400 line-clamp-1">{preset.text}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800">
              <label className="text-xs font-semibold text-slate-300 block mb-1.5">
                Or Enter Custom Emergency Report:
              </label>
              <textarea
                rows={3}
                value={simText}
                onChange={(e) => setSimText(e.target.value)}
                placeholder="e.g. Chemical spill and fire near Main Street bridge, three workers need immediate rescue..."
                className="w-full bg-[#0a0f1d] border border-slate-700 rounded-xl p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-red-500"
              />
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setShowSimulateModal(false)}
                className="px-4 py-2 rounded-lg text-xs text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 transition cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={() => handleSimulateSubmit()}
                disabled={simSubmitting || !simText.trim()}
                className={`px-4 py-2 rounded-lg text-xs font-semibold text-white flex items-center space-x-1.5 transition cursor-pointer ${
                  simSubmitting || !simText.trim()
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                    : 'bg-red-600 hover:bg-red-500 shadow-md shadow-red-950/60'
                }`}
              >
                <Send className="w-3.5 h-3.5" />
                <span>{simSubmitting ? 'Processing AI...' : 'Submit to Pipeline'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

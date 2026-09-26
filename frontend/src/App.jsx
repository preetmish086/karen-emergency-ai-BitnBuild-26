import React, { useState, useEffect, useRef } from 'react';
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
  RotateCcw,
  Search,
  MapPin,
  TrendingUp,
  Cpu,
  Layers,
  ChevronRight,
  Info,
  Volume2,
  VolumeX,
  Compass,
  Zap,
  Target,
  Navigation
} from 'lucide-react';

// Custom Spider-Man Icon
function SpiderIcon({ className = "w-5 h-5" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C10.9 2 10 2.9 10 4C10 4.6 10.2 5.1 10.6 5.5C8.9 5.8 7.4 6.8 6.5 8.3C5.5 8.1 4.5 8.5 3.8 9.2C3.1 9.9 2.9 11 3.2 12C3.6 13.1 4.7 13.8 5.8 13.6C6.1 14.8 6.9 15.9 8 16.5C7.5 17.5 7.4 18.7 7.9 19.8C8.3 20.9 9.3 21.6 10.5 21.7C10.7 22.4 11.3 23 12 23C12.7 23 13.3 22.4 13.5 21.7C14.7 21.6 15.7 20.9 16.1 19.8C16.6 18.7 16.5 17.5 16 16.5C17.1 15.9 17.9 14.8 18.2 13.6C19.3 13.8 20.4 13.1 20.8 12C21.1 11 20.9 9.9 20.2 9.2C19.5 8.5 18.5 8.1 17.5 8.3C16.6 6.8 15.1 5.8 13.4 5.5C13.8 5.1 14 4.6 14 4C14 2.9 13.1 2 12 2ZM12 7C14.2 7 16 8.8 16 11C16 12.3 15.4 13.4 14.4 14.2C14.8 15.3 14.7 16.6 14.2 17.7C13.7 18.7 12.8 19.3 11.7 19.5C11.5 19.1 11.2 18.8 10.8 18.6C11.3 17.9 11.5 17 11.3 16.2C11.1 15.4 10.6 14.7 9.8 14.3C9.2 13.5 8.8 12.5 8.8 11.4C8.8 9 10.2 7 12 7Z" />
    </svg>
  );
}

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

// Map simulation coordinates for New York City landmarks
const NYC_LOCATIONS = {
  "central market": { x: 50, y: 44, label: "Central Market", zone: "Midtown" },
  "Station Road": { x: 62, y: 38, label: "Station Rd / Grand Central", zone: "Midtown East" },
  "highway": { x: 28, y: 25, label: "West Side Hwy", zone: "Upper West" },
  "riverside area": { x: 22, y: 55, label: "Hudson Riverfront", zone: "Chelsea" },
  "downtown": { x: 58, y: 78, label: "Downtown / Financial", zone: "Financial Dist" },
  "market": { x: 48, y: 46, label: "Market District", zone: "Midtown" },
  "bus stand": { x: 40, y: 42, label: "Port Authority", zone: "Hell's Kitchen" },
  "Times Square": { x: 45, y: 35, label: "Times Square", zone: "Theater Dist" }
};

const PRESET_SIMULATIONS = [
  {
    title: "🦎 THE LIZARD-THING HEADING DOWNTOWN",
    text: "The giant lizard-thing just smashed through a subway grate on 8th Ave and is heading downtown towards Penn Station!",
  },
  {
    title: "💥 5TH AVE COLLAPSE & EXPLOSION",
    text: "Huge explosion near the central market! Building facade collapsed, multiple people are stuck under the rubble!",
  },
  {
    title: "🔥 THREE-STORY APARTMENT BLAZE",
    text: "Smoke and heavy fire coming from residential building near Station Road. People waving from 4th floor.",
  },
  {
    title: "🌊 FLASH FLOOD AT RIVERSIDE",
    text: "Water rising rapidly near the riverside area. Cars stalling and pedestrians stranded on elevated barriers.",
  },
  {
    title: "❓ VAGUE INDISTINCT NOISE",
    text: "Not sure what happened but there is a loud noise somewhere downtown near the docks.",
  }
];

export default function App() {
  const [reports, setReports] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState(null);
  const [explanation, setExplanation] = useState(null);

  // Audio voice synthesis state
  const [isSpeaking, setIsSpeaking] = useState(false);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');

  // Simulation Modal
  const [showSimulateModal, setShowSimulateModal] = useState(false);
  const [simText, setSimText] = useState('');
  const [simSubmitting, setSimSubmitting] = useState(false);

  // Spidey Suit HUD Mode
  const [hudMode, setHudMode] = useState('spidey'); // 'spidey' or 'dispatch'

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

  // Top target for "Where to Swing First"
  const topReport = reports.length > 0 ? reports[0] : null;

  // Karen Voice Synthesizer using Web Speech API
  const speakKarenDirective = () => {
    if (!('speechSynthesis' in window)) {
      alert("Text-to-speech is not supported in this browser.");
      return;
    }

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    if (!topReport) return;

    const speechText = `Peter, I have prioritized the emergency communications. Your primary directive is at ${topReport.location || 'the target sector'}. ${topReport.text} The threat level is ${topReport.severity}, with an estimated priority score of ${(topReport.priority * 100).toFixed(0)} percent. I recommend immediate web-swing intervention.`;

    const utterance = new SpeechSynthesisUtterance(speechText);
    utterance.rate = 1.05;
    utterance.pitch = 1.15; // Slightly elevated pitch for Stark's Karen assistant

    // Try finding an English female voice
    const voices = window.speechSynthesis.getVoices();
    const karenVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Samantha') || v.name.includes('Karen') || v.name.includes('Female') || v.name.includes('Google UK English Female')));
    if (karenVoice) {
      utterance.voice = karenVoice;
    }

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
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
          dispatched_unit: unit || 'Spider-Man (Web Strike)'
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
    if (priority >= 0.85) return 'bg-red-500/20 text-red-400 border-red-500/50 spidey-glow-red';
    if (priority >= 0.70) return 'bg-orange-500/20 text-orange-400 border-orange-500/40';
    if (priority >= 0.50) return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
    return 'bg-slate-800 text-slate-400 border-slate-700';
  };

  return (
    <div className="min-h-screen bg-[#070a14] text-slate-100 flex flex-col font-sans selection:bg-red-500 selection:text-white">
      {/* Stark OS Top Header */}
      <header className="border-b border-red-950/60 bg-[#0a0f1e]/90 backdrop-blur sticky top-0 z-30 px-6 py-3 flex items-center justify-between shadow-xl shadow-black/60">
        <div className="flex items-center space-x-3.5">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-red-600 to-red-500 flex items-center justify-center shadow-lg shadow-red-950 border border-red-400/50 spidey-glow-red">
              <SpiderIcon className="w-6 h-6 text-white" />
            </div>
            <span className="absolute -bottom-1 -right-1 w-3 h-3 rounded-full bg-emerald-400 border-2 border-[#0a0f1e] animate-ping"></span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-black tracking-wider text-white m-0 uppercase font-mono">
                Karen's Ear
              </h1>
              <span className="text-[10px] px-2 py-0.5 rounded bg-red-950/80 text-red-300 border border-red-600/40 font-mono tracking-widest uppercase">
                STARK SUIT OS // PROTOCOL 2.4
              </span>
            </div>
            <p className="text-xs text-slate-400 m-0 flex items-center space-x-1.5">
              <span>Peter Parker Tactical Triage & Manhattan Crisis Intercept</span>
              <span className="text-red-400">•</span>
              <span className="text-red-400 font-mono text-[11px]">Web Fluid: 96%</span>
            </p>
          </div>
        </div>

        {/* Header Right Actions */}
        <div className="flex items-center space-x-2.5">
          {/* Karen Voice Readout */}
          <button
            onClick={speakKarenDirective}
            className={`flex items-center space-x-2 text-xs font-semibold px-3.5 py-2 rounded-lg border transition cursor-pointer shadow-lg ${
              isSpeaking
                ? 'bg-amber-600 hover:bg-amber-500 text-white border-amber-400 animate-pulse'
                : 'bg-red-950/50 hover:bg-red-900/60 text-red-200 border-red-700/60'
            }`}
            title="Read out primary emergency target"
          >
            {isSpeaking ? <VolumeX className="w-4 h-4 text-white" /> : <Volume2 className="w-4 h-4 text-red-400" />}
            <span className="font-mono uppercase">{isSpeaking ? 'Mute Karen' : "Karen's Voice Briefing"}</span>
          </button>

          {/* Simulate Call Button */}
          <button
            onClick={() => setShowSimulateModal(true)}
            className="flex items-center space-x-1.5 text-xs font-bold bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white px-3.5 py-2 rounded-lg transition shadow-lg shadow-red-950/60 border border-red-500/40 cursor-pointer"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Simulate 911 Call</span>
          </button>

          <button
            onClick={handleResetData}
            title="Reset to sample dataset"
            className="flex items-center space-x-1 text-xs text-slate-400 hover:text-white bg-slate-900 hover:bg-slate-800 px-2.5 py-2 rounded-lg border border-slate-800 transition cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Reset</span>
          </button>

          <button
            onClick={fetchData}
            title="Refresh feed"
            className="p-2 text-slate-400 hover:text-white bg-slate-900 hover:bg-slate-800 rounded-lg border border-slate-800 transition cursor-pointer"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* "WHERE TO SWING FIRST" — Karen's Primary Hero Directive Banner */}
      {topReport && (
        <div className="bg-gradient-to-r from-red-950/90 via-[#130b1c]/90 to-blue-950/80 border-b border-red-600/40 px-6 py-3.5 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-full bg-gradient-to-l from-red-600/10 to-transparent pointer-events-none"></div>

          <div className="flex items-start md:items-center space-x-3.5 z-10">
            <div className="w-10 h-10 rounded-xl bg-red-600/30 border border-red-500 flex items-center justify-center shrink-0 spidey-glow-red animate-pulse">
              <Target className="w-5 h-5 text-red-400" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-[10px] font-black uppercase font-mono px-2 py-0.5 rounded bg-red-600 text-white tracking-widest">
                  WHERE TO SWING FIRST
                </span>
                <span className="text-xs font-mono font-bold text-red-300">
                  ETA: 45 SECONDS (1.2 km SW from Midtown)
                </span>
              </div>
              <p className="text-sm font-semibold text-white mt-0.5 m-0 leading-tight">
                🎯 Primary Target: <span className="text-red-400 uppercase">{topReport.location || 'Manhattan Sector'}</span> — {topReport.text}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3 shrink-0 z-10 w-full md:w-auto justify-end">
            <span className="text-xs font-mono text-slate-300 bg-black/40 px-3 py-1.5 rounded-lg border border-red-500/30">
              PRIORITY: <strong className="text-red-400 font-bold">{(topReport.priority * 100).toFixed(0)}%</strong>
            </span>
            <button
              onClick={() => handleDispatchAction(topReport.report_id, 'dispatched', 'Spider-Man (Web Strike)')}
              disabled={topReport.dispatch_status === 'dispatched'}
              className={`text-xs font-bold px-4 py-2 rounded-lg flex items-center space-x-1.5 transition cursor-pointer shadow-lg ${
                topReport.dispatch_status === 'dispatched'
                  ? 'bg-emerald-950 text-emerald-400 border border-emerald-600 cursor-default'
                  : 'bg-red-600 hover:bg-red-500 text-white shadow-red-950/60 border border-red-400'
              }`}
            >
              <SpiderIcon className="w-4 h-4 text-white" />
              <span>{topReport.dispatch_status === 'dispatched' ? 'Spider-Man En Route' : 'Swing To Location'}</span>
            </button>
          </div>
        </div>
      )}

      {/* Moving Hazard Ticker ("The Lizard-Thing Tracker") */}
      <div className="bg-[#0b1021] border-b border-slate-800/80 px-6 py-2 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
          <span className="font-mono text-amber-400 font-bold uppercase tracking-wider">
            ⚠️ MOVING THREAT VECTOR:
          </span>
          <span className="text-slate-300">
            Reptilian bio-entity ("The Lizard") spotted moving <strong>South towards Downtown Manhattan</strong> along 7th Ave (~35 mph).
          </span>
        </div>
        <span className="hidden lg:inline text-slate-500 font-mono text-[11px]">
          Threat Level: OMEGA • NYPD Perimeter Deployed
        </span>
      </div>

      {/* KPI Stats Bar */}
      <div className="px-6 py-3.5 grid grid-cols-2 md:grid-cols-4 gap-3.5 bg-[#080d1c] border-b border-slate-800/80">
        <div className="bg-[#0e1428] p-3 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider font-mono">Active Incidents</p>
            <h3 className="text-xl font-extrabold text-white mt-0.5">{stats ? stats.total_reports : '--'}</h3>
          </div>
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <Layers className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-[#0e1428] p-3 rounded-xl border border-red-950 flex items-center justify-between spidey-glow-red">
          <div>
            <p className="text-[11px] font-semibold text-red-400 uppercase tracking-wider font-mono">Critical Crises</p>
            <h3 className="text-xl font-extrabold text-red-400 mt-0.5">{stats ? stats.critical_count : '--'}</h3>
          </div>
          <div className="w-8 h-8 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400">
            <AlertOctagon className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-[#0e1428] p-3 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-[11px] font-semibold text-amber-400 uppercase tracking-wider font-mono">Pending Triage</p>
            <h3 className="text-xl font-extrabold text-amber-400 mt-0.5">{stats ? stats.pending_dispatch : '--'}</h3>
          </div>
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <SpiderIcon className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-[#0e1428] p-3 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider font-mono">Avg Urgency</p>
            <h3 className="text-xl font-extrabold text-emerald-400 mt-0.5">{stats ? (stats.average_priority * 100).toFixed(0) + '%' : '--'}</h3>
          </div>
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <TrendingUp className="w-4 h-4" />
          </div>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="flex-1 px-6 py-5 flex flex-col lg:flex-row gap-6 overflow-hidden">
        {/* Left Column: Triage Queue & Search */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Controls Bar */}
          <div className="bg-[#0e1428] p-3 rounded-xl border border-slate-800 mb-3 flex flex-wrap gap-2.5 items-center justify-between">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search emergency chatter, locations, incidents..."
                className="w-full bg-[#080d1c] border border-slate-700/80 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-red-500 font-mono"
              />
            </div>

            <div className="flex items-center space-x-2">
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="bg-[#080d1c] border border-slate-700 text-xs rounded-lg px-2.5 py-1.5 text-slate-300 focus:outline-none focus:border-red-500 font-mono"
              >
                <option value="all">All Incidents</option>
                <option value="fire">Fire</option>
                <option value="explosion">Explosion</option>
                <option value="accident">Accident</option>
                <option value="collapse">Collapse</option>
                <option value="flood">Flood</option>
                <option value="medical">Medical</option>
                <option value="unknown">Unknown</option>
              </select>

              <select
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
                className="bg-[#080d1c] border border-slate-700 text-xs rounded-lg px-2.5 py-1.5 text-slate-300 focus:outline-none focus:border-red-500 font-mono"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
              </select>
            </div>
          </div>

          {/* Queue Subheader */}
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2 px-1 font-mono">
            <span>TRIAGE STREAM // AUTO-RANKED BY LIFE THREAT</span>
            <span>{filteredReports.length} Active Calls</span>
          </div>

          {/* Emergency Cards List */}
          <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 max-h-[calc(100vh-360px)]">
            {loading ? (
              <div className="text-center py-12 text-slate-500 text-sm font-mono">Scanning New York emergency frequencies...</div>
            ) : filteredReports.length === 0 ? (
              <div className="text-center py-12 text-slate-500 bg-[#0e1428]/50 rounded-xl border border-slate-800 font-mono">
                No active signals matching filter parameters.
              </div>
            ) : (
              filteredReports.map((report) => {
                const isSelected = selectedReport && selectedReport.report_id === report.report_id;
                const isSpiderManNeeded = report.severity === 'critical' || report.incident_type === 'explosion' || report.incident_type === 'collapse';

                return (
                  <div
                    key={report.report_id}
                    onClick={() => selectReport(report)}
                    className={`p-3.5 rounded-xl border transition cursor-pointer text-left ${
                      isSelected
                        ? 'bg-[#141b34] border-red-500 shadow-xl shadow-red-950/40 ring-1 ring-red-500/40'
                        : 'bg-[#0d1326] border-slate-800/90 hover:border-slate-700 hover:bg-[#101730]'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-xs font-bold text-slate-400 bg-black/40 px-2 py-0.5 rounded border border-slate-800">
                          {report.report_id}
                        </span>
                        <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-200 capitalize">
                          {INCIDENT_ICONS[report.incident_type] || INCIDENT_ICONS.unknown}
                          <span>{report.incident_type.replace('_', ' ')}</span>
                        </div>
                        {isSpiderManNeeded ? (
                          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-red-950 text-red-300 border border-red-700 font-mono">
                            🕸️ Spider-Man Needed
                          </span>
                        ) : (
                          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                            🚒 Delegate to Civil
                          </span>
                        )}
                      </div>

                      {/* Priority Score Meter */}
                      <div className={`px-2.5 py-1 rounded-lg border font-mono font-bold text-xs flex items-center space-x-1 ${getPriorityBadgeClass(report.priority)}`}>
                        <Zap className="w-3.5 h-3.5" />
                        <span>{(report.priority * 100).toFixed(0)}% PRIORITY</span>
                      </div>
                    </div>

                    <p className="text-sm text-slate-200 mt-2 font-normal leading-relaxed">
                      "{report.text}"
                    </p>

                    <div className="mt-3 pt-2.5 border-t border-slate-800/70 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2 font-mono">
                      <div className="flex items-center space-x-3">
                        <span className="flex items-center space-x-1 text-slate-200">
                          <MapPin className="w-3.5 h-3.5 text-red-400" />
                          <span>{report.location || 'Location unverified'}</span>
                        </span>
                        <span className="text-slate-600">•</span>
                        <span>Credibility: <strong className="text-slate-300">{(report.credibility * 100).toFixed(0)}%</strong></span>
                      </div>

                      <div className="flex items-center space-x-2">
                        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded uppercase ${
                          report.dispatch_status === 'dispatched'
                            ? 'bg-blue-950 text-blue-300 border border-blue-700'
                            : report.dispatch_status === 'resolved'
                            ? 'bg-emerald-950 text-emerald-300 border border-emerald-700'
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

        {/* Right Column: Holographic NYC Map & AI Inspector */}
        <div className="w-full lg:w-[420px] flex flex-col space-y-4">
          {/* Holographic Tactical Manhattan Radar Map */}
          <div className="bg-[#0e1428] p-4 rounded-xl border border-slate-800 relative overflow-hidden">
            <div className="flex items-center justify-between pb-2.5 border-b border-slate-800 mb-2.5">
              <div className="flex items-center space-x-2">
                <Compass className="w-4 h-4 text-red-400" />
                <h3 className="text-xs font-bold text-white m-0 uppercase font-mono tracking-wider">
                  Manhattan Tactical Grid // Radar Scan
                </h3>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/40">
                GPS LIVE
              </span>
            </div>

            {/* Tactical Grid Visualization */}
            <div className="relative w-full h-52 bg-[#060913] rounded-lg border border-slate-800/80 overflow-hidden flex items-center justify-center">
              {/* Grid lines */}
              <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f293d_1px,transparent_1px),linear-gradient(to_bottom,#1f293d_1px,transparent_1px)] bg-[size:1.5rem_1.5rem] opacity-25"></div>

              {/* Central Park / River Contours representation */}
              <div className="absolute left-2 top-4 bottom-4 w-4 bg-blue-950/40 rounded-full border border-blue-900/30"></div>
              <div className="absolute right-2 top-4 bottom-4 w-4 bg-blue-950/40 rounded-full border border-blue-900/30"></div>
              <div className="absolute left-1/2 -translate-x-1/2 top-4 w-16 h-20 bg-emerald-950/30 rounded border border-emerald-900/40 flex items-center justify-center text-[9px] text-emerald-500/60 font-mono">
                Central Pk
              </div>

              {/* Spider-Man Current Position */}
              <div className="absolute left-[48%] top-[50%] -translate-x-1/2 -translate-y-1/2 z-20 flex flex-col items-center">
                <div className="w-7 h-7 rounded-full bg-red-600 border border-white flex items-center justify-center spidey-glow-red animate-bounce">
                  <SpiderIcon className="w-4 h-4 text-white" />
                </div>
                <span className="text-[9px] font-mono font-bold text-red-400 bg-black/80 px-1 rounded mt-0.5">
                  Peter (Rooftop)
                </span>
              </div>

              {/* Emergency Map Pins */}
              {reports.map((r, i) => {
                const locInfo = r.location && NYC_LOCATIONS[r.location]
                  ? NYC_LOCATIONS[r.location]
                  : { x: 30 + (i * 10) % 50, y: 30 + (i * 12) % 50, label: r.location || 'Unknown' };

                const isSelected = selectedReport && selectedReport.report_id === r.report_id;
                const isCrit = r.severity === 'critical';

                return (
                  <div
                    key={r.report_id}
                    onClick={() => selectReport(r)}
                    style={{ left: `${locInfo.x}%`, top: `${locInfo.y}%` }}
                    className="absolute -translate-x-1/2 -translate-y-1/2 z-10 cursor-pointer group"
                    title={`${r.report_id}: ${r.text}`}
                  >
                    <div className={`w-3.5 h-3.5 rounded-full border flex items-center justify-center transition-all ${
                      isSelected
                        ? 'bg-red-500 border-white scale-150 spidey-glow-red'
                        : isCrit
                        ? 'bg-red-600 border-red-300 animate-pulse'
                        : 'bg-amber-500 border-amber-300'
                    }`}></div>

                    {isSelected && (
                      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-black/90 text-white text-[10px] px-2 py-0.5 rounded whitespace-nowrap border border-red-500 font-mono">
                        {r.location || r.report_id} ({(r.priority * 100).toFixed(0)}%)
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Moving Lizard Hazard Arrow */}
              <div className="absolute left-[38%] top-[35%] w-24 h-16 pointer-events-none z-10 flex flex-col items-center">
                <div className="text-[9px] font-mono text-amber-400 bg-black/80 px-1 rounded border border-amber-500/40">
                  🦎 Lizard Vector ↘
                </div>
                <div className="w-16 h-0.5 bg-amber-400 border-b border-dashed border-amber-300 mt-1 rotate-45"></div>
              </div>
            </div>

            <p className="text-[10px] text-slate-500 mt-2 font-mono text-center">
              Click pins to inspect incident. Red = Critical • Yellow = Moderate
            </p>
          </div>

          {/* AI Explainability Inspector */}
          <div className="bg-[#0e1428] p-4 rounded-xl border border-slate-800 flex-1 flex flex-col">
            <div className="flex items-center justify-between pb-2.5 border-b border-slate-800 mb-3">
              <div className="flex items-center space-x-2">
                <Cpu className="w-4 h-4 text-red-400" />
                <h3 className="text-xs font-bold text-white m-0 uppercase font-mono tracking-wider">
                  Karen's Neural Triage Explainability
                </h3>
              </div>
              <span className="text-[10px] bg-red-950 text-red-300 border border-red-800 px-2 py-0.5 rounded font-mono">
                WEIGHTED FORMULA
              </span>
            </div>

            {explanation ? (
              <div className="space-y-3 text-xs font-mono">
                <div className="p-3 rounded-lg bg-[#070b16] border border-slate-800">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-slate-400 text-[11px]">Karen's Recommendation</span>
                    <span className="font-bold text-red-400">{explanation.recommendation}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400 text-[11px]">Composite Priority</span>
                    <span className="font-bold text-white text-base">{(explanation.final_priority * 100).toFixed(0)}%</span>
                  </div>
                </div>

                {/* Breakdown Bars */}
                <div className="space-y-2 text-[11px]">
                  <div>
                    <div className="flex justify-between text-slate-300 mb-1">
                      <span>Severity ({explanation.components.severity.level})</span>
                      <span className="text-slate-400">{(explanation.components.severity.contribution * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-1.5">
                      <div
                        className="bg-red-500 h-1.5 rounded-full"
                        style={{ width: `${(explanation.components.severity.contribution / 0.45) * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-300 mb-1">
                      <span>Actionability ({explanation.components.actionability.level})</span>
                      <span className="text-slate-400">{(explanation.components.actionability.contribution * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-1.5">
                      <div
                        className="bg-orange-400 h-1.5 rounded-full"
                        style={{ width: `${(explanation.components.actionability.contribution / 0.25) * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-300 mb-1">
                      <span>Credibility Assessment</span>
                      <span className="text-slate-400">{(explanation.components.credibility.contribution * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-1.5">
                      <div
                        className="bg-blue-400 h-1.5 rounded-full"
                        style={{ width: `${(explanation.components.credibility.contribution / 0.22) * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-300 mb-1">
                      <span>Corroboration Bonus</span>
                      <span className="text-slate-400">{(explanation.components.corroboration.contribution * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-1.5">
                      <div
                        className="bg-emerald-400 h-1.5 rounded-full"
                        style={{ width: `${(explanation.components.corroboration.contribution / 0.08) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                {/* Dispatch Buttons */}
                <div className="pt-2 border-t border-slate-800 flex gap-2">
                  <button
                    onClick={() => handleDispatchAction(selectedReport.report_id, 'dispatched', 'Spider-Man (Web Strike)')}
                    className="flex-1 py-2 px-3 bg-red-600 hover:bg-red-500 text-white rounded-lg font-bold text-xs flex items-center justify-center space-x-1.5 transition cursor-pointer shadow-lg shadow-red-950"
                  >
                    <SpiderIcon className="w-3.5 h-3.5" />
                    <span>Deploy Spider-Man</span>
                  </button>

                  <button
                    onClick={() => handleDispatchAction(selectedReport.report_id, 'resolved')}
                    className="py-2 px-3 bg-emerald-800 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold flex items-center justify-center space-x-1 transition cursor-pointer"
                  >
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>Contained</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-slate-500 text-xs font-mono">
                Select an incident to view neural triage breakdown.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Simulate Incident Modal */}
      {showSimulateModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-[#0e1428] border border-red-600/40 rounded-2xl max-w-lg w-full p-5 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <SpiderIcon className="w-5 h-5 text-red-500" />
                <h3 className="text-base font-bold text-white m-0 font-mono uppercase">
                  Simulate New York 911 / Police Scanner Feed
                </h3>
              </div>
              <button
                onClick={() => setShowSimulateModal(false)}
                className="text-slate-400 hover:text-white text-lg font-bold px-2 cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div>
              <p className="text-xs text-slate-400 mb-2 font-mono font-medium">Quick Emergency Scenarios (Click to test Karen's AI):</p>
              <div className="grid grid-cols-1 gap-2">
                {PRESET_SIMULATIONS.map((preset, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSimulateSubmit(preset.text)}
                    disabled={simSubmitting}
                    className="text-left text-xs p-2.5 rounded-lg bg-[#070b16] hover:bg-slate-800/80 border border-slate-800 hover:border-red-500/50 transition cursor-pointer flex flex-col space-y-0.5"
                  >
                    <span className="font-bold text-red-300 font-mono text-[11px]">{preset.title}</span>
                    <span className="text-[11px] text-slate-300 line-clamp-1">"{preset.text}"</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800">
              <label className="text-xs font-semibold text-slate-300 block mb-1.5 font-mono">
                Or Transcribe Panicked Radio / Civilian Text:
              </label>
              <textarea
                rows={3}
                value={simText}
                onChange={(e) => setSimText(e.target.value)}
                placeholder="e.g. Someone trapped under heavy steel girder on 34th St, need Spider-Man immediately..."
                className="w-full bg-[#070b16] border border-slate-700 rounded-xl p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-red-500 font-mono"
              />
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setShowSimulateModal(false)}
                className="px-4 py-2 rounded-lg text-xs text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 transition cursor-pointer font-mono"
              >
                Cancel
              </button>
              <button
                onClick={() => handleSimulateSubmit()}
                disabled={simSubmitting || !simText.trim()}
                className={`px-4 py-2 rounded-lg text-xs font-bold text-white flex items-center space-x-1.5 transition cursor-pointer font-mono ${
                  simSubmitting || !simText.trim()
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                    : 'bg-red-600 hover:bg-red-500 shadow-lg shadow-red-950/60'
                }`}
              >
                <Send className="w-3.5 h-3.5" />
                <span>{simSubmitting ? 'Karen Processing...' : 'Transmit Signal'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

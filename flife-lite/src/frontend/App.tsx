import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import {
  Activity,
  BarChart3,
  BookOpen,
  Database,
  FileInput,
  FileText,
  Gauge,
  KeyRound,
  Layers3,
  Moon,
  Play,
  Save,
  Settings,
  Sun,
} from "lucide-react";
import { defaultMaterials } from "./materials";
import { StartupSplash } from "./components/StartupSplash";
import { activateLicense, getLicenseStatus, isDesktopRuntime, runAnalysis } from "./services";
import type { AnalysisResult, AnalysisSettings, LicenseStatus, Material } from "./types";

const ResultsCharts = lazy(() => import("./components/ResultsCharts").then((module) => ({ default: module.ResultsCharts })));

const navItems = [
  { id: "home", label: "Home", icon: Gauge },
  { id: "workspace", label: "Workspace", icon: Layers3 },
  { id: "import", label: "Data Import", icon: FileInput },
  { id: "materials", label: "Materials", icon: Database },
  { id: "analysis", label: "Analysis", icon: Settings },
  { id: "results", label: "Results", icon: BarChart3 },
  { id: "reports", label: "Reports", icon: FileText },
  { id: "license", label: "License", icon: KeyRound },
] as const;

type Page = (typeof navItems)[number]["id"];

const initialSettings: AnalysisSettings = {
  method: "dirlik",
  meanStressCorrection: "goodman",
  cycleCounting: "four-point",
  safetyFactor: 1.2,
  damageModel: "miners-rule",
};

export function App() {
  const [page, setPage] = useState<Page>("home");
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [license, setLicense] = useState<LicenseStatus | null>(null);
  const [materials, setMaterials] = useState<Material[]>(defaultMaterials);
  const [selectedMaterialId, setSelectedMaterialId] = useState(defaultMaterials[0].id);
  const [settings, setSettings] = useState<AnalysisSettings>(initialSettings);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [email, setEmail] = useState("");
  const [licenseKey, setLicenseKey] = useState("");
  const [busy, setBusy] = useState(false);
  const [boot, setBoot] = useState({ progress: 8, step: "Starting diagnostics", ready: false });

  const selectedMaterial = useMemo(
    () => materials.find((material) => material.id === selectedMaterialId) ?? materials[0],
    [materials, selectedMaterialId],
  );

  useEffect(() => {
    const timers = [
      window.setTimeout(() => setBoot({ progress: 32, step: "Checking local runtime", ready: false }), 120),
      window.setTimeout(() => setBoot({ progress: 58, step: "Validating license state", ready: false }), 280),
      window.setTimeout(() => setBoot({ progress: 84, step: "Restoring workspace", ready: false }), 460),
    ];
    getLicenseStatus()
      .then(setLicense)
      .catch(() => {
        setLicense({ state: "unactivated", type: "trial", daysRemaining: 0, offlineUntil: "" });
      })
      .finally(() => {
        window.setTimeout(() => setBoot({ progress: 100, step: "Ready", ready: true }), 650);
      });
    return () => timers.forEach(window.clearTimeout);
  }, []);

  const executeAnalysis = async () => {
    setBusy(true);
    try {
      setResult(await runAnalysis(settings, selectedMaterial));
      setPage("results");
    } finally {
      setBusy(false);
    }
  };

  const submitActivation = async () => {
    setBusy(true);
    try {
      setLicense(await activateLicense(email, licenseKey));
    } finally {
      setBusy(false);
    }
  };

  const updateMaterial = (field: keyof Material, value: string) => {
    setMaterials((items) =>
      items.map((item) =>
        item.id === selectedMaterial.id
          ? { ...item, [field]: typeof item[field] === "number" ? Number(value) : value }
          : item,
      ),
    );
  };

  if (!boot.ready) {
    return <StartupSplash progress={boot.progress} step={boot.step} />;
  }

  return (
    <main className={`app ${theme}`}>
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">FL</div>
          <div>
            <strong>FLIFE Lite</strong>
            <span>Durability Workbench</span>
          </div>
        </div>
        <nav>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button className={page === item.id ? "active" : ""} key={item.id} onClick={() => setPage(item.id)}>
                <Icon size={18} />
                {item.label}
              </button>
            );
          })}
        </nav>
        <button className="theme-toggle" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          {theme === "dark" ? "Light" : "Dark"}
        </button>
      </aside>

      <section className="workspace">
        <div className="toolbar">
          <button className="tool-button"><Save size={17} /> Save</button>
          <button className="tool-button"><FileInput size={17} /> Import</button>
          <button className="tool-button" onClick={executeAnalysis} disabled={busy}><Activity size={17} /> Solve</button>
          <span className="toolbar-spacer" />
          <span className={`license-badge ${license?.state ?? "checking"}`}>{license?.state ?? "checking"}</span>
        </div>
        <header className="topbar">
          <div>
            <span className="eyebrow">Offline-first fatigue prediction</span>
            <h1>{navItems.find((item) => item.id === page)?.label}</h1>
          </div>
          <div className="runtime">
            <span>{isDesktopRuntime() ? "Desktop runtime" : "Browser preview"}</span>
            <strong>{license?.state ?? "checking"}</strong>
          </div>
        </header>

        {page === "home" && (
          <div className="grid home-grid">
            <section className="hero-panel">
              <div>
                <span className="eyebrow">Client demo build</span>
                <h2>Fatigue life prediction for engineering teams</h2>
                <p>Import stress histories, select materials, configure spectral or rainflow methods, and generate traceable durability reports.</p>
                <button className="primary" onClick={executeAnalysis} disabled={busy}>
                  <Play size={18} /> Run baseline analysis
                </button>
              </div>
              <div className="contour" aria-hidden="true">
                {Array.from({ length: 64 }, (_, index) => <span key={index} />)}
              </div>
            </section>
            <Metric label="License days" value={`${license?.daysRemaining ?? 0}`} />
            <Metric label="Last life" value={result ? `${result.lifeSeconds.toFixed(0)} s` : "Not run"} />
            <Metric label="Material" value={selectedMaterial.name} />
            <Metric label="Usage" value="12 analyses" />
          </div>
        )}

        {page === "workspace" && (
          <Panel title="Project Workspace">
            <div className="project-layout">
              {["Create", "Open", "Save", "Duplicate"].map((action) => (
                <button className="tool-button" key={action}>
                  <Save size={17} /> {action} project
                </button>
              ))}
            </div>
            <pre className="tree">{`project_name/
  input/
  results/
  reports/
  settings/`}</pre>
          </Panel>
        )}

        {page === "import" && (
          <Panel title="Data Import">
            <div className="dropzone">
              <FileInput size={32} />
              <strong>Drop CSV, XLSX, or TXT fatigue data</strong>
              <span>Map stress, time, PSD, or cycle columns before analysis.</span>
            </div>
            <div className="table-preview">
              <div>time_s</div><div>stress_mpa</div><div>load_case</div><div>unit</div>
              <div>0.000</div><div>12.4</div><div>baseline</div><div>MPa</div>
              <div>0.005</div><div>38.7</div><div>baseline</div><div>MPa</div>
              <div>0.010</div><div>64.1</div><div>baseline</div><div>MPa</div>
            </div>
          </Panel>
        )}

        {page === "materials" && (
          <Panel title="Material Database">
            <div className="split">
              <div className="material-list">
                {materials.map((material) => (
                  <button key={material.id} className={material.id === selectedMaterialId ? "selected" : ""} onClick={() => setSelectedMaterialId(material.id)}>
                    <strong>{material.name}</strong>
                    <span>{material.family}</span>
                  </button>
                ))}
              </div>
              <div className="form-grid">
                <Field label="Name" value={selectedMaterial.name} onChange={(value) => updateMaterial("name", value)} />
                <Field label="Family" value={selectedMaterial.family} onChange={(value) => updateMaterial("family", value)} />
                <Field label="UTS MPa" value={selectedMaterial.utsMpa} onChange={(value) => updateMaterial("utsMpa", value)} />
                <Field label="Yield MPa" value={selectedMaterial.yieldMpa} onChange={(value) => updateMaterial("yieldMpa", value)} />
                <Field label="SN intercept" value={selectedMaterial.snIntercept} onChange={(value) => updateMaterial("snIntercept", value)} />
                <Field label="SN slope" value={selectedMaterial.snSlope} onChange={(value) => updateMaterial("snSlope", value)} />
              </div>
            </div>
          </Panel>
        )}

        {page === "analysis" && (
          <Panel title="Analysis Setup">
            <div className="form-grid">
              <Select label="Fatigue method" value={settings.method} options={["dirlik", "rainflow", "narrowband", "tovo-benasciutti"]} onChange={(method) => setSettings({ ...settings, method: method as AnalysisSettings["method"] })} />
              <Select label="Mean stress" value={settings.meanStressCorrection} options={["goodman", "none"]} onChange={(meanStressCorrection) => setSettings({ ...settings, meanStressCorrection: meanStressCorrection as AnalysisSettings["meanStressCorrection"] })} />
              <Select label="Cycle counting" value={settings.cycleCounting} options={["four-point", "three-point"]} onChange={(cycleCounting) => setSettings({ ...settings, cycleCounting: cycleCounting as AnalysisSettings["cycleCounting"] })} />
              <Field label="Safety factor" value={settings.safetyFactor} onChange={(safetyFactor) => setSettings({ ...settings, safetyFactor: Number(safetyFactor) })} />
            </div>
            <button className="primary" onClick={executeAnalysis} disabled={busy}>
              <Activity size={18} /> {busy ? "Running" : "Run fatigue prediction"}
            </button>
          </Panel>
        )}

        {page === "results" && (
          <Panel title="Results Dashboard">
            {result ? (
              <>
                <div className="metrics-row">
                  <Metric label="Predicted life" value={`${result.lifeSeconds.toFixed(1)} s`} />
                  <Metric label="Damage/sec" value={result.damagePerSecond.toExponential(2)} />
                  <Metric label="Peak stress" value={`${result.peakStressMpa.toFixed(1)} MPa`} />
                </div>
                <Suspense fallback={<div className="chart-skeleton">Loading engineering charts</div>}>
                  <ResultsCharts result={result} theme={theme} />
                </Suspense>
              </>
            ) : (
              <button className="primary" onClick={executeAnalysis}>Run analysis</button>
            )}
          </Panel>
        )}

        {page === "reports" && (
          <Panel title="Report Generator">
            <div className="report-sheet">
              <BookOpen size={28} />
              <h3>Engineering report package</h3>
              <p>Includes project metadata, material properties, analysis settings, graph exports, predicted life, and damage accumulation summary.</p>
              <button className="tool-button"><FileText size={17} /> Generate PDF</button>
            </div>
          </Panel>
        )}

        {page === "license" && (
          <Panel title="Activation">
            <div className="activation">
              <Metric label="Status" value={license?.state ?? "checking"} />
              <Metric label="Offline until" value={license?.offlineUntil ? new Date(license.offlineUntil).toLocaleDateString() : "Unavailable"} />
              <Field label="Email" value={email} onChange={setEmail} />
              <Field label="License key" value={licenseKey} onChange={setLicenseKey} />
              <button className="primary" onClick={submitActivation} disabled={busy || !email || !licenseKey}>
                <KeyRound size={18} /> Activate
              </button>
            </div>
          </Panel>
        )}
      </section>
      <footer className="statusbar">
        <span>Project: unsaved.flifeproj</span>
        <span>Solver: {settings.method}</span>
        <span>Material: {selectedMaterial.name}</span>
        <span>{busy ? "Running analysis" : "Ready"}</span>
      </footer>
    </main>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="panel">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Field({ label, value, onChange }: { label: string; value: string | number; onChange: (value: string) => void }) {
  return (
    <label className="field">
      <span>{label}</span>
      <input value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function Select({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (value: string) => void }) {
  return (
    <label className="field">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => <option key={option}>{option}</option>)}
      </select>
    </label>
  );
}

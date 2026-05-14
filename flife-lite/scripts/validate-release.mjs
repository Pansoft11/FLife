import { existsSync, mkdirSync, writeFileSync } from "node:fs";

const releaseRoot = process.env.FLIFE_RELEASE_ROOT ?? "build/release";
const checks = [
  ["Installer artifact", `${releaseRoot}/installer/FLIFE-Lite-Setup.exe`],
  ["Portable ZIP", `${releaseRoot}/portable/FLIFE-Lite-Portable.zip`],
  ["Checksums", `${releaseRoot}/checksums/SHA256SUMS.txt`],
  ["Release manifest", `${releaseRoot}/manifests/release-manifest.json`],
  ["Bundle report", `${releaseRoot}/reports/bundle-report.json`],
];

const rows = checks.map(([name, path]) => ({ name, path, status: existsSync(path) ? "PASS" : "PENDING" }));
const now = new Date().toISOString();
const body = [
  "# FLIFE Lite RC1 Validation Report",
  "",
  `Generated: ${now}`,
  "",
  "| Check | Status | Path |",
  "| --- | --- | --- |",
  ...rows.map((row) => `| ${row.name} | ${row.status} | \`${row.path}\` |`),
  "",
  "Manual validation checklist:",
  "",
  "- Installer launches and installs to selected directory.",
  "- Desktop and Start menu shortcuts are created.",
  "- Portable ZIP launches from a writable folder or USB drive.",
  "- Activation succeeds against licensing server.",
  "- Offline mode remains valid through grace period.",
  "- Report generation creates HTML and DOCX-ready output.",
  "- Recovery snapshots are written after workspace changes.",
  "- Updater manifest parses and signature placeholder is replaced for production.",
  "- Crash dumps are written to `%LOCALAPPDATA%/FLIFE/crash-dumps/`.",
].join("\n");

mkdirSync(releaseRoot, { recursive: true });
writeFileSync(`${releaseRoot}/RC1-validation-report.md`, body);
console.log("RC1 validation report generated.");

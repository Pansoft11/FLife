import { existsSync, mkdirSync, writeFileSync } from "node:fs";

const checks = [
  ["Installer artifact", "release/installer/FLIFE-Lite-Setup.exe"],
  ["Portable ZIP", "release/portable/FLIFE-Lite-Portable.zip"],
  ["Checksums", "release/checksums/SHA256SUMS.txt"],
  ["Release manifest", "release/manifests/release-manifest.json"],
  ["Bundle report", "release/reports/bundle-report.json"],
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

mkdirSync("release", { recursive: true });
writeFileSync("release/RC1-validation-report.md", body);
console.log("RC1 validation report generated.");

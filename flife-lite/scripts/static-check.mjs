import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const roots = ["src/frontend", "src-tauri/src"];
const forbidden = [/eval\s*\(/, /innerHTML\s*=/, /dangerouslySetInnerHTML/];
const findings = [];

function walk(dir) {
  for (const entry of readdirSync(dir)) {
    const path = join(dir, entry);
    const stat = statSync(path);
    if (stat.isDirectory()) {
      walk(path);
    } else if (/\.(ts|tsx|rs)$/.test(entry)) {
      const source = readFileSync(path, "utf8");
      for (const pattern of forbidden) {
        if (pattern.test(source)) {
          findings.push(`${path}: forbidden pattern ${pattern}`);
        }
      }
    }
  }
}

for (const root of roots) {
  walk(root);
}

if (findings.length > 0) {
  console.error(findings.join("\n"));
  process.exit(1);
}

console.log("Static check passed.");

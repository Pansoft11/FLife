import { mkdirSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const dist = fileURLToPath(new URL("../dist", import.meta.url));
const files = [];

function walk(dir) {
  for (const entry of readdirSync(dir)) {
    const path = join(dir, entry);
    const stat = statSync(path);
    if (stat.isDirectory()) {
      walk(path);
    } else {
      files.push({ path: relative(dist, path).replaceAll("\\", "/"), bytes: stat.size });
    }
  }
}

walk(dist);
files.sort((a, b) => b.bytes - a.bytes);

const report = {
  generatedAt: new Date().toISOString(),
  totalBytes: files.reduce((sum, file) => sum + file.bytes, 0),
  files,
};

const buildDir = fileURLToPath(new URL("../build", import.meta.url));
mkdirSync(buildDir, { recursive: true });
writeFileSync(join(buildDir, "bundle-report.json"), JSON.stringify(report, null, 2));
console.log(`Bundle report written with ${files.length} files.`);

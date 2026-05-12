import type { AnalysisResult, AnalysisSettings, LicenseStatus, Material } from "./types";

type TauriInvoke = <T>(command: string, args?: Record<string, unknown>) => Promise<T>;

const invokeFromWindow = (): TauriInvoke | undefined => {
  const candidate = (window as unknown as { __TAURI__?: { core?: { invoke?: TauriInvoke } } }).__TAURI__;
  return candidate?.core?.invoke;
};

export const isDesktopRuntime = () => Boolean(invokeFromWindow());

export async function activateLicense(email: string, licenseKey: string): Promise<LicenseStatus> {
  const invoke = invokeFromWindow();
  if (invoke) return invoke("activate_license", { email, licenseKey });

  return {
    state: "trial",
    type: "trial",
    daysRemaining: 14,
    offlineUntil: new Date(Date.now() + 14 * 86400000).toISOString(),
    email,
  };
}

export async function getLicenseStatus(): Promise<LicenseStatus> {
  const invoke = invokeFromWindow();
  if (invoke) return invoke("license_status");

  return {
    state: "trial",
    type: "trial",
    daysRemaining: 14,
    offlineUntil: new Date(Date.now() + 14 * 86400000).toISOString(),
    email: "demo@flife.local",
  };
}

export async function runAnalysis(settings: AnalysisSettings, material: Material): Promise<AnalysisResult> {
  const invoke = invokeFromWindow();
  if (invoke) return invoke("run_analysis", { settings, material });

  const ranges = [18, 24, 32, 42, 58, 72, 88, 110];
  return {
    lifeSeconds: 1595.03,
    damagePerSecond: 1 / 1595.03,
    peakStressMpa: 142.4,
    rmsStressMpa: 64.1,
    cycles: ranges.map((range, index) => ({ range, mean: 8 + index * 2.5, count: 40 + index * 18 })),
    snCurve: Array.from({ length: 18 }, (_, index) => {
      const cycles = 10 ** (3 + index * 0.25);
      return { cycles, stress: Math.pow(material.snIntercept / cycles, 1 / material.snSlope) };
    }),
  };
}

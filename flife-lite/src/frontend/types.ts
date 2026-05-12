export type LicenseType = "trial" | "monthly" | "yearly" | "perpetual" | "enterprise";

export type LicenseStatus = {
  state: "active" | "trial" | "offline" | "expired" | "unactivated" | "suspended" | "revoked" | "offline_grace";
  type: LicenseType;
  daysRemaining: number;
  offlineUntil: string;
  email?: string;
};

export type Material = {
  id: string;
  name: string;
  family: string;
  utsMpa: number;
  yieldMpa: number;
  snIntercept: number;
  snSlope: number;
  fatigueStrengthCoefficient: number;
  fatigueDuctilityCoefficient: number;
};

export type AnalysisSettings = {
  method: "rainflow" | "dirlik" | "narrowband" | "tovo-benasciutti";
  meanStressCorrection: "none" | "goodman";
  cycleCounting: "four-point" | "three-point";
  safetyFactor: number;
  damageModel: "miners-rule";
};

export type AnalysisResult = {
  lifeSeconds: number;
  damagePerSecond: number;
  peakStressMpa: number;
  rmsStressMpa: number;
  cycles: Array<{ range: number; mean: number; count: number }>;
  snCurve: Array<{ cycles: number; stress: number }>;
};

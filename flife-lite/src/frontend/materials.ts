import type { Material } from "./types";

export const defaultMaterials: Material[] = [
  {
    id: "steel-42crmo4",
    name: "42CrMo4 Steel",
    family: "Steel",
    utsMpa: 1080,
    yieldMpa: 930,
    snIntercept: 1.8e19,
    snSlope: 6,
    fatigueStrengthCoefficient: 1450,
    fatigueDuctilityCoefficient: 0.42,
  },
  {
    id: "al-7075-t6",
    name: "Aluminum 7075-T6",
    family: "Aluminum",
    utsMpa: 572,
    yieldMpa: 503,
    snIntercept: 8.4e17,
    snSlope: 5.1,
    fatigueStrengthCoefficient: 920,
    fatigueDuctilityCoefficient: 0.21,
  },
  {
    id: "ti-6al-4v",
    name: "Ti-6Al-4V",
    family: "Titanium",
    utsMpa: 950,
    yieldMpa: 880,
    snIntercept: 2.2e18,
    snSlope: 5.6,
    fatigueStrengthCoefficient: 1380,
    fatigueDuctilityCoefficient: 0.26,
  },
];

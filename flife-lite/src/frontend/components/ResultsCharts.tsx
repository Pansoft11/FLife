import Plot from "react-plotly.js";
import type { AnalysisResult } from "../types";

type ResultsChartsProps = {
  result: AnalysisResult;
  theme: "dark" | "light";
};

export function ResultsCharts({ result, theme }: ResultsChartsProps) {
  return (
    <div className="charts">
      <Plot
        data={[
          {
            x: result.cycles.map((cycle) => cycle.range),
            y: result.cycles.map((cycle) => cycle.count),
            type: "bar",
            marker: { color: "#4fd1c5" },
          },
        ]}
        layout={chartLayout("Cycle histogram", theme, { xaxis: { title: "Range MPa" }, yaxis: { title: "Count" } })}
        config={{ displaylogo: false, responsive: true, toImageButtonOptions: { scale: 3 } }}
      />
      <Plot
        data={[
          {
            x: result.snCurve.map((point) => point.cycles),
            y: result.snCurve.map((point) => point.stress),
            mode: "lines",
            line: { color: "#ffb86b", width: 3 },
          },
        ]}
        layout={chartLayout("SN curve", theme, { xaxis: { type: "log", title: "Cycles" }, yaxis: { title: "Stress MPa" } })}
        config={{ displaylogo: false, responsive: true, toImageButtonOptions: { scale: 3 } }}
      />
      <Plot
        data={[
          {
            x: result.cycles.map((cycle) => cycle.range),
            y: cumulative(result.cycles.map((cycle) => cycle.count)),
            mode: "lines+markers",
            line: { color: "#2f80ed", width: 3 },
          },
        ]}
        layout={chartLayout("Cumulative damage proxy", theme, { xaxis: { title: "Range MPa" }, yaxis: { title: "Cumulative cycles" } })}
        config={{ displaylogo: false, responsive: true, toImageButtonOptions: { scale: 3 } }}
      />
    </div>
  );
}

function cumulative(values: number[]) {
  let total = 0;
  return values.map((value) => {
    total += value;
    return total;
  });
}

function chartLayout(title: string, theme: "dark" | "light", axes: Record<string, unknown>) {
  const paper = theme === "dark" ? "#111827" : "#ffffff";
  const font = theme === "dark" ? "#d7e1ea" : "#1d2733";
  return {
    title,
    autosize: true,
    paper_bgcolor: paper,
    plot_bgcolor: paper,
    font: { color: font },
    margin: { l: 56, r: 18, t: 46, b: 48 },
    ...axes,
  };
}

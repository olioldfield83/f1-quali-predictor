"use client";

import { useEffect, useMemo, useState } from "react";

type Race = {
  round: number;
  name: string;
  country: string;
  location: string;
  official_name?: string;
  date?: string;
};

type Prediction = {
  driver: string;
  team: string;
  predicted_position: number;
  score: number;
  driver_recent_avg_position: number | null;
  driver_long_avg_position?: number | null;
  team_recent_avg_position: number | null;
  team_long_avg_position?: number | null;
  teammate_gap?: number | null;
  momentum?: number | null;
  q3_rate: number | null;
  pole_probability: number;
  q3_probability: number;
  confidence: string;
};

type DriverExplanation = {
  driver: string;
  predicted_position: number;
  explanation: string;
};

type ExplainResponse = {
  prediction_model: string;
  ai_model: string;
  count: number;
  target?: {
    year: number;
    round: number;
  };
  explanation?: {
    summary: string;
    driver_explanations: DriverExplanation[];
  };
  predictions: Prediction[];
  cached?: boolean;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export default function Home() {
  const [data, setData] = useState<ExplainResponse | null>(null);
  const [races, setRaces] = useState<Race[]>([]);
  const [year, setYear] = useState("2026");
  const [selectedRound, setSelectedRound] = useState("");
  const [mode, setMode] = useState<"next" | "race">("next");
  const [loading, setLoading] = useState(false);
  const [loadingRaces, setLoadingRaces] = useState(false);
  const [error, setError] = useState("");

  const selectedRace = useMemo(() => {
    return races.find((race) => String(race.round) === selectedRound) ?? null;
  }, [races, selectedRound]);

  const explanationByDriver = useMemo(() => {
    const map = new Map<string, string>();

    data?.explanation?.driver_explanations?.forEach((item) => {
      map.set(item.driver, item.explanation);
    });

    return map;
  }, [data]);

  async function loadRaces(targetYear: string) {
    setLoadingRaces(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/races/?year=${targetYear}`);

      if (!response.ok) {
        throw new Error(`Could not load races. Status ${response.status}`);
      }

      const json = await response.json();

      const raceList = ((json.races ?? []) as Race[]).filter(
        (race) => race.round > 0
      );

      setRaces(raceList);

      if (raceList.length > 0) {
        setSelectedRound(String(raceList[0].round));
      } else {
        setSelectedRound("");
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Could not load race list";
      setError(message);
    } finally {
      setLoadingRaces(false);
    }
  }

  async function loadPredictions() {
    setLoading(true);
    setError("");

    try {
      let url = `${API_BASE_URL}/predictions/next?start_year=2024&end_year=2026`;

      if (mode === "race") {
        if (!selectedRound) {
          throw new Error("Please select a race first.");
        }

        url = `${API_BASE_URL}/predictions/race/${year}/${selectedRound}?start_year=2024`;      }

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const json = (await response.json()) as ExplainResponse;
      setData(json);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRaces(year);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [year]);

  useEffect(() => {
    loadPredictions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const topThree = data?.predictions?.slice(0, 3) ?? [];

  return (
    <main className="min-h-screen bg-neutral-950 text-white">
      <section className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-8 flex flex-col gap-6 rounded-3xl border border-neutral-800 bg-neutral-900/70 p-6 shadow-2xl md:flex-row md:items-end md:justify-between">
          <div>
            <p className="mb-2 text-sm uppercase tracking-[0.35em] text-red-400">
              F1 Quali Predictor
            </p>
            <h1 className="text-4xl font-bold tracking-tight md:text-6xl">
              AI qualifying forecast
            </h1>
            <p className="mt-4 max-w-2xl text-neutral-300">
              Predict qualifying order using FastF1 historical data, a
              backtested baseline model, and OpenAI-generated explanations.
            </p>
          </div>

          <div className="rounded-2xl border border-neutral-800 bg-black/40 p-4">
            <p className="text-xs uppercase tracking-widest text-neutral-500">
              Model
            </p>
            <p className="mt-1 text-lg font-semibold">
              {data?.prediction_model ?? "baseline-history-v1"}
            </p>
            <p className="mt-1 text-sm text-neutral-400">
              AI: {data?.ai_model ?? "gpt-4.1-mini"}
            </p>
            {data?.cached !== undefined && (
              <p className="mt-1 text-xs text-neutral-500">
                {data.cached ? "Loaded from cache" : "Fresh forecast"}
              </p>
            )}
          </div>
        </div>

        <div className="mb-8 grid gap-4 rounded-3xl border border-neutral-800 bg-neutral-900 p-5 md:grid-cols-[1fr_1fr_2fr_auto]">
          <div>
            <label className="mb-2 block text-sm text-neutral-400">
              Forecast type
            </label>
            <select
              value={mode}
              onChange={(event) =>
                setMode(event.target.value as "next" | "race")
              }
              className="w-full rounded-xl border border-neutral-700 bg-black px-4 py-3 text-white"
            >
              <option value="next">Next/current forecast</option>
              <option value="race">Specific race</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm text-neutral-400">Year</label>
            <select
              value={year}
              onChange={(event) => setYear(event.target.value)}
              disabled={mode === "next"}
              className="w-full rounded-xl border border-neutral-700 bg-black px-4 py-3 text-white disabled:opacity-40"
            >
              <option value="2026">2026</option>
              <option value="2025">2025</option>
              <option value="2024">2024</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm text-neutral-400">
              Race / track
            </label>
            <select
              value={selectedRound}
              onChange={(event) => setSelectedRound(event.target.value)}
              disabled={mode === "next" || loadingRaces}
              className="w-full rounded-xl border border-neutral-700 bg-black px-4 py-3 text-white disabled:opacity-40"
            >
              {races.map((race, index) => (
                <option
                  key={`${race.round}-${race.name}-${race.location}-${index}`}
                  value={race.round}
                >
                  Round {race.round}: {race.name}
                  {race.location ? ` — ${race.location}` : ""}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={loadPredictions}
            disabled={loading}
            className="rounded-xl bg-red-600 px-6 py-3 font-semibold text-white transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-60 md:self-end"
          >
            {loading ? "Loading..." : "Update forecast"}
          </button>
        </div>

        {mode === "race" && selectedRace && (
          <div className="mb-8 rounded-3xl border border-neutral-800 bg-neutral-900 p-5">
            <p className="text-sm uppercase tracking-widest text-red-400">
              Selected race
            </p>
            <h2 className="mt-2 text-2xl font-bold">{selectedRace.name}</h2>
            <p className="mt-1 text-neutral-300">
              Round {selectedRace.round} · {selectedRace.location},{" "}
              {selectedRace.country}
            </p>
            {selectedRace.date && (
              <p className="mt-1 text-sm text-neutral-500">
                Event date: {formatDate(selectedRace.date)}
              </p>
            )}
          </div>
        )}

        {error && (
          <div className="mb-8 rounded-2xl border border-red-800 bg-red-950/60 p-4 text-red-200">
            {error}
          </div>
        )}

        {data?.explanation?.summary && (
          <div className="mb-8 rounded-3xl border border-neutral-800 bg-neutral-900 p-6">
            <p className="mb-2 text-sm uppercase tracking-widest text-red-400">
              AI summary
            </p>
            <p className="text-lg leading-8 text-neutral-100">
              {data.explanation.summary}
            </p>
          </div>
        )}

        {topThree.length > 0 && (
          <div className="mb-8 grid gap-4 md:grid-cols-3">
            {topThree.map((prediction) => (
              <div
                key={prediction.driver}
                className="rounded-3xl border border-neutral-800 bg-gradient-to-b from-neutral-900 to-black p-6"
              >
                <p className="text-sm text-neutral-400">
                  Predicted P{prediction.predicted_position}
                </p>
                <h2 className="mt-2 text-4xl font-bold">
                  {prediction.driver}
                </h2>
                <p className="mt-1 text-neutral-300">{prediction.team}</p>
                <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
                  <Metric
                    label="Pole"
                    value={`${Math.round(
                      prediction.pole_probability * 100
                    )}%`}
                  />
                  <Metric
                    label="Q3"
                    value={`${Math.round(prediction.q3_probability * 100)}%`}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="overflow-hidden rounded-3xl border border-neutral-800 bg-neutral-900">
          <div className="border-b border-neutral-800 p-5">
            <h2 className="text-2xl font-bold">Predicted qualifying order</h2>
            <p className="mt-1 text-sm text-neutral-400">
              Lower score means a stronger predicted qualifying result.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[1000px] text-left">
              <thead className="bg-black/40 text-sm uppercase tracking-wider text-neutral-400">
                <tr>
                  <th className="px-5 py-4">Pos</th>
                  <th className="px-5 py-4">Driver</th>
                  <th className="px-5 py-4">Team</th>
                  <th className="px-5 py-4">Score</th>
                  <th className="px-5 py-4">Recent</th>
                  <th className="px-5 py-4">Team recent</th>
                  <th className="px-5 py-4">Q3</th>
                  <th className="px-5 py-4">Confidence</th>
                  <th className="px-5 py-4">AI explanation</th>
                </tr>
              </thead>
              <tbody>
                {data?.predictions?.map((prediction) => (
                  <tr
                    key={`${prediction.predicted_position}-${prediction.driver}`}
                    className="border-t border-neutral-800 align-top"
                  >
                    <td className="px-5 py-4 font-bold">
                      P{prediction.predicted_position}
                    </td>
                    <td className="px-5 py-4">
                      <div className="font-semibold">{prediction.driver}</div>
                    </td>
                    <td className="px-5 py-4 text-neutral-300">
                      {prediction.team}
                    </td>
                    <td className="px-5 py-4">{prediction.score}</td>
                    <td className="px-5 py-4">
                      {formatNumber(prediction.driver_recent_avg_position)}
                    </td>
                    <td className="px-5 py-4">
                      {formatNumber(prediction.team_recent_avg_position)}
                    </td>
                    <td className="px-5 py-4">
                      {prediction.q3_rate === null
                        ? "—"
                        : `${Math.round(prediction.q3_rate * 100)}%`}
                    </td>
                    <td className="px-5 py-4">
                      <span className="rounded-full border border-neutral-700 px-3 py-1 text-sm capitalize">
                        {prediction.confidence}
                      </span>
                    </td>
                    <td className="max-w-md px-5 py-4 text-sm leading-6 text-neutral-300">
                      {explanationByDriver.get(prediction.driver) ??
                        "No explanation returned."}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-neutral-800 bg-black/50 p-3">
      <p className="text-xs uppercase tracking-widest text-neutral-500">
        {label}
      </p>
      <p className="mt-1 text-xl font-bold">{value}</p>
    </div>
  );
}

function formatNumber(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "—";
  }

  return value.toFixed(2);
}

function formatDate(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString("en-GB", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}
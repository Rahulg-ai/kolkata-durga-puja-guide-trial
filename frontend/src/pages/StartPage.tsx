import API_BASE_URL from "../api";
import { useEffect, useState } from "react";

import "./StartPage.css";

type StartPageProps = {
  selectedStation: string;
  onStationChange: (station: string) => void;
  onContinue: () => void;
  onBack: () => void;
};

function StartPage({
  selectedStation,
  onStationChange,
  onContinue,
  onBack,
}: StartPageProps) {
  const [lines, setLines] = useState<
    Record<string, string[]>
  >({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStations() {
      try {
        const response = await fetch(
          `${API_BASE_URL}/stations`
        );

        if (!response.ok) {
          throw new Error(
            "Failed to load stations"
          );
        }

        const data = await response.json();

        setLines(data.lines);
      } catch (error) {
        console.error(
          "Failed to load stations:",
          error
        );
      } finally {
        setLoading(false);
      }
    }

    loadStations();
  }, []);

  return (
    <main className="app">
      <section className="screen-card start-selection-screen">
        <p className="festival-tag">
          🪔 YOUR PUJA JOURNEY
        </p>

        <h1 className="screen-title">
          Where are you
          <span>starting from?</span>
        </h1>

        <p className="screen-subtitle">
          Pick the Metro station where your Puja
          journey begins.
        </p>

        {loading ? (
          <p className="loading-text">
            Loading Metro stations...
          </p>
        ) : (
          <div className="station-list">
            {Object.entries(lines).map(
              ([line, stations]) => (
                <div
                  className="station-line-group"
                  key={line}
                >
                  <h2 className="station-line-title">
                    🚇 {line}
                  </h2>

                  <div className="station-list-items">
                    {stations.map(
                      (station) => {
                        const selected =
                          selectedStation ===
                          station;

                        return (
                          <button
                            key={`${line}-${station}`}
                            type="button"
                            className={`station-option ${
                              selected
                                ? "selected"
                                : ""
                            }`}
                            onClick={() =>
                              onStationChange(
                                station
                              )
                            }
                          >
                            <span>
                              {station}
                            </span>

                            {selected && (
                              <span>
                                ✓
                              </span>
                            )}
                          </button>
                        );
                      }
                    )}
                  </div>
                </div>
              )
            )}
          </div>
        )}

        {selectedStation && (
          <div className="selected-station-card">
            <div className="location-icon">
              🚉
            </div>

            <div>
              <p className="location-label">
                STARTING POINT
              </p>

              <h2>{selectedStation}</h2>

              <p className="location-description">
                Your Puja journey starts here.
              </p>
            </div>

            <div className="selected-check">
              ✓
            </div>
          </div>
        )}

        <button
          className="start-button"
          disabled={!selectedStation}
          onClick={onContinue}
        >
          Continue →
        </button>

        <button
          className="back-button"
          onClick={onBack}
        >
          ← Back
        </button>
      </section>
    </main>
  );
}

export default StartPage;
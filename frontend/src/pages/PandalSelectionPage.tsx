import {
  useMemo,
  useState,
} from "react";
import pandalsData from "../data/pandals.json";

import "./PandalSelectionPage.css";


type Pandal = {
  pandal_name: string;
  nearest_metro_station: string;
  area: string;
  last_mile_transport: string;
  distance_m: number;
  approx_time_min: number;
  google_maps_link: string;
  metro_line?: string;
};


type PandalSelectionPageProps = {
  selectedPandals: string[];

  onSelectionChange: (
    pandals: string[]
  ) => void;

  onContinue: () => void;

  loadingRoute: boolean;

  onBack: () => void;
};


/* =====================================================
   POPULAR PANDALS
   Names are matched against pandals.json (no duplicate
   data is stored here).
   ===================================================== */

const POPULAR_PANDAL_NAMES = [
  "Baghbazar Sarbojanin",
  "Sree Bhumi Sporting Club",
  "Sovabazar Boro Rajbari",
  "Kumartuli Park",
  "College Square",
  "Santosh Mitra Square",
  "Badamtala Ashar Sangha",
  "Deshapriya Park",
  "Ekdalia Evergreen",
  "Tridhara Sammilani",
];


function normalizeName(
  name: string
): string {
  return name
    .trim()
    .toLowerCase();
}


function formatDistance(
  meters: number
): string {

  if (
    typeof meters !== "number" ||
    Number.isNaN(meters)
  ) {
    return "—";
  }

  if (meters >= 1000) {
    return `${(meters / 1000).toFixed(1)} km`;
  }

  return `${Math.round(meters)} m`;
}


function PandalSelectionPage({
  selectedPandals,
  onSelectionChange,
  onContinue,
  loadingRoute,
  onBack,
}: PandalSelectionPageProps) {

  const pandals = pandalsData as Pandal[];

  const [search, setSearch] =
    useState("");
  const loading = false;


  const isSearching =
    search.trim().length > 0;


  /* =====================================================
     POPULAR (matched from existing data)
     ===================================================== */

  const popularPandals =
    useMemo(() => {

      const byName =
        new Map<string, Pandal>();

      pandals.forEach((pandal) => {
        byName.set(
          normalizeName(
            pandal.pandal_name
          ),
          pandal
        );
      });

      const result: Pandal[] = [];

      POPULAR_PANDAL_NAMES.forEach(
        (name) => {

          const match =
            byName.get(
              normalizeName(name)
            );

          if (match) {
            result.push(match);
          }

        }
      );

      return result;

    }, [pandals]);


  const popularNameSet =
    useMemo(() => {

      return new Set(
        popularPandals.map(
          (pandal) =>
            pandal.pandal_name
        )
      );

    }, [popularPandals]);


  /* =====================================================
     SEARCH
     ===================================================== */

  const filteredPandals =
    useMemo(() => {

      const query =
        search
          .trim()
          .toLowerCase();


      if (!query) {
        return pandals;
      }


      return pandals.filter(
        (pandal) => {

          return (
            pandal.pandal_name
              .toLowerCase()
              .includes(query) ||

            pandal.area
              .toLowerCase()
              .includes(query) ||

            pandal.nearest_metro_station
              .toLowerCase()
              .includes(query)
          );

        }
      );

    }, [
      pandals,
      search,
    ]);


  /* =====================================================
     TOGGLE PANDAL
     ===================================================== */

  function togglePandal(
    pandalName: string
  ) {

    if (
      selectedPandals.includes(
        pandalName
      )
    ) {

      onSelectionChange(
        selectedPandals.filter(
          (name) =>
            name !== pandalName
        )
      );

      return;
    }


    onSelectionChange([
      ...selectedPandals,
      pandalName,
    ]);

  }


  /* =====================================================
     CLEAR
     ===================================================== */

  function clearSelection() {
    onSelectionChange([]);
  }


  /* =====================================================
     CARD
     ===================================================== */

  function renderPandalCard(
    pandal: Pandal,
    popular: boolean
  ) {

    const selected =
      selectedPandals.includes(
        pandal.pandal_name
      );

    const classes = [
      "pandal-card",
      selected ? "selected" : "",
      popular ? "popular" : "",
    ]
      .filter(Boolean)
      .join(" ");


    return (

      <button
        type="button"
        key={pandal.pandal_name}
        className={classes}
        aria-pressed={selected}
        onClick={() =>
          togglePandal(
            pandal.pandal_name
          )
        }
      >

        {/* TOP ROW */}

        <div className="pandal-card-top">

          <div
            className="pandal-check"
            aria-hidden="true"
          >
            {selected ? "✓" : ""}
          </div>


          {popular && (
            <span className="pandal-popular-badge">
              🔥 POPULAR
            </span>
          )}


          <span
            className="pandal-emblem"
            aria-hidden="true"
          >
            🌺
          </span>

        </div>


        {/* DIVIDER */}

        <div
          className="pandal-card-divider"
          aria-hidden="true"
        >
          ✦
        </div>


        {/* NAME */}

        <h3 className="pandal-name">
          {pandal.pandal_name}
        </h3>


        {/* AREA */}

        <p className="pandal-area">
          📍 {pandal.area}
        </p>


        {/* META */}

        <div className="pandal-meta">

          <div className="pandal-meta-row">

            <span
              className="pandal-meta-icon"
              aria-hidden="true"
            >
              🚇
            </span>

            <span className="pandal-meta-text">

              <span className="pandal-meta-label">
                Nearest Metro
              </span>

              <span className="pandal-meta-value">
                {pandal.nearest_metro_station}
              </span>

            </span>

          </div>


          <div className="pandal-meta-row">

            <span
              className="pandal-meta-icon"
              aria-hidden="true"
            >
              🚶
            </span>

            <span className="pandal-meta-text">

              <span className="pandal-meta-label">
                Distance
              </span>

              <span className="pandal-meta-value">
                {formatDistance(
                  pandal.distance_m
                )}
              </span>

            </span>

          </div>

        </div>


        {/* FOOTER */}

        <div className="pandal-card-footer">

          <span>
            DURGA PUJA • KOLKATA
          </span>

        </div>

      </button>

    );

  }


  /* =====================================================
     RENDER
     ===================================================== */

  return (
    <main className="app">

      <section className="screen-card pandal-selection-screen">


        {/* ===============================================
            PAGE HEADER
            =============================================== */}

        <p className="festival-tag">
          🎉 CHOOSE YOUR PANDALS
        </p>


        <h1 className="screen-title">

          Pick the pandals

          <span>
            you want to visit
          </span>

        </h1>


        <p className="screen-subtitle">

          Select as many as you like.
          We'll work out the journey.

        </p>


        {/* ===============================================
            SELECTION SUMMARY
            =============================================== */}

        <div className="selection-summary">

          <div>

            <strong>
              {selectedPandals.length}
            </strong>

            <span>
              pandals selected
            </span>

          </div>


          {selectedPandals.length > 0 && (
            <button
              type="button"
              className="clear-selection-button"
              onClick={
                clearSelection
              }
            >
              Clear
            </button>
          )}

        </div>


        {/* ===============================================
            SEARCH
            =============================================== */}

        <div className="pandal-search">

          <span>
            🔎
          </span>


          <input
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value
              )
            }
            placeholder="Search pandal, area or Metro station..."
          />

        </div>


        {/* ===============================================
            LOADING
            =============================================== */}

        {loading ? (

          <div className="pandal-loading">

            <div className="loading-spinner" />

            <p>
              Loading pandals...
            </p>

          </div>

        ) : filteredPandals.length === 0 ? (

          /* =============================================
             EMPTY
             ============================================= */

          <div className="pandal-empty">

            <div>
              🔎
            </div>

            <h2>
              No pandal found
            </h2>

            <p>
              Try another pandal name,
              area or Metro station.
            </p>

          </div>

        ) : isSearching ? (

          /* =============================================
             SEARCH RESULTS (single clean grid)
             ============================================= */

          <div className="pandal-scroll">

            <p className="pandal-results-count">
              {filteredPandals.length}
              {" "}
              {filteredPandals.length === 1
                ? "pandal"
                : "pandals"}
              {" "}found
            </p>


            <div className="pandal-grid">

              {filteredPandals.map(
                (pandal) =>
                  renderPandalCard(
                    pandal,
                    popularNameSet.has(
                      pandal.pandal_name
                    )
                  )
              )}

            </div>

          </div>

        ) : (

          /* =============================================
             POPULAR + ALL PANDALS
             ============================================= */

          <div className="pandal-scroll">

            {popularPandals.length > 0 && (

              <section className="pandal-section pandal-section-popular">

                <header className="pandal-section-header">

                  <h2 className="pandal-section-title">
                    🔥 Popular Pandals
                  </h2>

                  <p className="pandal-section-subtitle">
                    Crowd-favourite Puja stops
                    to get you started
                  </p>

                  <div
                    className="pandal-section-rule"
                    aria-hidden="true"
                  >
                    <span>✦</span>
                  </div>

                </header>


                <div className="pandal-grid">

                  {popularPandals.map(
                    (pandal) =>
                      renderPandalCard(
                        pandal,
                        true
                      )
                  )}

                </div>

              </section>

            )}


            <section className="pandal-section">

              <header className="pandal-section-header">

                <h2 className="pandal-section-title">
                  All Pandals
                </h2>

                <p className="pandal-section-subtitle">
                  {pandals.length} pandals across the city
                </p>

                <div
                  className="pandal-section-rule"
                  aria-hidden="true"
                >
                  <span>✦</span>
                </div>

              </header>


              <div className="pandal-grid">

                {pandals.map(
                  (pandal) =>
                    renderPandalCard(
                      pandal,
                      popularNameSet.has(
                        pandal.pandal_name
                      )
                    )
                )}

              </div>

            </section>

          </div>

        )}


        {/* ===============================================
            GENERATE ROUTE
            =============================================== */}

        <button
          className="start-button route-generate-button"
          disabled={
            selectedPandals.length === 0 ||
            loadingRoute
          }
          onClick={
            onContinue
          }
        >

          {loadingRoute
            ? "✨ Creating Your Route..."
            : "Generate My Route →"}

        </button>


        {/* ===============================================
            BACK
            =============================================== */}

        <button
          className="back-button"
          onClick={
            onBack
          }
        >
          ← Change Starting Station
        </button>

      </section>

    </main>
  );
}


export default PandalSelectionPage;
import {
  useEffect,
  useMemo,
  useState,
} from "react";

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


function PandalSelectionPage({
  selectedPandals,
  onSelectionChange,
  onContinue,
  loadingRoute,
  onBack,
}: PandalSelectionPageProps) {

  const [pandals, setPandals] =
    useState<Pandal[]>([]);

  const [search, setSearch] =
    useState("");

  const [loading, setLoading] =
    useState(true);


  /* =====================================================
     LOAD PANDALS
     ===================================================== */

  useEffect(() => {

    async function loadPandals() {

      try {

        const response =
          await fetch(
            "http://localhost:8000/pandals"
          );


        if (!response.ok) {
          throw new Error(
            "Failed to load pandals"
          );
        }


        const data =
          await response.json();


        setPandals(data);

      } catch (error) {

        console.error(
          "Failed to load pandals:",
          error
        );

      } finally {

        setLoading(false);

      }

    }


    loadPandals();

  }, []);


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

        ) : (

          /* =============================================
             PANDAL GRID
             ============================================= */

          <div className="pandal-grid">

            {filteredPandals.map(
              (pandal) => {

                const selected =
                  selectedPandals.includes(
                    pandal.pandal_name
                  );


                return (

                  <button
                    type="button"
                    key={
                      pandal.pandal_name
                    }
                    className={`pandal-card ${
                      selected
                        ? "selected"
                        : ""
                    }`}
                    onClick={() =>
                      togglePandal(
                        pandal.pandal_name
                      )
                    }
                  >

                    {/* TOP */}

                    <div className="pandal-card-top">

                      <div className="pandal-check">

                        {selected
                          ? "✓"
                          : ""}

                      </div>


                      <span className="pandal-number">
                        🌺
                      </span>

                    </div>


                    {/* DECORATIVE DIVIDER */}

                    <div className="pandal-card-divider">
                      ✦
                    </div>


                    {/* PANDAL NAME */}

                    <h2>
                      {pandal.pandal_name}
                    </h2>


                    {/* PLACE */}

                    <p className="pandal-area">
                      📍 {pandal.area}
                    </p>


                    {/* FOOTER */}

                    <div className="pandal-card-footer">

                      <span>
                        DURGA PUJA
                      </span>

                    </div>

                  </button>

                );

              }
            )}

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
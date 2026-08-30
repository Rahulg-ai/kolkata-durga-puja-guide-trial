import {
  useEffect,
  useMemo,
  useState,
} from "react";

import type {
  JourneyOption,
  RouteStop,
} from "../types/route";

import API_BASE_URL from "../api";

import "./RoutePage.css";


/* =====================================================
   TYPES
   ===================================================== */

type RoutePageProps = {
  startStation: string;
  route: RouteStop[];
  onBack: () => void;
  onStartNewJourney: () => void;
};


type ReturnMetroSegment = {
  line: string | null;
  stations: string[];
};


type ReturnInterchange = {
  station: string;
  from_line: string;
  to_line: string;
};


type ReturnRoute = {
  from_pandal: string;
  starting_station: string;
  nearest_metro_station: string;

  last_mile_transport: string;
  last_mile_recommended: string;

  walk_to_metro_distance_m: number;
  walk_to_metro_time_min: number;
  auto_to_metro_time_min: number;

  metro_route: string[];

  metro_segments: ReturnMetroSegment[];

  interchanges: ReturnInterchange[];

  metro_hops: number;
  metro_time_min: number;
  estimated_time_min: number;
};


/* =====================================================
   HELPERS
   ===================================================== */

function formatDistance(distance?: number) {
  if (
    distance === undefined ||
    distance === null
  ) {
    return "";
  }

  if (distance >= 1000) {
    return `${(
      distance / 1000
    ).toFixed(1)} km`;
  }

  return `${distance} m`;
}


function formatTime(time: number) {
  return `~${time} min`;
}


function getModeIcon(
  mode: JourneyOption["mode"]
) {
  if (mode === "walk") {
    return "🚶";
  }

  if (mode === "metro") {
    return "🚇";
  }

  if (mode === "auto") {
    return "🛺";
  }

  return "🚶";
}


function getModeLabel(
  mode: JourneyOption["mode"]
) {
  if (mode === "walk") {
    return "Walk";
  }

  if (mode === "metro") {
    return "Metro";
  }

  if (mode === "auto") {
    return "Auto";
  }

  return "Travel";
}


/* =====================================================
   HUMAN-READABLE TRAVEL INSTRUCTION
   ===================================================== */

function getTravelInstruction(
  from: string,
  to: string,
  option: JourneyOption
) {
  if (option.mode === "walk") {
    const distance = formatDistance(
      option.distance_m
    );

    const time = formatTime(
      option.time_min
    );

    return (
      `Walk directly from ${from} to ${to}. ` +
      `The distance is about ${distance} ` +
      `and it takes around ${time.replace(
        "~",
        ""
      )}.`
    );
  }


  if (option.mode === "auto") {
    const distance = formatDistance(
      option.distance_m
    );

    const time = formatTime(
      option.time_min
    );

    return (
      `Take an auto directly from ${from} to ${to}. ` +
      `The distance is about ${distance} ` +
      `and the estimated travel time is ${time.replace(
        "~",
        ""
      )}.`
    );
  }


  if (option.mode === "metro") {
    const metroRoute =
      option.metro_route ?? [];

    const firstStation =
      metroRoute.length > 0
        ? metroRoute[0]
        : "the nearest Metro station";

    const lastStation =
      metroRoute.length > 0
        ? metroRoute[
            metroRoute.length - 1
          ]
        : "the destination station";

    const departureDistance =
      formatDistance(
        option.departure_distance_m
      );

    const arrivalDistance =
      formatDistance(
        option.arrival_distance_m
      );

    let instruction =
      `From ${from}, go to ${firstStation} Metro Station`;

    if (
      option.departure_distance_m !==
      undefined
    ) {
      instruction += ` (${departureDistance})`;
    }

    if (metroRoute.length > 1) {
      instruction +=
        `. Take the Metro from ${firstStation} to ${lastStation}`;
    } else {
      instruction +=
        ` and continue by Metro`;
    }

    if (
      option.arrival_distance_m !==
      undefined
    ) {
      instruction +=
        `. From ${lastStation}, travel the final ${arrivalDistance} to ${to}`;
    } else {
      instruction +=
        `. Continue to ${to}`;
    }

    instruction += ".";

    return instruction;
  }


  return `Travel from ${from} to ${to}.`;
}


/* =====================================================
   OUTBOUND TRAVEL OPTION
   ===================================================== */

function OptionCard({
  from,
  to,
  option,
  recommended,
  selected,
  onSelect,
}: {
  from: string;
  to: string;
  option: JourneyOption;
  recommended: boolean;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      className={`route-option ${
        recommended
          ? "recommended"
          : ""
      } ${
        selected
          ? "selected-option"
          : ""
      }`}
      onClick={onSelect}
    >

      <div className="option-top">

        <div className="option-mode">

          <span className="option-icon">
            {getModeIcon(
              option.mode
            )}
          </span>

          <div>

            {recommended && (
              <p className="recommended-label">
                ⭐ RECOMMENDED
              </p>
            )}

            <h3>
              {getModeLabel(
                option.mode
              )}
            </h3>

          </div>

        </div>


        <strong>
          {formatTime(
            option.time_min
          )}
        </strong>

      </div>


      <div className="option-instruction">

        <p>
          {getTravelInstruction(
            from,
            to,
            option
          )}
        </p>

      </div>


      {option.mode === "metro" &&
        option.metro_route &&
        option.metro_route.length > 0 && (
          <div className="metro-route-mini">

            <p>
              🚇 Metro route
            </p>

            <span>
              {option.metro_route.join(
                " → "
              )}
            </span>

          </div>
        )}


      {option.mode !== "metro" &&
        option.distance_m !==
          undefined && (
          <p className="option-distance">
            📍{" "}
            {formatDistance(
              option.distance_m
            )}
          </p>
        )}


      {option.estimated && (
        <span className="estimate-label">
          Estimated
        </span>
      )}


      {selected && (
        <span className="selected-label">
          ✓ Selected
        </span>
      )}

    </button>
  );
}


/* =====================================================
   FIRST PANDAL JOURNEY
   ===================================================== */

function FirstPandalJourney({
  startStation,
  stop,
}: {
  startStation: string;
  stop: RouteStop;
}) {
  return (
    <div className="arrival-instructions">

      <p className="instruction-heading">
        🚉 How to reach{" "}
        <strong>
          {stop.pandal}
        </strong>
      </p>


      <div className="journey-direction">

        <strong>
          {startStation}
        </strong>

        <span>
          →
        </span>

        <strong>
          {stop.metro_station}
        </strong>

        <span>
          →
        </span>

        <strong>
          {stop.pandal}
        </strong>

      </div>


      {stop.metro_segments.length > 0 && (
        <div className="metro-instruction">

          <p className="instruction-subheading">
            🚇 Metro journey
          </p>

          {stop.metro_segments.map(
            (
              segment,
              index
            ) => (
              <div
                className="metro-segment"
                key={`${segment.line}-${index}`}
              >

                {index > 0 && (
                  <div className="transfer-label">
                    🔄 Change Line
                  </div>
                )}

                <p className="segment-line">
                  {segment.line}
                </p>

                <p className="segment-stations">
                  {segment.stations.join(
                    " → "
                  )}
                </p>

              </div>
            )
          )}

        </div>
      )}


      <div className="last-mile-instruction">

        <p className="instruction-subheading">
          🚶 Final journey to pandal
        </p>


        <p>
          From{" "}
          <strong>
            {stop.metro_station}
          </strong>
          ,{" "}
          {stop.last_mile_transport
            .toLowerCase()
            .includes("auto")
            ? "take an auto"
            : "walk"}{" "}
          to{" "}
          <strong>
            {stop.pandal}
          </strong>
          . The distance is about{" "}
          <strong>
            {formatDistance(
              stop.last_mile_distance_m
            )}
          </strong>{" "}
          and it takes around{" "}
          <strong>
            {stop.last_mile_time_min} minutes
          </strong>
          .
        </p>

      </div>

    </div>
  );
}


/* =====================================================
   SUBSEQUENT PANDAL JOURNEY

   Uses the exact option selected in the
   previous Pandal's NEXT JOURNEY section.
   ===================================================== */

function SubsequentPandalJourney({
  from,
  to,
  option,
}: {
  from: string;
  to: string;
  option: JourneyOption;
}) {
  return (
    <div className="arrival-instructions">

      <p className="instruction-heading">
        {getModeIcon(option.mode)}{" "}
        Your journey here
      </p>


      <div className="arrival-route-title">

        <strong>
          {from}
        </strong>

        <span>
          →
        </span>

        <strong>
          {to}
        </strong>

      </div>


      <div className="selected-arrival-mode">

        <div className="selected-arrival-header">

          <span>
            {getModeIcon(
              option.mode
            )}
          </span>


          <strong>
            {getModeLabel(
              option.mode
            )}
          </strong>


          <span className="arrival-time">
            {formatTime(
              option.time_min
            )}
          </span>

        </div>


        <p>
          {getTravelInstruction(
            from,
            to,
            option
          )}
        </p>


        {option.mode === "metro" &&
          option.metro_route &&
          option.metro_route.length > 0 && (
            <div className="metro-route-mini">

              <p>
                🚇 Metro route
              </p>

              <span>
                {option.metro_route.join(
                  " → "
                )}
              </span>

            </div>
          )}


        {option.mode !== "metro" &&
          option.distance_m !==
            undefined && (
            <p className="arrival-distance">
              📍{" "}
              {formatDistance(
                option.distance_m
              )}
            </p>
          )}

      </div>

    </div>
  );
}


/* =====================================================
   RETURN LAST-MILE STEP
   ===================================================== */

function ReturnLastMileStep({
  returnRoute,
}: {
  returnRoute: ReturnRoute;
}) {
  const recommendedIsAuto =
    returnRoute.last_mile_recommended
      .toLowerCase()
      .includes("auto");


  const time = recommendedIsAuto
    ? returnRoute.auto_to_metro_time_min
    : returnRoute.walk_to_metro_time_min;


  return (
    <div className="return-step-card">

      <div className="return-step-number">
        2
      </div>


      <div className="return-step-content">

        <p className="return-step-label">

          {recommendedIsAuto
            ? "🛺 GO TO METRO"
            : "🚶 WALK TO METRO"}

        </p>


        <h3>

          {returnRoute.from_pandal}
          {" → "}
          {returnRoute.nearest_metro_station}

        </h3>


        <p className="return-step-description">

          {recommendedIsAuto ? (
            <>
              Take an{" "}
              <strong>
                auto
              </strong>{" "}
              from{" "}
              <strong>
                {returnRoute.from_pandal}
              </strong>{" "}
              to{" "}
              <strong>
                {
                  returnRoute.nearest_metro_station
                }{" "}
                Metro Station
              </strong>
              .
            </>
          ) : (
            <>
              Walk from{" "}
              <strong>
                {returnRoute.from_pandal}
              </strong>{" "}
              to{" "}
              <strong>
                {
                  returnRoute.nearest_metro_station
                }{" "}
                Metro Station
              </strong>
              .
            </>
          )}

        </p>


        <div className="return-metric-row">

          <span>
            📍{" "}
            {formatDistance(
              returnRoute.walk_to_metro_distance_m
            )}
          </span>


          <span>
            ⏱{" "}
            {formatTime(time)}
          </span>

        </div>


        {recommendedIsAuto && (
          <div className="return-recommendation">
            ⭐ Auto recommended for this distance.
          </div>
        )}

      </div>

    </div>
  );
}


/* =====================================================
   RETURN METRO STEP
   ===================================================== */

function ReturnMetroStep({
  returnRoute,
}: {
  returnRoute: ReturnRoute;
}) {
  return (
    <div className="return-step-card metro-return-card">

      <div className="return-step-number">
        3
      </div>


      <div className="return-step-content">

        <p className="return-step-label">
          🚇 TAKE THE METRO
        </p>


        <h3>

          {returnRoute.nearest_metro_station}
          {" → "}
          {returnRoute.starting_station}

        </h3>


        <p className="return-step-description">

          Board the Metro at{" "}
          <strong>
            {
              returnRoute.nearest_metro_station
            }
          </strong>{" "}
          and follow the route to{" "}
          <strong>
            {returnRoute.starting_station}
          </strong>
          .

        </p>


        <div className="return-segment-list">

          {returnRoute.metro_segments.map(
            (
              segment,
              segmentIndex
            ) => {

              const interchange =
                segmentIndex > 0
                  ? returnRoute
                      .interchanges[
                      segmentIndex - 1
                    ]
                  : null;


              return (
                <div
                  className="return-segment-wrapper"
                  key={`return-segment-${segmentIndex}`}
                >

                  {interchange && (
                    <div className="return-interchange">

                      <span>
                        🔄
                      </span>


                      <div>

                        <strong>
                          Change Metro Line
                        </strong>


                        <p>
                          At{" "}
                          <strong>
                            {
                              interchange.station
                            }
                          </strong>
                          {" — "}
                          {
                            interchange.from_line
                          }
                          {" → "}
                          {
                            interchange.to_line
                          }
                        </p>

                      </div>

                    </div>
                  )}


                  <div className="return-line-card">

                    <div className="return-line-header">

                      <span>
                        🚇
                      </span>

                      <strong>
                        {
                          segment.line ||
                          "Metro"
                        }
                      </strong>

                    </div>


                    <div className="return-line-stations">

                      {segment.stations.map(
                        (
                          station,
                          stationIndex
                        ) => (

                          <div
                            className="return-line-station"
                            key={`${station}-${stationIndex}`}
                          >

                            <span className="return-line-dot">
                              {stationIndex === 0
                                ? "●"
                                : stationIndex ===
                                  segment
                                    .stations
                                    .length - 1
                                ? "●"
                                : "•"}
                            </span>


                            <strong>
                              {station}
                            </strong>

                          </div>

                        )
                      )}

                    </div>

                  </div>

                </div>
              );
            }
          )}

        </div>


        <div className="return-metro-summary">

          <span>
            🚇{" "}
            {returnRoute.metro_hops}{" "}
            stops
          </span>


          <span>
            ⏱{" "}
            {formatTime(
              returnRoute.metro_time_min
            )}{" "}
            Metro travel
          </span>

        </div>

      </div>

    </div>
  );
}


/* =====================================================
   MAIN ROUTE PAGE
   ===================================================== */

function RoutePage({
  startStation,
  route,
  onBack,
  onStartNewJourney,
}: RoutePageProps) {

  /* =================================================
     UNIQUE JOURNEY STORAGE KEY
     ================================================= */

  const journeyKey = useMemo(
    () => {

      const routeNames =
        route
          .map(
            (stop) =>
              stop.pandal
          )
          .join("|");


      return (
        `visitedPandals:` +
        `${startStation}:` +
        `${routeNames}`
      );

    },
    [
      startStation,
      route,
    ]
  );


  /* =================================================
     VISITED PANDALS
     ================================================= */

  const [
    visitedPandals,
    setVisitedPandals,
  ] = useState<string[]>(() => {

    const saved =
      localStorage.getItem(
        journeyKey
      );


    if (!saved) {
      return [];
    }


    try {

      const parsed =
        JSON.parse(saved);


      return Array.isArray(
        parsed
      )
        ? parsed
        : [];

    } catch {

      return [];

    }

  });


  /* =================================================
     SELECTED TRANSPORT

     Example:
       {
         "Sikdar Bagan": "auto",
         "Hatibagan Nabinpally": "metro"
       }
     ================================================= */

  const [
    selectedModes,
    setSelectedModes,
  ] = useState<
    Record<
      string,
      JourneyOption["mode"]
    >
  >({});


  /* =================================================
     PUJA CELEBRATION
     ================================================= */

  const [
    celebration,
    setCelebration,
  ] = useState<
    string | null
  >(null);


  /* =================================================
     RETURN ROUTE
     ================================================= */

  const [
    returnRoute,
    setReturnRoute,
  ] =
    useState<ReturnRoute | null>(
      null
    );


  const [
    loadingReturnRoute,
    setLoadingReturnRoute,
  ] = useState(false);


  const [
    returnRouteError,
    setReturnRouteError,
  ] = useState("");


  /* =================================================
     SAVE VISITED STATE
     ================================================= */

  useEffect(() => {

    localStorage.setItem(
      journeyKey,
      JSON.stringify(
        visitedPandals
      )
    );

  }, [
    journeyKey,
    visitedPandals,
  ]);


  /* =================================================
     TOGGLE VISITED
     ================================================= */

  function toggleVisited(
    pandalName: string
  ) {

    const alreadyVisited =
      visitedPandals.includes(
        pandalName
      );


    if (alreadyVisited) {

      setVisitedPandals(
        (current) =>
          current.filter(
            (name) =>
              name !== pandalName
          )
      );


      setCelebration(
        "Removed from visited ✨"
      );


      window.setTimeout(() => {
        setCelebration(null);
      }, 1800);


      return;
    }


    setVisitedPandals(
      (current) => [
        ...current,
        pandalName,
      ]
    );


    setCelebration(
      `Shubho! ${pandalName} 🎉`
    );


    window.setTimeout(() => {
      setCelebration(null);
    }, 2200);

  }


  /* =================================================
     PROGRESS
     ================================================= */

  const totalPandals =
    route.length;


  const visitedCount =
    route.filter(
      (stop) =>
        visitedPandals.includes(
          stop.pandal
        )
    ).length;


  /* =================================================
     RETURN ROUTE GENERATION

     IMPORTANT:
     This does NOT depend on visitedCount.
     ================================================= */

  async function generateReturnRoute() {

    if (
      route.length === 0
    ) {
      return;
    }


    const lastPandal =
      route[
        route.length - 1
      ].pandal;


    setLoadingReturnRoute(
      true
    );

    setReturnRoute(
      null
    );

    setReturnRouteError("");


    try {

      const response =
        await fetch(
          `${API_BASE_URL}/return-route`,
          {
            method:
              "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              current_pandal:
                lastPandal,

              start_station:
                startStation,
            }),
          }
        );


      const data =
        await response.json();


      if (
        !response.ok ||
        !data.success
      ) {

        throw new Error(
          data.message ||
            "Return route could not be created."
        );

      }


      setReturnRoute(
        data.return_route
      );


      window.setTimeout(() => {

        document
          .getElementById(
            "return-route-section"
          )
          ?.scrollIntoView({
            behavior:
              "smooth",

            block:
              "start",
          });

      }, 100);


    } catch (error) {

      console.error(
        "Return route failed:",
        error
      );


      setReturnRouteError(
        error instanceof Error
          ? error.message
          : "Return route could not be created."
      );


    } finally {

      setLoadingReturnRoute(
        false
      );

    }

  }


  /* =================================================
     START NEW JOURNEY
     ================================================= */

  function handleStartNewJourney() {

    localStorage.removeItem(
      journeyKey
    );


    setVisitedPandals([]);

    setSelectedModes({});

    setReturnRoute(null);

    setCelebration(null);

    onStartNewJourney();

  }


  /* =================================================
     RENDER
     ================================================= */

  return (
    <main className="app">

      <section className="screen-card route-screen">

        {/* ==========================================
            PUJA CELEBRATION
            ========================================== */}

        {celebration && (
          <div
            className="puja-celebration"
            role="status"
            aria-live="polite"
          >

            <span>
              ✨
            </span>


            <strong>
              {celebration}
            </strong>


            <span>
              🌺
            </span>

          </div>
        )}


        {/* ==========================================
            PAGE HEADER
            ========================================== */}

        <p className="festival-tag">
          ✨ YOUR PUJA JOURNEY
        </p>


        <h1 className="screen-title">

          Let's go

          <span>
            pandal hopping
          </span>

        </h1>


        {/* ==========================================
            PROGRESS
            ========================================== */}

        <div className="progress-card">

          <div>

            <p>
              PUJA PROGRESS
            </p>


            <h2>

              {visitedCount} /{" "}
              {totalPandals}{" "}
              Pandals Visited

            </h2>

          </div>


          <div className="progress-circle">

            {totalPandals > 0
              ? Math.round(
                  (
                    visitedCount /
                    totalPandals
                  ) *
                    100
                )
              : 0}

            %

          </div>

        </div>


        {/* ==========================================
            STARTING STATION
            ========================================== */}

        <div className="route-start-card">

          <div className="location-icon">
            🚉
          </div>


          <div>

            <p className="location-label">
              JOURNEY STARTS AT
            </p>


            <h2>
              {startStation}
            </h2>


            <p className="location-description">
              Follow each step in order.
            </p>

          </div>

        </div>


        {/* ==========================================
            OUTBOUND ROUTE
            ========================================== */}

        <div className="route-timeline">

          {route.map(
            (
              stop,
              index
            ) => {

              const visited =
                visitedPandals.includes(
                  stop.pandal
                );


              const previousStop =
                index > 0
                  ? route[
                      index - 1
                    ]
                  : null;


              const incomingTransition =
                previousStop?.next_transition;


              const incomingMode =
                previousStop
                  ? (
                      selectedModes[
                        previousStop.pandal
                      ] ??
                      incomingTransition
                        ?.recommended
                    )
                  : undefined;


              const incomingOption =
                previousStop &&
                incomingTransition &&
                incomingMode
                  ? incomingTransition.options.find(
                      (
                        option
                      ) =>
                        option.mode ===
                        incomingMode
                    )
                  : undefined;


              const nextTransition =
                stop.next_transition;


              return (
                <div
                  className={`journey-block ${
                    visited
                      ? "visited-block"
                      : ""
                  }`}
                  key={
                    stop.pandal
                  }
                >

                  {/* =================================
                      PANDAL CARD
                      ================================= */}

                  <div className="route-stop">

                    <div className="route-marker">

                      {visited
                        ? "✓"
                        : index + 1}

                    </div>


                    <div className="route-content">

                      {/* ARRIVAL SOURCE */}

                      <div className="arrival-source">

                        <span>

                          {index === 0
                            ? "🚉"
                            : getModeIcon(
                                incomingMode ??
                                  "walk"
                              )}

                        </span>


                        <div>

                          <p className="route-label">

                            {index === 0
                              ? "STARTING FROM"
                              : "ARRIVING FROM"}

                          </p>


                          <strong>

                            {index === 0
                              ? startStation
                              : previousStop?.pandal}

                          </strong>

                        </div>

                      </div>


                      {/* PANDAL NAME */}

                      <p className="route-label">

                        PANDAL{" "}
                        {index + 1}

                      </p>


                      <h2>
                        {stop.pandal}
                      </h2>


                      {visited && (
                        <div className="visited-badge">
                          ✅ VISITED
                        </div>
                      )}


                      {/* FIRST PANDAL */}

                      {index === 0 && (
                        <FirstPandalJourney
                          startStation={
                            startStation
                          }
                          stop={
                            stop
                          }
                        />
                      )}


                      {/* OTHER PANDALS */}

                      {index > 0 &&
                        previousStop &&
                        incomingOption && (
                          <SubsequentPandalJourney
                            from={
                              previousStop.pandal
                            }
                            to={
                              stop.pandal
                            }
                            option={
                              incomingOption
                            }
                          />
                        )}


                      {/* ARRIVAL */}

                      <div className="arrival-box">

                        <p>
                          🎉 YOU HAVE ARRIVED
                        </p>


                        <strong>
                          {stop.pandal}
                        </strong>

                      </div>


                      {/* GOOGLE MAPS */}

                      <a
                        className="maps-link"
                        href={
                          stop.google_maps_link
                        }
                        target="_blank"
                        rel="noreferrer"
                      >
                        📍 Open directions to{" "}
                        {stop.pandal}
                      </a>


                      {/* VISITED TOGGLE */}

                      <button
                        type="button"
                        className={`visited-button ${
                          visited
                            ? "completed"
                            : ""
                        }`}
                        onClick={() =>
                          toggleVisited(
                            stop.pandal
                          )
                        }
                      >

                        {visited
                          ? "✅ Visited — tap to undo"
                          : "✅ I've Visited This Pandal"}

                      </button>

                    </div>

                  </div>


                  {/* =================================
                      NEXT JOURNEY
                      ================================= */}

                  {nextTransition && (
                    <div className="between-pandals">

                      <div className="journey-arrow">
                        ↓
                      </div>


                      <div className="next-journey">

                        <p className="route-label">
                          NEXT JOURNEY
                        </p>


                        <h3>

                          {stop.pandal}
                          {" → "}
                          {
                            nextTransition.to
                          }

                        </h3>


                        <p className="next-journey-instruction">

                          You are at{" "}
                          <strong>
                            {stop.pandal}
                          </strong>
                          .

                          {" "}
                          Choose how you want
                          to travel to{" "}
                          <strong>
                            {
                              nextTransition.to
                            }
                          </strong>
                          .

                        </p>


                        <div className="options-list">

                          {nextTransition.options.map(
                            (
                              option
                            ) => (

                            <OptionCard
                              key={
                                option.mode
                              }

                              from={
                                stop.pandal
                              }

                              to={
                                nextTransition.to
                              }

                              option={
                                option
                              }

                              recommended={
                                option.mode ===
                                nextTransition.recommended
                              }

                              selected={
                                option.mode ===
                                (
                                  selectedModes[
                                    stop.pandal
                                  ] ??
                                  nextTransition.recommended
                                )
                              }

                              onSelect={() =>
                                setSelectedModes(
                                  (
                                    current
                                  ) => ({
                                    ...current,

                                    [stop.pandal]:
                                      option.mode,
                                  })
                                )
                              }

                            />

                          ))}

                        </div>

                      </div>

                    </div>
                  )}

                </div>
              );
            }
          )}

        </div>


        {/* ==========================================
            RETURN CTA
            ========================================== */}

        <div className="route-end-card">

          <div className="finish-icon">
            🏠
          </div>


          <h2>
            Ready to head back?
          </h2>


          <p>

            You can view your return journey
            anytime. You don't need to mark
            every pandal as visited.

          </p>


          <button
            type="button"
            className="start-button"
            onClick={
              generateReturnRoute
            }
            disabled={
              loadingReturnRoute
            }
          >

            {loadingReturnRoute
              ? "Creating Return Journey..."
              : `🏠 Show Return Journey to ${startStation}`}

          </button>


          {returnRouteError && (
            <p className="return-error">
              ⚠{" "}
              {returnRouteError}
            </p>
          )}

        </div>


        {/* ==========================================
            RETURN JOURNEY
            ========================================== */}

        {returnRoute && (
          <section
            id="return-route-section"
            className="return-route-section"
          >

            {/* RETURN HEADER */}

            <div className="return-route-header">

              <p className="route-label">
                🏠 RETURN JOURNEY
              </p>


              <h2>

                Your way back to{" "}
                {
                  returnRoute.starting_station
                }

              </h2>


              <p>

                Follow these steps from your
                final pandal back to your
                starting station.

              </p>

            </div>


            <div className="return-timeline">


              {/* ==================================
                  STEP 1
                  ================================== */}

              <div className="return-step-card">

                <div className="return-step-number">
                  1
                </div>


                <div className="return-step-content">

                  <p className="return-step-label">
                    YOU ARE HERE
                  </p>


                  <h3>

                    🎪{" "}
                    {
                      returnRoute.from_pandal
                    }

                  </h3>


                  <p className="return-step-description">

                    This is your final pandal.
                    From here, follow the
                    steps below to return to{" "}
                    <strong>
                      {
                        returnRoute.starting_station
                      }
                    </strong>
                    .

                  </p>

                </div>

              </div>


              <div className="return-connector">
                ↓
              </div>


              {/* ==================================
                  STEP 2
                  ================================== */}

              <ReturnLastMileStep
                returnRoute={
                  returnRoute
                }
              />


              <div className="return-connector">
                ↓
              </div>


              {/* ==================================
                  STEP 3
                  ================================== */}

              <ReturnMetroStep
                returnRoute={
                  returnRoute
                }
              />


              <div className="return-connector">
                ↓
              </div>


              {/* ==================================
                  FINAL ARRIVAL
                  ================================== */}

              <div className="return-arrival-card">

                <div className="return-arrival-icon">
                  🏠
                </div>


                <p className="return-step-label">
                  JOURNEY COMPLETE
                </p>


                <h3>

                  You're back at{" "}
                  {
                    returnRoute.starting_station
                  }

                </h3>


                <p>

                  Your Puja journey is complete.
                  Safe travels and Shubho Bijoya! 🌺

                </p>

              </div>

            </div>

          </section>
        )}


        {/* ==========================================
            BOTTOM BUTTONS
            ========================================== */}

        <button
          className="back-button"
          onClick={onBack}
        >
          ← Change Pandals
        </button>


        <button
          className="back-button"
          onClick={
            handleStartNewJourney
          }
        >
          🏠 Start New Journey
        </button>

      </section>

    </main>
  );
}


export default RoutePage;
import { useEffect, useState } from "react";

import { getFestivalMessage } from "../utils/festival";
import API_BASE_URL from "../api";

import DurgaMotif from "../components/decorative/DurgaMotif";
import AlpanaDivider from "../components/decorative/AlpanaDivider";

import "./WelcomePage.css";


type WelcomePageProps = {
  onStart: () => void;
};


type Supporter = {
  rank: number;
  display_name: string;
  amount: number;
  title: string;
  icon: string;
};


function WelcomePage({
  onStart,
}: WelcomePageProps) {

  const festival =
    getFestivalMessage();


  const [
    supporters,
    setSupporters,
  ] = useState<Supporter[]>([]);


  const [
    loadingSupporters,
    setLoadingSupporters,
  ] = useState(true);


  /* =====================================================
     LOAD SUPPORTERS
     ===================================================== */

  useEffect(() => {

    async function loadSupporters() {

      try {

        const response =
          await fetch(
            `${API_BASE_URL}/supporters`
          );


        if (!response.ok) {

          throw new Error(
            "Failed to load supporters"
          );

        }


        const data =
          await response.json();


        const loadedSupporters =
          Array.isArray(
            data?.supporters
          )
            ? data.supporters
            : [];


        setSupporters(
          loadedSupporters
        );

      } catch (error) {

        console.error(
          "Failed to load supporters:",
          error
        );

        setSupporters([]);

      } finally {

        setLoadingSupporters(
          false
        );

      }

    }


    loadSupporters();

  }, []);


  /* =====================================================
     OPEN SUPPORT PAGE
     ===================================================== */

  function openSupportPage() {

    window.location.href =
      "/support";

  }


  return (
    <main className="app">

      <section className="hero">


        {/* =================================================
           HERO CONTENT
           ================================================= */}

        <div className="hero-content">

          <DurgaMotif />


          <p className="festival-tag">
            🪔 KOLKATA DURGA PUJA 2026
          </p>


          <h1>
            {festival.title}
          </h1>


          <p className="subtitle">
            {festival.subtitle}
          </p>


          <p className="hero-description">

            Discover Kolkata's famous pandals,
            plan your Metro journey, and enjoy
            your Puja without the travel headache.

          </p>


          {/* ===============================================
              HERO ACTIONS
              =============================================== */}

          <div className="hero-actions">

            <button
              type="button"
              className="start-button"
              onClick={onStart}
            >
              Start Exploring →
            </button>


            <button
              type="button"
              className="support-button"
              onClick={
                openSupportPage
              }
            >
              🌺 Support the App
            </button>

          </div>


          {/* ===============================================
              HERO FEATURES
              =============================================== */}

          <div className="hero-features">

            <div className="hero-feature">
              <span>🚇</span>
              <p>
                Smart Metro Routes
              </p>
            </div>


            <div className="hero-feature">
              <span>🎉</span>
              <p>
                Curated Pandals
              </p>
            </div>


            <div className="hero-feature">
              <span>🗺️</span>
              <p>
                Easy Navigation
              </p>
            </div>

          </div>

        </div>


        {/* =================================================
           DIVIDER
           ================================================= */}

        <AlpanaDivider
          className="welcome-divider"
        />


        {/* =================================================
           SUPPORTER SECTION
           ================================================= */}

        <div className="supporter-section">


          {/* ===============================================
              HEADER
              =============================================== */}

          <div className="supporter-header">

            <p className="festival-tag">
              🌺 PUJA SUPPORTERS
            </p>


            <h2>
              People helping keep

              <span>
                the guide alive.
              </span>
            </h2>


            <p>
              Support the project and get
              your name on the supporter board.
            </p>

          </div>


          {/* ===============================================
              SUPPORT BUTTON — NOW ABOVE THE BOARD
              =============================================== */}

          <button
            type="button"
            className="leaderboard-support-button"
            onClick={
              openSupportPage
            }
          >
            🌺 Become a Supporter
          </button>


          {/* ===============================================
              SUPPORTER BOARD
              =============================================== */}

          {loadingSupporters ? (

            <div className="supporter-loading">

              ✨ Loading the Pujo squad...

            </div>

          ) : supporters.length === 0 ? (

            <div className="supporter-empty">

              <div className="supporter-empty-icon">
                🌺
              </div>


              <p>
                Be the first name on the
                Pujo Supporter Board. ❤️
              </p>

            </div>

          ) : (

            <div className="supporter-list">

              {[...supporters]
                .sort(
                  (a, b) =>
                    b.amount - a.amount
                )
                .slice(0, 12)
                .map(
                  (
                    supporter
                  ) => (

                    <article
                      className="supporter-row"
                      key={`${supporter.display_name}-${supporter.amount}`}
                    >

                      {/* =================================
                          ICON
                          ================================= */}

                      <div
                        className="supporter-rank"
                        aria-hidden="true"
                      >
                        {supporter.icon}
                      </div>


                      {/* =================================
                          NAME + TITLE
                          ================================= */}

                      <div className="supporter-info">

                        <div className="supporter-name">
                          {
                            supporter.display_name
                          }
                        </div>


                        <div className="supporter-title">
                          {supporter.title}
                        </div>

                      </div>


                      {/* =================================
                          AMOUNT
                          ================================= */}

                      <div className="supporter-amount">

                        ₹
                        {supporter.amount.toLocaleString(
                          "en-IN"
                        )}

                      </div>

                    </article>

                  )
                )}

            </div>

          )}


          {/* ===============================================
              FOOTER
              =============================================== */}

          <p className="supporter-board-footer">

            Every supporter matters.
            Every contribution helps. ❤️

          </p>

        </div>


        {/* =================================================
           DECORATIONS
           ================================================= */}

        <div className="hero-decoration hero-decoration-one">
          🪔
        </div>


        <div className="hero-decoration hero-decoration-two">
          🌺
        </div>


        <div className="hero-decoration hero-decoration-three">
          ✨
        </div>

      </section>

    </main>
  );
}


export default WelcomePage;
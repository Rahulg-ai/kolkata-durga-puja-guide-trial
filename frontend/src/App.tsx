import { useState } from "react";
import {
  BrowserRouter,
  Route,
  Routes,
  useNavigate,
} from "react-router-dom";

import "./App.css";

import WelcomePage from "./pages/WelcomePage";
import StartPage from "./pages/StartPage";
import PandalSelectionPage from "./pages/PandalSelectionPage";
import RoutePage from "./pages/RoutePage";
import DonationPage from "./pages/DonationPage";

import API_BASE_URL from "./api";

import type { RouteStop } from "./types/route";


function AppRoutes() {
  const navigate = useNavigate();

  const [selectedStation, setSelectedStation] =
    useState("");

  const [selectedPandals, setSelectedPandals] =
    useState<string[]>([]);

  const [route, setRoute] =
    useState<RouteStop[]>([]);

  const [loadingRoute, setLoadingRoute] =
    useState(false);


  function startNewJourney() {
    setSelectedStation("");
    setSelectedPandals([]);
    setRoute([]);

    navigate("/start");
  }


  function changePandals() {
    setRoute([]);

    navigate("/pandals");
  }


  async function generateRoute() {
    if (!selectedStation) {
      alert(
        "Please select your starting Metro station."
      );

      navigate("/start");
      return;
    }

    if (selectedPandals.length === 0) {
      alert(
        "Please select at least one pandal."
      );

      return;
    }

    setLoadingRoute(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/route`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            start_station: selectedStation,
            selected_pandals: selectedPandals,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Failed to generate route."
        );
      }

      const data = await response.json();

      if (
        !Array.isArray(data.route) ||
        data.route.length === 0
      ) {
        throw new Error(
          "No valid route was returned."
        );
      }

      setRoute(data.route);

      navigate("/route");
    } catch (error) {
      console.error(
        "Route generation failed:",
        error
      );

      alert(
        "We couldn't generate your route. Please try again."
      );
    } finally {
      setLoadingRoute(false);
    }
  }


  return (
    <Routes>

      <Route
        path="/"
        element={
          <WelcomePage
            onStart={startNewJourney}
          />
        }
      />


      <Route
        path="/start"
        element={
          <StartPage
            selectedStation={selectedStation}
            onStationChange={(station) => {
              setSelectedStation(station);
              setRoute([]);
            }}
            onContinue={() => {
              if (!selectedStation) {
                alert(
                  "Please select a starting Metro station."
                );
                return;
              }

              navigate("/pandals");
            }}
            onBack={() => navigate("/")}
          />
        }
      />


      <Route
        path="/pandals"
        element={
          <PandalSelectionPage
            selectedPandals={selectedPandals}
            onSelectionChange={(pandals) => {
              setSelectedPandals(pandals);
              setRoute([]);
            }}
            onContinue={generateRoute}
            loadingRoute={loadingRoute}
            onBack={() => navigate("/start")}
          />
        }
      />


      <Route
        path="/route"
        element={
          route.length > 0 &&
          selectedStation ? (
            <RoutePage
              startStation={selectedStation}
              route={route}
              onBack={changePandals}
              onStartNewJourney={startNewJourney}
            />
          ) : (
            <StartPage
              selectedStation={selectedStation}
              onStationChange={setSelectedStation}
              onContinue={() =>
                navigate("/pandals")
              }
              onBack={() => navigate("/")}
            />
          )
        }
      />


      <Route
        path="/support"
        element={
          <DonationPage
            onBack={() => navigate("/")}
          />
        }
      />

    </Routes>
  );
}


function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}


export default App;
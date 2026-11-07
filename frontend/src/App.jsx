
import { useMemo, useState } from "react";
import "./index.css";

const initialAppliances = [
  { id: 1, icon: "❄️", name: "Air Conditioner", watts: 1500, hours: 4 },
  { id: 2, icon: "🧊", name: "Refrigerator", watts: 150, hours: 8 },
  { id: 3, icon: "📺", name: "Television", watts: 100, hours: 5 },
  { id: 4, icon: "💡", name: "Lighting", watts: 80, hours: 6 },
  { id: 5, icon: "🧺", name: "Washing Machine", watts: 500, hours: 0.5 },
];

const navigation = [
  { name: "Dashboard", icon: "▦" },
  { name: "My Household", icon: "⌂" },
  { name: "What-If Simulator", icon: "◈" },
  { name: "Bill Calculator", icon: "▤" },
  { name: "AI Forecasting", icon: "✦" },
];

function App() {
  const [page, setPage] = useState("Dashboard");
  const [appliances, setAppliances] = useState(initialAppliances);
  const [householdName, setHouseholdName] = useState("My Home");
  const [occupants, setOccupants] = useState(4);
  const [reduction, setReduction] = useState(20);
  const [consumption, setConsumption] = useState(400);

  const estimatedKwh = useMemo(() => {
    return appliances.reduce((sum, appliance) => {
      return sum + (appliance.watts * appliance.hours * 30) / 1000;
    }, 0);
  }, [appliances]);

  const scenarioKwh = estimatedKwh * (1 - reduction / 100);

  function updateHours(id, value) {
    setAppliances((current) =>
      current.map((appliance) =>
        appliance.id === id
          ? { ...appliance, hours: Number(value) }
          : appliance
      )
    );
  }

  function removeAppliance(id) {
    setAppliances((current) =>
      current.filter((appliance) => appliance.id !== id)
    );
  }

  function addAppliance() {
    const name = window.prompt("Enter the appliance name:");
    if (!name || !name.trim()) return;

    const watts = Number(window.prompt("Power rating in watts:", "100"));
    if (!Number.isFinite(watts) || watts <= 0) return;

    setAppliances((current) => [
      ...current,
      {
        id: Date.now(),
        icon: "⚡",
        name: name.trim(),
        watts,
        hours: 1,
      },
    ]);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">⚡</div>
          <div>
            <strong>EgyptPowerSim</strong>
            <span>Smart Energy Platform</span>
          </div>
        </div>

        <div className="nav-heading">WORKSPACE</div>

        <nav className="navigation">
          {navigation.map((item) => (
            <button
              key={item.name}
              className={`nav-item ${page === item.name ? "active" : ""}`}
              onClick={() => setPage(item.name)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.name}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-note">
            <span className="sidebar-note-icon">✦</span>
            <strong>Building smarter homes</strong>
            <p>
              Explore your electricity consumption and test
              different household scenarios.
            </p>
          </div>
          <div className="sidebar-footer">MIU · Graduation Project AI08</div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> {page}</div>
          <div className="topbar-right">
            <span className="prototype-pill">● Prototype</span>
            <div className="avatar">AI</div>
          </div>
        </header>

        <div className="page-content">
          {page === "Dashboard" && (
            <>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">YOUR ENERGY OVERVIEW</div>
                  <h1>Good to see you! 👋</h1>
                  <p>
                    Understand your household's electricity usage
                    and explore ways to manage it.
                  </p>
                </div>
                <button
                  className="primary-button"
                  onClick={() => setPage("My Household")}
                >
                  Manage household →
                </button>
              </div>

              <div className="hero-card">
                <div className="hero-copy">
                  <span className="hero-tag">YOUR SMART ENERGY JOURNEY</span>
                  <h2>Take control of your home's energy.</h2>
                  <p>
                    Build your household profile, understand where
                    electricity goes, and compare possible changes.
                  </p>
                  <button
                    className="hero-button"
                    onClick={() => setPage("What-If Simulator")}
                  >
                    Explore scenarios →
                  </button>
                </div>
                <div className="hero-art">⌁<span>⚡</span></div>
              </div>

              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-top">
                    <span>Estimated monthly usage</span>
                    <span className="stat-symbol">↗</span>
                  </div>
                  <div className="stat-value">
                    {estimatedKwh.toFixed(1)}
                    <small> kWh</small>
                  </div>
                  <div className="stat-foot">
                    Based on appliance assumptions
                  </div>
                </div>

                <div className="stat-card">
                  <div className="stat-top">
                    <span>Registered appliances</span>
                    <span className="stat-symbol">⌂</span>
                  </div>
                  <div className="stat-value">
                    {appliances.length}
                    <small> devices</small>
                  </div>
                  <div className="stat-foot">
                    Editable in My Household
                  </div>
                </div>

                <div className="stat-card">
                  <div className="stat-top">
                    <span>Household members</span>
                    <span className="stat-symbol">♧</span>
                  </div>
                  <div className="stat-value">
                    {occupants}
                    <small> people</small>
                  </div>
                  <div className="stat-foot">
                    Your current household profile
                  </div>
                </div>
              </div>

              <div className="content-grid">
                <section className="panel">
                  <div className="panel-heading">
                    <div>
                      <h3>Appliance energy breakdown</h3>
                      <p>Estimated monthly electricity consumption</p>
                    </div>
                    <span className="small-pill">Monthly</span>
                  </div>

                  <div className="usage-list">
                    {appliances.map((a) => {
                      const usage = (a.watts * a.hours * 30) / 1000;
                      const percent =
                        estimatedKwh > 0
                          ? (usage / estimatedKwh) * 100
                          : 0;

                      return (
                        <div className="usage-row" key={a.id}>
                          <span className="usage-icon">{a.icon}</span>
                          <div className="usage-info">
                            <div className="usage-label">
                              <strong>{a.name}</strong>
                              <span>{usage.toFixed(1)} kWh</span>
                            </div>
                            <div className="progress-track">
                              <div
                                className="progress-fill"
                                style={{ width: `${percent}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </section>

                <section className="panel insight-panel">
                  <div className="panel-heading">
                    <div>
                      <h3>Energy insights</h3>
                      <p>Explore your household information</p>
                    </div>
                  </div>

                  <div className="insight-icon">✦</div>
                  <h4>Start with your appliances</h4>
                  <p className="insight-description">
                    Adjust the power ratings and daily usage hours
                    to see how your estimated consumption changes.
                  </p>
                  <button
                    className="text-button"
                    onClick={() => setPage("My Household")}
                  >
                    Update household profile →
                  </button>
                  <div className="insight-foot">
                    AI forecasting will be added after model training.
                  </div>
                </section>
              </div>
            </>
          )}

          {page === "My Household" && (
            <>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">HOUSEHOLD PROFILE</div>
                  <h1>My Household</h1>
                  <p>
                    Describe your home and customize its estimated
                    electricity usage.
                  </p>
                </div>
                <button className="primary-button" onClick={addAppliance}>
                  + Add appliance
                </button>
              </div>

              <section className="panel profile-panel">
                <h3>Home information</h3>
                <div className="form-grid">
                  <label>
                    Household name
                    <input
                      value={householdName}
                      onChange={(e) => setHouseholdName(e.target.value)}
                    />
                  </label>
                  <label>
                    Number of occupants
                    <input
                      type="number"
                      min="1"
                      max="30"
                      value={occupants}
                      onChange={(e) =>
                        setOccupants(
                          Math.max(1, Number(e.target.value) || 1)
                        )
                      }
                    />
                  </label>
                </div>
              </section>

              <section className="panel">
                <div className="panel-heading">
                  <div>
                    <h3>Your appliances</h3>
                    <p>Change daily hours to update the estimate</p>
                  </div>
                  <span className="small-pill">{appliances.length} items</span>
                </div>

                {appliances.map((a) => (
                  <div className="appliance-row" key={a.id}>
                    <div className="appliance-main">
                      <div className="appliance-icon">{a.icon}</div>
                      <div>
                        <strong>{a.name}</strong>
                        <p>{a.watts} W assumed power</p>
                      </div>
                    </div>

                    <label className="hours-control">
                      Hours per day
                      <input
                        type="number"
                        min="0"
                        max="24"
                        step="0.5"
                        value={a.hours}
                        onChange={(e) =>
                          updateHours(
                            a.id,
                            Math.max(
                              0,
                              Math.min(24, Number(e.target.value) || 0)
                            )
                          )
                        }
                      />
                    </label>

                    <strong>
                      {((a.watts * a.hours * 30) / 1000).toFixed(1)} kWh/mo
                    </strong>

                    <button
                      className="remove-button"
                      onClick={() => removeAppliance(a.id)}
                      aria-label={`Remove ${a.name}`}
                    >
                      ×
                    </button>
                  </div>
                ))}
                <p className="disclaimer">
                  Power ratings and operating hours are illustrative
                  defaults. For cycling appliances such as refrigerators,
                  use average operating-equivalent hours.
                </p>
              </section>
            </>
          )}

          {page === "What-If Simulator" && (
            <>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">SCENARIO PLANNING</div>
                  <h1>What-If Simulator</h1>
                  <p>
                    Explore how a change in estimated electricity usage
                    could affect your monthly consumption.
                  </p>
                </div>
              </div>

              <section className="panel scenario-panel">
                <h3>Try a consumption reduction</h3>
                <p className="muted">
                  This is a simple percentage scenario, not an AI prediction.
                </p>

                <label className="range-label">
                  Estimated usage reduction <strong>{reduction}%</strong>
                </label>
                <input
                  className="range-input"
                  type="range"
                  min="0"
                  max="60"
                  step="5"
                  value={reduction}
                  onChange={(e) => setReduction(Number(e.target.value))}
                />

                <div className="comparison-grid">
                  <div className="comparison-card">
                    <span>Current estimate</span>
                    <strong>{estimatedKwh.toFixed(1)} kWh</strong>
                    <small>Based on your appliance profile</small>
                  </div>
                  <div className="comparison-card improved">
                    <span>Scenario estimate</span>
                    <strong>{scenarioKwh.toFixed(1)} kWh</strong>
                    <small>
                      {(estimatedKwh - scenarioKwh).toFixed(1)} kWh less
                    </small>
                  </div>
                </div>

                <p className="disclaimer">
                  Electricity bill comparisons will use the Python tariff
                  engine once we connect the backend.
                </p>
              </section>
            </>
          )}

          {page === "Bill Calculator" && (
            <>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">ELECTRICITY PRICING</div>
                  <h1>Bill Calculator</h1>
                  <p>
                    Estimate bills using your existing Egyptian
                    electricity tariff engine.
                  </p>
                </div>
              </div>

              <section className="panel simple-panel">
                <div className="insight-icon">▤</div>
                <h3>Connect the bill calculator</h3>
                <p className="muted">
                  Your Python calculator is already working and has passed
                  14 tests. Next, we will connect it to this React page
                  through FastAPI.
                </p>
                <label className="bill-input">
                  Monthly consumption (kWh)
                  <input
                    type="number"
                    min="0"
                    max="20000"
                    value={consumption}
                    onChange={(e) =>
                      setConsumption(Number(e.target.value))
                    }
                  />
                </label>
                <div className="notice">
                  Current input: {consumption} kWh. No bill has been
                  calculated yet because the backend is not connected.
                </div>
              </section>
            </>
          )}

          {page === "AI Forecasting" && (
            <>
              <div className="page-heading">
                <div>
                  <div className="eyebrow">MACHINE LEARNING</div>
                  <h1>AI Forecasting</h1>
                  <p>
                    Explore future household electricity demand.
                  </p>
                </div>
              </div>
              <section className="panel simple-panel">
                <div className="insight-icon">✦</div>
                <h3>Forecasting is coming next</h3>
                <p className="muted">
                  This module will display predictions from a real,
                  trained Python machine-learning model after we
                  select and evaluate a suitable dataset.
                </p>
                <div className="notice">
                  No AI forecast is being generated in this prototype yet.
                </div>
              </section>
            </>
          )}

          <footer className="main-footer">
            EgyptPowerSim · MIU Team AI08 · Prototype estimates are not official bills
          </footer>
        </div>
      </main>
    </div>
  );
}

export default App;

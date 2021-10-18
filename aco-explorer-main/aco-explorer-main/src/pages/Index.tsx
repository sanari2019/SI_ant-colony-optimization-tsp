import { Activity, Play, Trash2, Shuffle, ChevronDown, ChevronUp, StopCircle } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { io, Socket } from "socket.io-client";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface City {
  x: number;
  y: number;
}

interface AlgorithmData {
  iteration: number;
  best_distance: number;
  avg_distance: number;
  best_path: number[];
  pheromones?: number[][];
}

const Index = () => {
  const [isControlsOpen, setIsControlsOpen] = useState(true);
  const [cities, setCities] = useState<City[]>([]);
  const [numCities, setNumCities] = useState(25);
  const [variant, setVariant] = useState("MMAS");
  const [numAnts, setNumAnts] = useState(30);
  const [iterations, setIterations] = useState(100);
  const [alpha, setAlpha] = useState(1.0);
  const [beta, setBeta] = useState(3.0);
  const [rho, setRho] = useState(0.1);
  const [q0, setQ0] = useState(0.9);
  const [localSearch, setLocalSearch] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [status, setStatus] = useState("Idle");
  const [statusDetail, setStatusDetail] = useState("Ready to start");

  // Algorithm stats
  const [bestDistance, setBestDistance] = useState<number | null>(null);
  const [currentIteration, setCurrentIteration] = useState<number>(0);
  const [avgDistance, setAvgDistance] = useState<number | null>(null);
  const [bestPath, setBestPath] = useState<number[]>([]);
  const [pheromones, setPheromones] = useState<number[][] | null>(null);

  // Chart data
  const [convergenceData, setConvergenceData] = useState<number[]>([]);
  const [convergenceLabels, setConvergenceLabels] = useState<number[]>([]);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const socketRef = useRef<Socket | null>(null);

  // Socket.IO connection
  useEffect(() => {
    const socket = io("http://localhost:5000", {
      transports: ["websocket", "polling"],
    });

    socketRef.current = socket;

    socket.on("connect", () => {
      console.log("Connected to backend");
      setStatus("Connected");
      setStatusDetail("Ready to start");
    });

    socket.on("disconnect", () => {
      console.log("Disconnected from backend");
      setStatus("Disconnected");
      setStatusDetail("Connection lost");
    });

    socket.on("algorithm_starting", () => {
      setStatus("Running");
      setStatusDetail("Initializing...");
      setIsRunning(true);
      setConvergenceData([]);
      setConvergenceLabels([]);
    });

    socket.on("iteration_update", (data: AlgorithmData) => {
      setCurrentIteration(data.iteration);
      setBestDistance(data.best_distance);
      setAvgDistance(data.avg_distance);
      setBestPath(data.best_path);
      if (data.pheromones) {
        setPheromones(data.pheromones);
      }

      setConvergenceData(prev => [...prev, data.best_distance]);
      setConvergenceLabels(prev => [...prev, data.iteration]);
      setStatusDetail(`Iteration ${data.iteration}/${iterations}`);
    });

    socket.on("algorithm_complete", (data: any) => {
      setStatus("Complete");
      setStatusDetail(`Finished! Best: ${data.best_distance.toFixed(2)}`);
      setIsRunning(false);
      alert(`Optimization complete! Best distance: ${data.best_distance.toFixed(2)}`);
    });

    socket.on("algorithm_stopped", () => {
      setStatus("Stopped");
      setStatusDetail("Stopped by user");
      setIsRunning(false);
    });

    return () => {
      socket.disconnect();
    };
  }, [iterations]);

  // Canvas drawing
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw pheromone trails
    if (pheromones && cities.length > 0) {
      const maxPheromone = Math.max(...pheromones.flat());
      for (let i = 0; i < cities.length; i++) {
        for (let j = i + 1; j < cities.length; j++) {
          const intensity = pheromones[i][j] / maxPheromone;
          if (intensity > 0.1) {
            ctx.strokeStyle = `rgba(59, 130, 246, ${intensity * 0.3})`;
            ctx.lineWidth = intensity * 3;
            ctx.beginPath();
            ctx.moveTo(cities[i].x, cities[i].y);
            ctx.lineTo(cities[j].x, cities[j].y);
            ctx.stroke();
          }
        }
      }
    }

    // Draw best path
    if (bestPath.length > 0 && cities.length > 0) {
      ctx.strokeStyle = "#3b82f6";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(cities[bestPath[0]].x, cities[bestPath[0]].y);
      for (let i = 1; i < bestPath.length; i++) {
        ctx.lineTo(cities[bestPath[i]].x, cities[bestPath[i]].y);
      }
      ctx.lineTo(cities[bestPath[0]].x, cities[bestPath[0]].y);
      ctx.stroke();
    }

    // Draw cities
    cities.forEach((city, index) => {
      ctx.fillStyle = index === 0 && bestPath.length > 0 ? "#22c55e" : "#ef4444";
      ctx.beginPath();
      ctx.arc(city.x, city.y, 6, 0, 2 * Math.PI);
      ctx.fill();

      // Draw city number
      ctx.fillStyle = "#1f2937";
      ctx.font = "12px sans-serif";
      ctx.fillText(index.toString(), city.x - 5, city.y - 10);
    });
  }, [cities, bestPath, pheromones]);

  // Generate random cities
  const generateCities = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const newCities: City[] = [];
    const margin = 50;
    for (let i = 0; i < numCities; i++) {
      newCities.push({
        x: margin + Math.random() * (canvas.width - 2 * margin),
        y: margin + Math.random() * (canvas.height - 2 * margin),
      });
    }
    setCities(newCities);
    setBestPath([]);
    setPheromones(null);
    setConvergenceData([]);
    setConvergenceLabels([]);
    setBestDistance(null);
    setAvgDistance(null);
    setCurrentIteration(0);
  };

  // Clear cities
  const clearCities = () => {
    setCities([]);
    setBestPath([]);
    setPheromones(null);
    setConvergenceData([]);
    setConvergenceLabels([]);
    setBestDistance(null);
    setAvgDistance(null);
    setCurrentIteration(0);
  };

  // Add city on canvas click
  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    setCities([...cities, { x, y }]);
  };

  // Start optimization
  const startOptimization = () => {
    if (cities.length < 3) {
      alert("Please add at least 3 cities");
      return;
    }

    if (!socketRef.current) {
      alert("Not connected to backend");
      return;
    }

    socketRef.current.emit("start_aco", {
      cities: cities,
      variant: variant,
      n_ants: numAnts,
      n_iterations: iterations,
      alpha: alpha,
      beta: beta,
      evaporation_rate: rho,
      q0: q0,
      local_search: localSearch,
    });
  };

  // Stop optimization
  const stopOptimization = () => {
    if (socketRef.current) {
      socketRef.current.emit("stop_aco");
    }
  };

  // Chart configuration
  const chartData = {
    labels: convergenceLabels,
    datasets: [
      {
        label: "Best Distance",
        data: convergenceData,
        borderColor: "#3b82f6",
        backgroundColor: "rgba(59, 130, 246, 0.1)",
        tension: 0.1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top" as const,
      },
      title: {
        display: true,
        text: "Convergence Progress",
      },
    },
    scales: {
      y: {
        beginAtZero: false,
      },
    },
  };

  return (
    <div className="min-h-screen w-full bg-background">
      {/* Header */}
      <header className="bg-gradient-primary text-primary-foreground p-6 shadow-elevated">
        <div className="flex items-center gap-3">
          <Activity className="h-8 w-8" />
          <div>
            <h1 className="text-3xl font-bold">ACO Interactive Interface</h1>
            <p className="text-sm opacity-90">
              Visualize Ant Colony Optimization solving the Traveling Salesman Problem
            </p>
          </div>
        </div>
        <div className="mt-3 p-2 bg-primary-foreground/10 border border-primary-foreground/20 rounded text-sm">
          ℹ️ Connected to Flask backend on localhost:5000 via WebSocket
        </div>
      </header>

      <main className="p-6 max-w-[1800px] mx-auto space-y-6">
        {/* Collapsible Controls Section */}
        <div className="border border-border rounded-lg bg-card shadow-card overflow-hidden">
          <button
            onClick={() => setIsControlsOpen(!isControlsOpen)}
            className="w-full px-6 py-4 flex items-center justify-between bg-gradient-card hover:bg-muted/50 transition-colors"
          >
            <h2 className="text-lg font-semibold text-foreground">Algorithm Controls</h2>
            {isControlsOpen ? (
              <ChevronUp className="h-5 w-5 text-muted-foreground" />
            ) : (
              <ChevronDown className="h-5 w-5 text-muted-foreground" />
            )}
          </button>

          <div
            className={`transition-all duration-300 ease-in-out ${
              isControlsOpen ? "max-h-[800px] opacity-100" : "max-h-0 opacity-0"
            } overflow-hidden`}
          >
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Problem Setup */}
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-3 text-foreground">Problem Setup</h3>
                  <p className="text-xs text-muted-foreground mb-4">Configure the TSP instance</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-foreground">Number of Cities</label>
                  <input
                    type="number"
                    value={numCities}
                    onChange={(e) => setNumCities(Number(e.target.value))}
                    min={5}
                    max={100}
                    className="w-full mt-1 px-3 py-2 bg-background border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
                <button
                  onClick={generateCities}
                  className="w-full bg-gradient-primary text-primary-foreground py-2 px-4 rounded-md text-sm font-medium hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
                >
                  <Shuffle className="h-4 w-4" />
                  Generate Random Cities
                </button>
                <button
                  onClick={clearCities}
                  className="w-full border border-border bg-background py-2 px-4 rounded-md text-sm font-medium hover:bg-muted transition-colors flex items-center justify-center gap-2"
                >
                  <Trash2 className="h-4 w-4" />
                  Clear All Cities
                </button>
              </div>

              {/* Algorithm Settings */}
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-3 text-foreground">Algorithm Settings</h3>
                  <p className="text-xs text-muted-foreground mb-4">Configure ACO parameters</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-foreground">ACO Variant</label>
                  <select
                    value={variant}
                    onChange={(e) => setVariant(e.target.value)}
                    className="w-full mt-1 px-3 py-2 bg-background border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    <option value="MMAS">MMAS</option>
                    <option value="ACS">ACS</option>
                    <option value="RANK">Rank-based AS</option>
                    <option value="AS">Basic AS</option>
                  </select>
                </div>
                <div className="p-3 bg-muted/50 rounded-md text-xs text-muted-foreground">
                  {variant === "MMAS" && "Uses pheromone bounds [τ_min, τ_max] to prevent premature convergence."}
                  {variant === "ACS" && "Uses pseudo-random proportional rule with local pheromone update."}
                  {variant === "RANK" && "Updates pheromones based on ranked solutions."}
                  {variant === "AS" && "Classic Ant System algorithm."}
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-sm font-medium text-foreground">Ants</label>
                    <input
                      type="number"
                      value={numAnts}
                      onChange={(e) => setNumAnts(Number(e.target.value))}
                      min={1}
                      max={100}
                      className="w-full mt-1 px-3 py-2 bg-background border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-foreground">Iterations</label>
                    <input
                      type="number"
                      value={iterations}
                      onChange={(e) => setIterations(Number(e.target.value))}
                      min={10}
                      max={500}
                      className="w-full mt-1 px-3 py-2 bg-background border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-sm font-medium text-foreground">Alpha (α)</label>
                    <input
                      type="number"
                      value={alpha}
                      onChange={(e) => setAlpha(Number(e.target.value))}
                      min={0}
                      max={5}
                      step={0.1}
                      className="w-full mt-1 px-3 py-2 bg-background border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-foreground">Beta (β)</label>
                    <input
                      type="number"
                      value={beta}
                      onChange={(e) => setBeta(Number(e.target.value))}
                      min={0}
                      max={10}
                      step={0.1}
                      className="w-full mt-1 px-3 py-2 bg-background border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-sm font-medium text-foreground">Evaporation (ρ)</label>
                    <input
                      type="number"
                      value={rho}
                      onChange={(e) => setRho(Number(e.target.value))}
                      min={0}
                      max={1}
                      step={0.01}
                      className="w-full mt-1 px-3 py-2 bg-background border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                  </div>
                  {variant === "ACS" && (
                    <div>
                      <label className="text-sm font-medium text-foreground">Q0</label>
                      <input
                        type="number"
                        value={q0}
                        onChange={(e) => setQ0(Number(e.target.value))}
                        min={0}
                        max={1}
                        step={0.1}
                        className="w-full mt-1 px-3 py-2 bg-background border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                      />
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="localSearch"
                    checked={localSearch}
                    onChange={(e) => setLocalSearch(e.target.checked)}
                    className="w-4 h-4 rounded border-input"
                  />
                  <label htmlFor="localSearch" className="text-sm font-medium text-foreground">
                    Enable 2-opt Local Search
                  </label>
                </div>
              </div>

              {/* Control & Status */}
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-3 text-foreground">Control & Status</h3>
                  <p className="text-xs text-muted-foreground mb-4">Start and monitor the algorithm</p>
                </div>
                <button
                  onClick={startOptimization}
                  disabled={isRunning}
                  className="w-full bg-gradient-success text-success-foreground py-3 px-4 rounded-md text-sm font-medium hover:opacity-90 transition-opacity flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Play className="h-4 w-4" />
                  Start Optimization
                </button>
                <button
                  onClick={stopOptimization}
                  disabled={!isRunning}
                  className="w-full bg-destructive text-destructive-foreground py-3 px-4 rounded-md text-sm font-medium hover:opacity-90 transition-opacity flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <StopCircle className="h-4 w-4" />
                  Stop Algorithm
                </button>
                <div className="flex items-center gap-3 p-4 bg-muted/50 rounded-md border border-border">
                  <div className={`w-3 h-3 rounded-full ${
                    status === "Running" ? "bg-success animate-pulse" :
                    status === "Complete" ? "bg-success" :
                    status === "Stopped" ? "bg-destructive" :
                    status === "Disconnected" ? "bg-destructive" :
                    "bg-muted-foreground"
                  }`} />
                  <div>
                    <div className="text-sm font-medium text-foreground">{status}</div>
                    <div className="text-xs text-muted-foreground">{statusDetail}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: "Best Distance", value: bestDistance !== null ? bestDistance.toFixed(2) : "—" },
            { label: "Current Iteration", value: currentIteration > 0 ? `${currentIteration}/${iterations}` : "—" },
            { label: "Average Distance", value: avgDistance !== null ? avgDistance.toFixed(2) : "—" },
            { label: "Cities", value: cities.length.toString() },
          ].map((stat, i) => (
            <div
              key={i}
              className="bg-gradient-card shadow-card border-border/50 border rounded-lg p-4 animate-fade-in"
              style={{ animationDelay: `${i * 0.05}s` }}
            >
              <div className="text-sm font-medium text-muted-foreground mb-1">{stat.label}</div>
              <div className="text-2xl font-bold text-foreground">{stat.value}</div>
            </div>
          ))}
        </div>

        {/* Canvas */}
        <div className="border-2 border-border rounded-lg overflow-hidden shadow-elevated bg-card animate-fade-in">
          <canvas
            ref={canvasRef}
            width={900}
            height={600}
            onClick={handleCanvasClick}
            className="w-full h-auto cursor-crosshair bg-background"
          />
          <div className="p-3 bg-muted/50 border-t border-border">
            <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-destructive" />
                <span>Cities</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-success" />
                <span>Start City</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-0.5 bg-primary" />
                <span>Best Tour</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-0.5 bg-primary/30" />
                <span>Pheromones</span>
              </div>
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="h-[300px] bg-card border border-border rounded-lg p-4 shadow-card animate-fade-in">
          {convergenceData.length > 0 ? (
            <Line data={chartData} options={chartOptions} />
          ) : (
            <div className="h-full flex items-center justify-center text-muted-foreground">
              Convergence chart will appear when optimization starts
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Index;

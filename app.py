from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import numpy as np
import json
from advanced_aco import AdvancedACO, ACOVariant, generate_random_cities
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aco-visualization-secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
current_aco = None
is_running = False
stop_requested = False


def numpy_to_json(obj):
    """Convert numpy types to JSON-serializable types."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: numpy_to_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [numpy_to_json(item) for item in obj]
    return obj


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/generate_cities', methods=['POST'])
def generate_cities():
    """Generate random cities."""
    data = request.json
    n_cities = data.get('n_cities', 20)
    width = data.get('width', 800)
    height = data.get('height', 600)
    seed = data.get('seed', None)

    cities = generate_random_cities(n_cities, width, height, seed)

    return jsonify({
        'cities': cities.tolist()
    })


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('connection_response', {'data': 'Connected to ACO server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    global stop_requested
    print('Client disconnected')
    stop_requested = True


@socketio.on('start_aco')
def handle_start_aco(data):
    """Start ACO algorithm with given parameters."""
    global current_aco, is_running, stop_requested

    if is_running:
        emit('error', {'message': 'Algorithm is already running'})
        return

    try:
        # Parse parameters
        cities = np.array(data['cities'])
        variant_name = data.get('variant', 'MMAS')
        n_ants = data.get('n_ants', 20)
        n_iterations = data.get('n_iterations', 100)
        alpha = data.get('alpha', 1.0)
        beta = data.get('beta', 3.0)
        evaporation_rate = data.get('evaporation_rate', 0.1)
        q0 = data.get('q0', 0.9)
        local_search = data.get('local_search', True)

        # Map variant name to enum
        variant_map = {
            'AS': ACOVariant.AS,
            'ACS': ACOVariant.ACS,
            'MMAS': ACOVariant.MMAS,
            'RANK': ACOVariant.RANK
        }
        variant = variant_map.get(variant_name, ACOVariant.MMAS)

        # Create callback for real-time updates
        def iteration_callback(iteration_data):
            if stop_requested:
                return

            # Convert numpy types to JSON-serializable
            data_to_send = numpy_to_json(iteration_data)

            # Add pheromone matrix for visualization
            data_to_send['pheromones'] = numpy_to_json(current_aco.pheromones)

            socketio.emit('iteration_update', data_to_send)
            time.sleep(0.01)  # Small delay for visualization

        # Create ACO instance
        current_aco = AdvancedACO(
            cities=cities,
            variant=variant,
            n_ants=n_ants,
            n_iterations=n_iterations,
            alpha=alpha,
            beta=beta,
            evaporation_rate=evaporation_rate,
            q0=q0,
            local_search=local_search,
            callback=iteration_callback
        )

        # Run algorithm in separate thread
        def run_algorithm():
            global is_running, stop_requested
            is_running = True
            stop_requested = False

            try:
                emit('algorithm_started', {'message': 'Algorithm started'})
                best_path, best_distance = current_aco.solve(verbose=False)

                if not stop_requested:
                    result = {
                        'best_path': numpy_to_json(best_path),
                        'best_distance': float(best_distance),
                        'statistics': numpy_to_json(current_aco.get_statistics())
                    }
                    socketio.emit('algorithm_complete', result)
            except Exception as e:
                socketio.emit('error', {'message': str(e)})
            finally:
                is_running = False

        thread = threading.Thread(target=run_algorithm)
        thread.start()

    except Exception as e:
        emit('error', {'message': f'Error starting algorithm: {str(e)}'})
        is_running = False


@socketio.on('stop_aco')
def handle_stop_aco():
    """Stop the running algorithm."""
    global stop_requested
    stop_requested = True
    emit('algorithm_stopped', {'message': 'Algorithm stopped'})


@socketio.on('get_status')
def handle_get_status():
    """Get current algorithm status."""
    emit('status_update', {
        'is_running': is_running,
        'current_iteration': current_aco.current_iteration if current_aco else 0
    })


if __name__ == '__main__':
    print("=" * 80)
    print("ACO VISUALIZATION SERVER")
    print("=" * 80)
    print("\nServer starting on http://localhost:5000")
    print("Open your browser and navigate to the URL above")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 80)

    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)

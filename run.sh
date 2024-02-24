#!/bin/bash

# Function to handle SIGINT
function handle_sigint {
    echo "Terminating all child processes..."
    pkill -P $$  # Send SIGINT to all child processes
    pkill -f "python3 main.py"  # Kill all Python processes started by the script
    pkill -f "python3 server.py"  # Kill the file server process
    killall -9 Python  # Force quit Atom editor
    exit 0
}

# Trap SIGINT and call the handle_sigint function
trap handle_sigint SIGINT

# Start file server in the background
python3 server.py &

# Store PID of file server
server_pid=$!

# Start 4 instances of the Python script in parallel
for i in {1..4}; do
    sleep 0.1
    python3 main.py &
done

# Wait for all child processes to finish
wait

# Terminate the file server
kill $server_pid

# Terminate all Python processes started by the script
pkill -f "python3 main.py"
pkill -f "python3 server.py"

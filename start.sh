#!/bin/bash

# Start the backend
echo "Starting backend server..."
cd backend
python simple_app.py &
BACKEND_PID=$!

# Start the frontend
echo "Starting frontend server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

# Function to handle exit
function cleanup {
  echo "Stopping servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  exit
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

echo "Both servers are running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop both servers"

# Wait for user to press Ctrl+C
wait 
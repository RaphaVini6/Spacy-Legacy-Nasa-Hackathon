#!/bin/sh
# Starts the two APIs in the background (only reachable inside the container)
# and the backend on the public port Render gives us ($PORT).
set -e

(cd /app/vlibras && ASPNETCORE_URLS=http://127.0.0.1:5001 exec dotnet Api1.VLibras.dll) &
(cd /app/speech && ASPNETCORE_URLS=http://127.0.0.1:5002 exec dotnet Api2.Speech.dll) &

cd /app/backend
export ASPNETCORE_URLS="http://0.0.0.0:${PORT:-10000}"
exec dotnet Backend.dll

# Backend + the two APIs in one container, for hosting on Render (free plan).
# Render gives one public port per service and puts idle services to sleep, so running the three
# processes together means they wake up together. Build context: the repo root.

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY backend/Backend.csproj backend/
COPY api-1-vlibras/Api1.VLibras.csproj api-1-vlibras/
COPY api-2-speech/Api2.Speech.csproj api-2-speech/
RUN dotnet restore backend/Backend.csproj \
 && dotnet restore api-1-vlibras/Api1.VLibras.csproj \
 && dotnet restore api-2-speech/Api2.Speech.csproj
COPY backend/ backend/
COPY api-1-vlibras/ api-1-vlibras/
COPY api-2-speech/ api-2-speech/
RUN dotnet publish backend/Backend.csproj -c Release -o /app/backend --no-restore \
 && dotnet publish api-1-vlibras/Api1.VLibras.csproj -c Release -o /app/vlibras --no-restore \
 && dotnet publish api-2-speech/Api2.Speech.csproj -c Release -o /app/speech --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app
COPY --from=build /app .
COPY deploy/render/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# the backend reaches the APIs inside the container
ENV Apis__VLibras__BaseUrl=http://127.0.0.1:5001 \
    Apis__Speech__BaseUrl=http://127.0.0.1:5002 \
    Speech__CacheDir=/tmp/audio-cache \
    DOTNET_gcServer=0

USER $APP_UID
CMD ["/app/start.sh"]

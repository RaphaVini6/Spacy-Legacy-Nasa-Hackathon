# Third-party licenses

Every tool, library, service and data source used by Spacy Legacy, with its license.
Versions and licenses were read from the packages themselves (`node_modules/*/package.json`,
NuGet `.nuspec`, GitHub license API) on 2026-11-15. The same list is shown on the website at `/licenses`
(source: `frontend/src/data/licenses.js` - keep both in sync when adding a dependency).

## Frontend (`frontend/package.json`)

| Package | Version | License |
|---|---|---|
| react, react-dom | 19.3.1 | MIT |
| react-router-dom | 7.18.5 | MIT |
| motion | 14.14.0 | MIT |
| i18next | 27.1.1 | MIT |
| react-i18next | 18.0.1 | MIT |
| i18next-browser-languagedetector | 8.3.0 | MIT |
| axios | 1.21.1 | MIT |
| leaflet | 1.9.4 | BSD-2-Clause |
| lucide-react | 1.73.0 | ISC |
| @fontsource-variable/inter | 5.3.0 | OFL-1.1 |
| @fontsource-variable/space-grotesk | 5.3.0 | OFL-1.1 |
| @fontsource-variable/league-spartan | 5.3.0 | OFL-1.1 |
| @fontsource/tenor-sans | 5.3.0 | OFL-1.1 |

Build tools (dev only): vite 8.3.8 (MIT), @vitejs/plugin-react 6.3.0 (MIT), oxlint 1.93.0 (MIT),
@types/react and @types/react-dom 19.3.0 (MIT).

Blender 5.3 (GPL-3.0) renders the simulator part images with `tools/render-parts/render_parts.py`.
Images made with Blender belong to their author; the GPL only covers the Blender program.

> `react-leaflet` was **not** used on purpose: its Hippocratic-2.1 license is not an OSI-approved
> open-source license. The map uses Leaflet directly.

## Backend and APIs (`*.csproj`)

| Package | Version | License |
|---|---|---|
| .NET 10 / ASP.NET Core | 10.0 | MIT |
| Microsoft.AspNetCore.OpenApi | 10.0.15 | MIT |
| Scalar.AspNetCore | 2.21.0 | MIT |
| System.Speech (api-2-speech) | 11.0.0 | MIT |
| DotNetEnv | 3.2.0 | MIT |

## External services

| Service | Used for | License / terms |
|---|---|---|
| VLibras (gov.br) widget and API | Libras translation | LGPL-3.0 ([spbgovbr-vlibras](https://github.com/spbgovbr-vlibras/vlibras-web-browsers)) |
| NASA Moon Trek / Mars Trek tiles | maps on the artifact pages | NASA data ([trek.nasa.gov](https://trek.nasa.gov/)) |
| Knowlez TTS / Azure Speech | audio narration | commercial services, used through their APIs (no code included) |

## Images and data

- **NASA images**: generally not copyrighted; used following the
  [NASA media usage guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/).
  The origin of every image (photo, NASA illustration, NASA diagram or team illustration), its credit and
  link are in `backend/Data/images.json` and are shown on the site when the image is clicked.
- **Simulator part renders** (`frontend/public/images/hardware/`): modeled and rendered by the team in Blender,
  inspired by the real hardware listed in `backend/Data/components.json`.
- **Team illustrations**: created by the team with an AI image tool (gpt-6) from NASA documents, and marked
  "AI-generated (gpt-6)" on the image; each one links to the
  NASA reference used.
- **Mission data**: NASA Space Science Data Coordinated Archive (NSSDCA) and official NASA/JPL pages,
  linked from each artifact and from each simulator component (`backend/Data/components.json`).

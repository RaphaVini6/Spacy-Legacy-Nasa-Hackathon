// Third-party software, services and data used by the project, with their licenses.
// Versions and licenses were read from each package (node_modules/*/package.json, NuGet .nuspec, GitHub) on 2026-11-15.
// Keep in sync with frontend/package.json, the *.csproj files and THIRD_PARTY_LICENSES.md.

export const SOFTWARE = [
  {
    group: 'frontend',
    items: [
      { name: 'React / React DOM', version: '19.3.1', license: 'MIT', url: 'https://github.com/react/react' },
      { name: 'React Router', version: '7.18.5', license: 'MIT', url: 'https://github.com/remix-run/react-router' },
      { name: 'Motion', version: '14.14.0', license: 'MIT', url: 'https://github.com/motiondivision/motion' },
      { name: 'i18next', version: '27.1.1', license: 'MIT', url: 'https://github.com/i18next/i18next' },
      { name: 'react-i18next', version: '18.0.1', license: 'MIT', url: 'https://github.com/i18next/react-i18next' },
      { name: 'i18next-browser-languagedetector', version: '8.3.0', license: 'MIT', url: 'https://github.com/i18next/i18next-browser-languageDetector' },
      { name: 'Axios', version: '1.21.1', license: 'MIT', url: 'https://github.com/axios/axios' },
      { name: 'Leaflet', version: '1.9.4', license: 'BSD-2-Clause', url: 'https://github.com/Leaflet/Leaflet' },
      { name: 'Lucide icons (lucide-react)', version: '1.73.0', license: 'ISC', url: 'https://github.com/lucide-icons/lucide' },
      { name: 'Inter (Fontsource)', version: '5.3.0', license: 'OFL-1.1', url: 'https://fontsource.org/fonts/inter' },
      { name: 'Space Grotesk (Fontsource)', version: '5.3.0', license: 'OFL-1.1', url: 'https://fontsource.org/fonts/space-grotesk' },
      { name: 'League Spartan (Fontsource)', version: '5.3.0', license: 'OFL-1.1', url: 'https://fontsource.org/fonts/league-spartan' },
      { name: 'Tenor Sans (Fontsource)', version: '5.3.0', license: 'OFL-1.1', url: 'https://fontsource.org/fonts/tenor-sans' },
    ],
  },
  {
    group: 'build',
    items: [
      { name: 'Vite', version: '8.3.8', license: 'MIT', url: 'https://github.com/vitejs/vite' },
      { name: '@vitejs/plugin-react', version: '6.3.0', license: 'MIT', url: 'https://github.com/vitejs/vite-plugin-react' },
      { name: 'Oxlint', version: '1.93.0', license: 'MIT', url: 'https://github.com/oxc-project/oxc' },
      { name: 'Blender (renders of the simulator parts)', version: '5.3', license: 'GPL-3.0', url: 'https://www.blender.org/about/license/' },
    ],
  },
  {
    group: 'backend',
    items: [
      { name: '.NET 10 / ASP.NET Core', version: '10.0', license: 'MIT', url: 'https://github.com/dotnet/aspnetcore' },
      { name: 'Microsoft.AspNetCore.OpenApi', version: '10.0.15', license: 'MIT', url: 'https://github.com/dotnet/aspnetcore' },
      { name: 'Scalar.AspNetCore', version: '2.21.0', license: 'MIT', url: 'https://github.com/scalar/scalar' },
      { name: 'System.Speech', version: '11.0.0', license: 'MIT', url: 'https://github.com/dotnet/runtime' },
      { name: 'DotNetEnv', version: '3.2.0', license: 'MIT', url: 'https://github.com/tonerdo/dotnet-env' },
    ],
  },
  {
    group: 'services',
    items: [
      { name: 'VLibras (gov.br) widget and API', version: '-', license: 'LGPL-3.0', url: 'https://github.com/spbgovbr-vlibras/vlibras-web-browsers' },
    ],
  },
]

// images, maps and data: not software licenses, but the terms that allow us to use them
export const CONTENT = [
  { key: 'nasaMedia', url: 'https://www.nasa.gov/nasa-brand-center/images-and-media/' },
  { key: 'trek', url: 'https://trek.nasa.gov/' },
  { key: 'nssdca', url: 'https://nssdc.gsfc.nasa.gov/' },
  { key: 'teamImages', url: null },
]

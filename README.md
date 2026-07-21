🎧📡 icyarr Ecosystem — Metadata, Frontend, Tickarr, and Future Game ModeA modular, future‑ready metadata system powering radio streams, IPTV overlays, and dynamic sports experiences.📌 OverviewThis project is a multi‑component ecosystem built around icyarr, a lightweight metadata engine designed to enhance radio/IPTV streams with rich, dynamic information. It integrates cleanly with:Dispatcharr (channels + EPG)Tickarr (FFmpeg overlays)A custom frontend (UI for streams + metadata)XMLTV guide files (KGVO schedule, Griz Football)ESPN API (Tickarr sports ticker)Everything is modular.
Nothing is tightly coupled.
And the entire system is designed so future features can be dropped in without breaking anything.🧊 Current Components1. icyarr (Backend Metadata Engine)Handles:Now Playing metadataTickarr text endpoint (/tickarr_text)Local streams listM3U export (/export_m3u)Clean FastAPI architectureDoes not yet handle:XMLTV parsingLocal Game ModeESPN score filteringTickarr trigger integrationicyarr is stable and ready for future expansion.2. Frontend (UI Layer)Provides:Channel listMetadata displayStream managementClean separation from backend logicFuture‑ready for:Local Game Mode indicatorsXMLTV programme displayESPN score displayUnified ticker preview3. Dispatcharr (Organizer + EPG)Currently:Uses XMLTV guide (KGVO)Displays full Griz Football scheduleProvides FFmpeg profiles for TickarrNo icyarr integration yet — by design.4. Tickarr (Overlay Engine)Currently supports:Sports ticker (ESPN API)Custom text overlaysSatellite radio Now PlayingWeather alertsFFmpeg profile cloningFuture‑ready for:Local Game Mode triggerXMLTV‑aware overlaysicyarr metadata merging🏈 Future Feature: Local Game Mode (Designed, Not Implemented)Local Game Mode is a planned enhancement that activates only when KGVO is streaming a Griz Football game.
It merges three data sources:✔ ESPN score for the Griz game✔ icyarr metadata (booth info, stream title)✔ XMLTV programme title (e.g., “Griz Football: Idaho at Montana”)This creates a unified ticker:CopyGriz Football: Southern Utah at Montana • Score: MT 21, SUU 17 • Riley Corcoran & Greg Sundberg • Postgame at 10 PMStatus:🟦 Designed
⬜ Not implemented
🟦 Fully documented
⬜ Not activated
🟦 Ready to drop in later📁 Future‑Ready Files (Included in this repo)1. local_game_status.jsonDefines the API contract icyarr will expose.2. xmltv_game_detector.pyParses XMLTV and detects live Griz Football games.3. tickarr_local_game_mode.mdSpecifies how Tickarr will activate Local Game Mode.These files are not active, but they are ready for future integration.🧱 Architecture DiagramCopy┌──────────────────────────────┐
│          FRONTEND            │
│  UI for streams + metadata   │
│  (future: game status UI)    │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│            icyarr             │
│  Metadata engine              │
│  /tickarr_text                │
│  /export_m3u                  │
│  (future: /local_game_status) │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│            Tickarr            │
│  FFmpeg overlays              │
│  Sports ticker (ESPN)         │
│  (future: Local Game Mode)    │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│          Dispatcharr          │
│  Channels + XMLTV EPG         │
└───────────────────────────────┘🌟 PhilosophyThis project follows three principles:1. ModularityEach component stands alone.
No forced integration.
No tight coupling.2. Future‑proofingFeatures are designed early, implemented later.
Nothing breaks the current system.3. Drop‑in architectureWhen the app is ready, new modules can be added with minimal changes.🚀 RoadmapShort‑termContinue stabilizing icyarrExpand frontend UIAdd more local streamsMid‑termAdd XMLTV parsing to icyarrAdd /local_game_status endpointAdd frontend game status displayLong‑termImplement Tickarr Local Game ModeMerge ESPN + XMLTV + icy metadataUnified Griz Football experience❤️ CreditsBuilt with care by Randall —
a modular, elegant, future‑ready ecosystem for radio, IPTV, and sports metadata.If you want, I can also generate:A CONTRIBUTING.mdA ROADMAP.mdA folder structure for the repoJust tap whichever you want next.

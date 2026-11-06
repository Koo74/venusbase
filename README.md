# 🪐 VenusBase v2.7.0

<div align="center">

![VenusBase Banner](https://img.shields.io/badge/🪐_VENUSBASE-Floating_Base_Selector-ffb84d?style=for-the-badge&logo=nasa&logoColor=white)

**The first interactive site selector for a Venus floating cloud city.**  
Built with real NASA/USGS Magellan radar data, real atmospheric physics, and a cyberpunk UI.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://venusbase.streamlit.app)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![NASA Data](https://img.shields.io/badge/Data-NASA%2FUSGS_Magellan-0B3D91?style=flat-square&logo=nasa&logoColor=white)](https://astrogeology.usgs.gov/search/map/venus-magellan-global-c3-mdir-colorized-topographic-mosaic-6600m)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=flat-square)](http://makeapullrequest.com)

### 🚀 **[LAUNCH VENUSBASE ON STREAMLIT](https://venusbase.streamlit.app)**
<a href="https://buymeacoffee.com/stargazex" target="_blank"> <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" > </a>

</div>

---

## 🌍 Why Venus?

Everyone thinks Venus is a hellscape. And on the surface, it is: **464°C, 92 atm of pressure, and sulfuric acid rain.** No rover will survive there. No human can walk there.

But at **50 km above the surface**, in the cloud deck, the story completely changes:

| Metric | Venus Surface | Venus Cloud Deck (50 km) | Earth | Mars Surface |
| :--- | :---: | :---: | :---: | :---: |
| **Pressure** | 92 atm 💀 | **1 atm** ✅ | 1 atm | 0.006 atm |
| **Temperature** | 464°C 💀 | **~30°C** ✅ | ~15°C | -60°C |
| **Gravity** | 0.9 G ✅ | **0.9 G** ✅ | 1.0 G | 0.38 G |
| **Radiation** | High | **Low (shielded by clouds)** ✅ | Low | Very High 💀 |

**VenusBase** was built to prove that the Venusian cloud deck is the most Earth-like environment in the solar system—and to find the best place to build a floating colony there.
<a href="https://www.buymeacoffee.com/stargazex" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" 
       alt="Buy Me A Coffee" 
       height="41" 
       width="174">
</a>
---

## ✨ Features

### 🗺️ Interactive Radar Map
- **High-Res NASA Data:** Uses the USGS Magellan Colorized Topographic Mosaic (loaded instantly via Base64 caching).
- **Click Anywhere:** Click any point on Venus to generate a custom site analysis on the fly.
- **20+ Pre-Loaded Sites:** Includes Ishtar Terra, Aphrodite Terra, Cleopatra Crater, Hecate Chasma, and more.

### 🚀 The Science Engine
- **Delta-V Calculator:** Proves that launching from the 50 km cloud deck saves **~18,500 m/s** of velocity—allowing **3.5× more payload** to orbit compared to a surface launch.
- **Live Climate Model:** Interpolates the ESA Venus Climate Database to show real temperature, pressure, wind speed, and density at any altitude.
- **8-Score Suitability Matrix:** Evaluates Cloud Altitude, Acid Risk, Wind Shear, Solar Power, UV Shielding, Lightning, Volcanic Activity, and Comm Delay.

### 🧪 Simulation Lab
- Adjust **Crew Size**, **Habitat Mass**, and **Power Source** to see how the mission scales.
- Real-time calculation of aerostat **envelope volume**, **air/water needs**, and **updated costs**.

### 🛰️ Live NASA Tracking
- **3D Venus Trek:** Direct link to NASA's official 3D visualization portal.
- **Live Solar System Tracker:** Embedded **NASA Eyes on the Solar System** shows the real-time positions of all active NASA missions in 3D.

### 🧠 Agent Memory
- Every analysis is stored in a local SQLite database.
- Browse past analyses in the **Memory Explorer** tab.
☕ Support the Project
If you enjoyed building your cloud city on Venus, consider buying me a coffee. It fuels the next planetary dashboard!

<a href="https://buymeacoffee.com/stargazex" target="_blank"> <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" > </a>

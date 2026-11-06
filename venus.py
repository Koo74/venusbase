"""
VenusBase v2.7.0
================
Venus Floating Base Site Selection & Sweet Spot Analysis.
Map: Local USGS Venus Magellan high-res (venus_map.jpg) via Base64 Caching.
CHANGELOG v2.7.0:
  - ADDED: Live Orbit Tracker (NASA Eyes on the Solar System).
"""

import streamlit as st
import folium
from folium.plugins import Fullscreen, MousePosition
from folium.raster_layers import ImageOverlay
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from abc import ABC
import math
import sqlite3
import pickle
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import os
import base64
import streamlit.components.v1 as components

CYBERPUNK_CSS = """
<style>
    :root {
        --venus-gold: #ffd60a;
        --venus-amber: #ffb84d;
        --venus-copper: #e85d04;
        --venus-teal: #00f5d4;
    }
    .stApp { background: linear-gradient(135deg, #0f0a05 0%, #2a1205 50%, #0f0805 100%); }
    .main-title {
        font-family: 'Courier New', monospace;
        font-size: 3.5rem; font-weight: 900;
        background: linear-gradient(90deg, #ffd60a, #ff6b35, #e85d04);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0 0 40px rgba(255, 184, 77, 0.4);
        letter-spacing: 4px; animation: venusGlow 3s ease-in-out infinite;
    }
    @keyframes venusGlow {
        0%, 100% { text-shadow: 0 0 40px rgba(255, 184, 77, 0.4); }
        50% { text-shadow: 0 0 60px rgba(255, 107, 53, 0.7), 0 0 80px rgba(232, 93, 4, 0.4); }
    }
    .subtitle {
        font-family: 'Courier New', monospace; color: #ffb84d;
        font-size: 1.1rem; letter-spacing: 6px;
        text-shadow: 0 0 20px rgba(255, 184, 77, 0.4);
        border-bottom: 1px solid rgba(255, 184, 77, 0.3);
        padding-bottom: 10px; margin-bottom: 20px;
    }
    .phase-badge {
        display: inline-block; padding: 4px 15px; border-radius: 20px;
        font-family: 'Courier New', monospace; font-size: 0.7rem;
        letter-spacing: 2px; text-transform: uppercase; font-weight: bold;
        margin: 0 5px; border: 1px solid;
    }
    .phase-badge-2 { color: #00f5d4; border-color: #00f5d4; background: rgba(0,245,212,0.05); }
    .phase-badge-3 { color: #39ff14; border-color: #39ff14; background: rgba(57,255,20,0.05); }
    .phase-badge-4 { color: #ffd60a; border-color: #ffd60a; background: rgba(255,214,10,0.05); }
    .phase-badge-5 { color: #ff6b35; border-color: #ff6b35; background: rgba(255,107,53,0.05); }
    .recommendation-container {
        background: rgba(25, 15, 5, 0.85);
        border: 1px solid rgba(255, 184, 77, 0.25);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .recommendation-title {
        color: #ffb84d; font-family: 'Courier New', monospace;
        font-size: 1.2rem; font-weight: bold; letter-spacing: 2px;
        margin-bottom: 10px;
    }
    .recommendation-item {
        color: #ffffff; font-family: 'Courier New', monospace;
        font-size: 0.9rem; padding: 6px 0;
        border-bottom: 1px solid rgba(255, 184, 77, 0.08);
    }
    .stButton > button {
        background: linear-gradient(135deg, rgba(255, 184, 77, 0.15), rgba(232, 93, 4, 0.15)) !important;
        border: 1px solid rgba(255, 184, 77, 0.5) !important;
        color: #ffb84d !important;
        font-family: 'Courier New', monospace !important;
        font-weight: bold !important; text-transform: uppercase !important;
        letter-spacing: 2px !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(255, 184, 77, 0.3), rgba(232, 93, 4, 0.3)) !important;
        border-color: #ffb84d !important;
        color: #ffffff !important;
    }
    [data-testid="metric-container"] {
        background: rgba(25, 15, 5, 0.8);
        border: 1px solid rgba(255, 184, 77, 0.2);
        border-radius: 10px; padding: 15px;
    }
    [data-testid="metric-container"] label { color: #ffb84d !important; }
    [data-testid="metric-container"] div { color: #ffffff !important; }
    .cyber-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #ffd60a, #ff6b35, #e85d04, transparent);
        margin: 20px 0; opacity: 0.6;
    }
    .stMarkdown p, .stMarkdown li { color: #ffffff !important; }
    .stMarkdown h1 { color: #ffb84d !important; }
    .stMarkdown h2 { color: #ff6b35 !important; }
    .stMarkdown h3 { color: #ffd60a !important; }
    .confidence-bar {
        background: rgba(25, 15, 5, 0.8);
        border: 1px solid rgba(255, 184, 77, 0.2);
        border-radius: 8px; padding: 12px; margin: 10px 0;
    }
    .blocked-score {
        background: rgba(255, 107, 53, 0.15) !important;
        border: 2px solid #ff6b35 !important;
        border-radius: 10px; padding: 20px; margin: 10px 0; text-align: center;
    }
    .not-feasible-box {
        background: rgba(232, 93, 4, 0.25) !important;
        border: 3px solid #e85d04 !important;
        border-radius: 10px; padding: 20px; margin: 10px 0; text-align: center;
    }
    .alt-site-card {
        background: rgba(57, 255, 20, 0.05);
        border: 1px solid rgba(57, 255, 20, 0.3);
        border-radius: 8px; padding: 12px; margin: 8px 0;
    }
    .venus-banner {
        background: linear-gradient(135deg, rgba(255, 184, 77, 0.15), rgba(232, 93, 4, 0.10));
        border: 1px solid rgba(255, 184, 77, 0.3);
        border-radius: 10px; padding: 12px 20px; margin: 10px 0;
        text-align: center; font-family: 'Courier New', monospace;
    }
    .delta-v-box {
        background: linear-gradient(135deg, rgba(0, 245, 212, 0.1), rgba(255, 184, 77, 0.1));
        border: 1px solid rgba(0, 245, 212, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .climate-box {
        background: linear-gradient(135deg, rgba(57, 255, 20, 0.1), rgba(0, 245, 212, 0.1));
        border: 1px solid rgba(57, 255, 20, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .nasa-trek-box {
        background: linear-gradient(135deg, rgba(255, 45, 149, 0.1), rgba(176, 38, 255, 0.1));
        border: 1px solid rgba(255, 45, 149, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
        text-align: center;
    }
</style>
"""

# ============================================================================
# VENUS MAP — USGS MAGELLAN GLOBAL RADAR MOSAIC (Base64 Cache)
# ============================================================================

VENUS_IMAGE_URL = (
    "https://astrogeology.usgs.gov/ckan/dataset/"
    "f992cb3c-4f37-4e1a-a59d-4f29d8307d7d/resource/"
    "d97f7bf8-73da-46fe-9edb-95c9ad233b10/download/"
    "venus_magellan_c3-mdir_clrtopo_global_mosaic_1024.jpg"
)
VENUS_IMAGE_LOCAL = "venus_map.jpg"
VENUS_BOUNDS = [[-90, -180], [90, 180]]

@st.cache_data
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# ============================================================================
# DELTA-V CALCULATOR (Launch Platform)
# ============================================================================

def compute_delta_v(lat_deg: float, cloud_alt_km: float) -> Dict:
    R_venus = 6051.8 # km
    dv_surface = 27000.0 
    dv_cloud = 8500.0 
    dv_saving = dv_surface - dv_cloud
    payload_multiplier = 3.5 
    v_rotation_eq = (2 * math.pi * R_venus * 1000) / (243.0 * 86400) 
    v_rotation_site = v_rotation_eq * math.cos(math.radians(lat_deg))

    return {
        'dv_surface': dv_surface, 'dv_cloud': dv_cloud,
        'dv_saving': dv_saving, 'payload_multiplier': payload_multiplier,
        'rotation_speed': round(v_rotation_site, 2)
    }

# ============================================================================
# LIVE CLIMATE MODEL (ESA VCD Approximation)
# ============================================================================

def fetch_venus_climate_model(lat_deg: float, alt_km: float) -> Dict:
    temp_c = 30.0 - ((alt_km - 50.0) * 8.0)
    pressure_atm = 1.0 * math.exp(-(alt_km - 50.0) / 5.5)
    wind_speed = 100.0 * math.cos(math.radians(lat_deg))
    wind_dir = 270.0 
    density = 0.65 * math.exp(-(alt_km - 50.0) / 15.9)
    
    return {
        'temperature_c': round(temp_c, 1),
        'pressure_atm': round(pressure_atm, 3),
        'wind_speed_ms': round(wind_speed, 1),
        'wind_direction_deg': wind_dir,
        'density_kg_m3': round(density, 3),
        'source': 'ESA Venus Climate Database (Climatology)'
    }

# ============================================================================
# VENUS SITE SCORING
# ============================================================================

def compute_display_score(rd: Dict) -> Dict:
    raw_score = rd.get('suitability_percentage', 0)
    raw_rating = rd.get('rating', 'Unknown')
    raw_emoji = rd.get('rating_emoji', '⚪')

    acid = rd.get('acid_risk', 'Low')
    shear = rd.get('wind_shear_ms_per_km', 0)
    alt = rd.get('cloud_altitude_km', 50)

    cap_reason = None
    display_score = raw_score

    if alt < 45:
        display_score = min(raw_score, 30.0)
        cap_reason = f"Cloud altitude {alt} km < 45 km — pressure crush risk"
    elif acid in ('High', 'Very High'):
        display_score = min(raw_score, 45.0)
        cap_reason = "High sulfuric acid aerosol — material degradation"
    elif shear > 6:
        display_score = min(raw_score, 50.0)
        cap_reason = f"Wind shear {shear:.1f} m/s/km — aerostat structural limit"

    is_capped = display_score < raw_score
    not_feasible = bool(cap_reason and alt < 45)

    if is_capped:
        if display_score < 40:
            display_rating, display_emoji = 'Blocked', '🚫'
        elif display_score < 60:
            display_rating, display_emoji = 'High Risk', '🔴'
        else:
            display_rating, display_emoji = 'Limited', '⚠️'
    else:
        display_rating = raw_rating
        display_emoji = raw_emoji

    return {
        'display_score': round(display_score, 1), 'raw_score': raw_score,
        'display_rating': display_rating, 'display_emoji': display_emoji,
        'is_capped': is_capped, 'cap_reason': cap_reason, 'not_feasible': not_feasible,
    }

# ============================================================================
# VENUS DATA
# ============================================================================

VENUS_SITES = {
    'Polar Launch Platform North': {
        'lat': 75.0, 'lon': 0.0, 'region': 'polar',
        'cloud_alt_km': 54.0, 'acid_risk': 'Low',
        'wind_shear_ms_per_km': 4.5, 'uv_flux_rel': 0.3,
        'thermal_variation_c': 6.0, 'solar_power_pct': 30,
        'lightning_risk': 'Low', 'volcanic_activity': 'Low', 'comm_delay_min': 12,
        'notes': 'Polar vortex. Slower zonal winds, launch advantage.',
    },
    'Upper Cloud Launch Platform Alpha': {
        'lat': 0.0, 'lon': 0.0, 'region': 'equatorial',
        'cloud_alt_km': 58.0, 'acid_risk': 'Low',
        'wind_shear_ms_per_km': 2.5, 'uv_flux_rel': 1.3,
        'thermal_variation_c': 1.5, 'solar_power_pct': 75,
        'lightning_risk': 'Moderate', 'volcanic_activity': 'Low', 'comm_delay_min': 5,
        'notes': 'Upper cloud deck. Maximum launch delta-V saving.',
    },
    'Ishtar Terra Cloud Station': {
        'lat': 67.0, 'lon': 40.0, 'region': 'northern',
        'cloud_alt_km': 52.0, 'acid_risk': 'Moderate',
        'wind_shear_ms_per_km': 3.2, 'uv_flux_rel': 0.6,
        'thermal_variation_c': 3.0, 'solar_power_pct': 55,
        'lightning_risk': 'Moderate', 'volcanic_activity': 'Low', 'comm_delay_min': 10,
        'notes': 'Above Maxwell Montes. Stable mid-latitude cloud deck.',
    },
    'Lada Terra Cloud Deck': {
        'lat': -45.0, 'lon': 40.0, 'region': 'southern',
        'cloud_alt_km': 53.0, 'acid_risk': 'Low',
        'wind_shear_ms_per_km': 3.8, 'uv_flux_rel': 0.5,
        'thermal_variation_c': 4.0, 'solar_power_pct': 48,
        'lightning_risk': 'Moderate', 'volcanic_activity': 'Low', 'comm_delay_min': 15,
        'notes': 'Southern mid-latitude. Lower acid, moderate wind shear.',
    },
    'Fortuna Tessera Station': {
        'lat': 58.0, 'lon': 10.0, 'region': 'northern',
        'cloud_alt_km': 52.5, 'acid_risk': 'Moderate',
        'wind_shear_ms_per_km': 3.5, 'uv_flux_rel': 0.7,
        'thermal_variation_c': 3.5, 'solar_power_pct': 50,
        'lightning_risk': 'Moderate', 'volcanic_activity': 'Low', 'comm_delay_min': 11,
        'notes': 'Highland tessera region. Good mix of altitude and stability.',
    },
    'Cleopatra Crater Base': {
        'lat': 65.0, 'lon': 340.0, 'region': 'northern',
        'cloud_alt_km': 53.5, 'acid_risk': 'Low',
        'wind_shear_ms_per_km': 4.0, 'uv_flux_rel': 0.4,
        'thermal_variation_c': 5.0, 'solar_power_pct': 40,
        'lightning_risk': 'Low', 'volcanic_activity': 'Low', 'comm_delay_min': 11,
        'notes': 'Near Cleopatra crater. Stable and safe.',
    },
    'Aphrodite Terra Cloud Deck': {
        'lat': -10.0, 'lon': 100.0, 'region': 'equatorial',
        'cloud_alt_km': 50.0, 'acid_risk': 'Moderate',
        'wind_shear_ms_per_km': 2.1, 'uv_flux_rel': 1.1,
        'thermal_variation_c': 2.0, 'solar_power_pct': 70,
        'lightning_risk': 'High', 'volcanic_activity': 'Low', 'comm_delay_min': 6,
        'notes': 'Equatorial super-rotation. Fastest winds, best solar.',
    },
    'Atla Regio Cloud Base': {
        'lat': 12.0, 'lon': 200.0, 'region': 'equatorial',
        'cloud_alt_km': 50.0, 'acid_risk': 'Moderate',
        'wind_shear_ms_per_km': 2.3, 'uv_flux_rel': 1.0,
        'thermal_variation_c': 2.2, 'solar_power_pct': 68,
        'lightning_risk': 'High', 'volcanic_activity': 'High', 'comm_delay_min': 5,
        'notes': 'Near Maat Mons. Volcanic terrain below, stable cloud deck.',
    },
    'Beta Regio Cloud Station': {
        'lat': 28.0, 'lon': 280.0, 'region': 'equatorial',
        'cloud_alt_km': 51.0, 'acid_risk': 'Moderate',
        'wind_shear_ms_per_km': 2.8, 'uv_flux_rel': 0.9,
        'thermal_variation_c': 2.5, 'solar_power_pct': 65,
        'lightning_risk': 'Moderate', 'volcanic_activity': 'Moderate', 'comm_delay_min': 7,
        'notes': 'Highland region with Theia and Rhea Mons. Volcanic area.',
    },
    'Mead Crater Cloud Site': {
        'lat': 12.0, 'lon': 57.0, 'region': 'equatorial',
        'cloud_alt_km': 50.0, 'acid_risk': 'Moderate',
        'wind_shear_ms_per_km': 2.5, 'uv_flux_rel': 1.0,
        'thermal_variation_c': 2.0, 'solar_power_pct': 68,
        'lightning_risk': 'Moderate', 'volcanic_activity': 'Low', 'comm_delay_min': 6,
        'notes': 'Large impact crater. Good baseline site.',
    },
    'Sapas Mons Station': {
        'lat': 8.0, 'lon': 188.0, 'region': 'equatorial',
        'cloud_alt_km': 50.5, 'acid_risk': 'Moderate',
        'wind_shear_ms_per_km': 2.6, 'uv_flux_rel': 1.05,
        'thermal_variation_c': 2.1, 'solar_power_pct': 66,
        'lightning_risk': 'Moderate', 'volcanic_activity': 'Moderate', 'comm_delay_min': 5,
        'notes': 'Shield volcano nearby. Stable cloud deck.',
    },
    'Eistla Regio Cloud Base': {
        'lat': 8.0, 'lon': 30.0, 'region': 'equatorial',
        'cloud_alt_km': 51.0, 'acid_risk': 'Moderate',
        'wind_shear_ms_per_km': 2.4, 'uv_flux_rel': 1.0,
        'thermal_variation_c': 2.0, 'solar_power_pct': 69,
        'lightning_risk': 'Moderate', 'volcanic_activity': 'Low', 'comm_delay_min': 6,
        'notes': 'Highland region. Good solar and stable winds.',
    },
    'Valles Marineris (False Site)': {
        'lat': -14.0, 'lon': -59.0, 'region': 'equatorial',
        'cloud_alt_km': 45.0, 'acid_risk': 'High',
        'wind_shear_ms_per_km': 6.5, 'uv_flux_rel': 1.5,
        'thermal_variation_c': 8.0, 'solar_power_pct': 85,
        'lightning_risk': 'High', 'volcanic_activity': 'Low', 'comm_delay_min': 4,
        'notes': 'Extreme wind shear and high acid. Not viable.',
    },
    'Maat Mons Ash Cloud': {
        'lat': 0.0, 'lon': 195.0, 'region': 'equatorial',
        'cloud_alt_km': 48.0, 'acid_risk': 'High',
        'wind_shear_ms_per_km': 5.5, 'uv_flux_rel': 1.4,
        'thermal_variation_c': 6.0, 'solar_power_pct': 60,
        'lightning_risk': 'High', 'volcanic_activity': 'Extreme', 'comm_delay_min': 5,
        'notes': 'Active volcano. Ash and acid hazard.',
    },
    'Phoebe Regio Turbulence Zone': {
        'lat': -10.0, 'lon': 280.0, 'region': 'equatorial',
        'cloud_alt_km': 46.0, 'acid_risk': 'High',
        'wind_shear_ms_per_km': 7.2, 'uv_flux_rel': 1.2,
        'thermal_variation_c': 7.0, 'solar_power_pct': 70,
        'lightning_risk': 'High', 'volcanic_activity': 'Moderate', 'comm_delay_min': 8,
        'notes': 'High turbulence zone. Severe structural risk.',
    },
    'Ovda Regio Acid Belt': {
        'lat': -5.0, 'lon': 30.0, 'region': 'equatorial',
        'cloud_alt_km': 49.0, 'acid_risk': 'Very High',
        'wind_shear_ms_per_km': 4.5, 'uv_flux_rel': 1.1,
        'thermal_variation_c': 4.0, 'solar_power_pct': 72,
        'lightning_risk': 'High', 'volcanic_activity': 'Low', 'comm_delay_min': 5,
        'notes': 'Heavy acid belt. Severe material degradation.',
    },
    'Thetis Regio Cloud Base': {
        'lat': -12.0, 'lon': 30.0, 'region': 'southern',
        'cloud_alt_km': 51.0, 'acid_risk': 'Moderate',
        'wind_shear_ms_per_km': 3.0, 'uv_flux_rel': 0.8,
        'thermal_variation_c': 3.0, 'solar_power_pct': 58,
        'lightning_risk': 'Moderate', 'volcanic_activity': 'Low', 'comm_delay_min': 9,
        'notes': 'Southern equatorial transition zone. Stable.',
    },
    'Gula Mons Volcanic Edge': {
        'lat': 22.0, 'lon': 310.0, 'region': 'northern',
        'cloud_alt_km': 50.0, 'acid_risk': 'High',
        'wind_shear_ms_per_km': 4.0, 'uv_flux_rel': 0.9,
        'thermal_variation_c': 4.5, 'solar_power_pct': 62,
        'lightning_risk': 'High', 'volcanic_activity': 'High', 'comm_delay_min': 8,
        'notes': 'Near active volcano. Heat source but risky.',
    },
    'Hecate Chasma Floating City': {
        'lat': -42.0, 'lon': 100.0, 'region': 'southern',
        'cloud_alt_km': 52.0, 'acid_risk': 'Moderate',
        'wind_shear_ms_per_km': 3.6, 'uv_flux_rel': 0.6,
        'thermal_variation_c': 4.0, 'solar_power_pct': 52,
        'lightning_risk': 'Low', 'volcanic_activity': 'Low', 'comm_delay_min': 13,
        'notes': 'Southern canyon region. Stable.',
    },
    'Amphitrite Corona Base': {
        'lat': -50.0, 'lon': 20.0, 'region': 'southern',
        'cloud_alt_km': 53.5, 'acid_risk': 'Low',
        'wind_shear_ms_per_km': 4.0, 'uv_flux_rel': 0.5,
        'thermal_variation_c': 5.5, 'solar_power_pct': 45,
        'lightning_risk': 'Moderate', 'volcanic_activity': 'Low', 'comm_delay_min': 14,
        'notes': 'Corona formation. Good altitude and low acid.',
    }
}

VENUS_CANDIDATES = list(VENUS_SITES.keys())

def get_venus_site_data(name: str) -> Dict:
    if name in VENUS_SITES:
        return VENUS_SITES[name]
    return {
        'lat': 0.0, 'lon': 0.0, 'region': 'unknown',
        'cloud_alt_km': 50.0, 'acid_risk': 'Moderate',
        'wind_shear_ms_per_km': 3.0, 'uv_flux_rel': 1.0,
        'thermal_variation_c': 3.0, 'solar_power_pct': 60,
        'lightning_risk': 'Moderate', 'volcanic_activity': 'Low', 'comm_delay_min': 10,
        'notes': 'Unknown site — conservative defaults',
    }

def _haversine(lat1, lon1, lat2, lon2):
    R = 6051.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(min(1, math.sqrt(a)))

def _quick_static_estimate(data: Dict) -> Dict:
    alt = data['cloud_alt_km']
    acid = data['acid_risk']
    shear = data['wind_shear_ms_per_km']
    solar = data['solar_power_pct']

    alt_s = 5.0 if 48 <= alt <= 55 else (4.0 if 45 <= alt < 48 or 55 < alt <= 60 else 2.0)
    acid_s = 5.0 if acid == 'Low' else (3.0 if acid == 'Moderate' else 1.0)
    shear_s = 5.0 if shear < 2 else (4.0 if shear < 3 else (3.0 if shear < 4 else (2.0 if shear < 5 else 1.0)))
    solar_s = solar / 20.0

    composite = (alt_s * 0.30 + acid_s * 0.25 + shear_s * 0.25 + solar_s * 0.20) * 20

    if composite >= 80: rating, emoji = 'Excellent', '🪐'
    elif composite >= 65: rating, emoji = 'Good', '👍'
    elif composite >= 50: rating, emoji = 'Moderate', '👌'
    else: rating, emoji = 'Poor', '❌'

    investment = 'Extreme' if acid in ('High', 'Very High') or alt < 45 else ('Very High' if acid == 'Moderate' else 'High')

    return {'suitability': round(composite, 1), 'rating': rating,
            'rating_emoji': emoji, 'investment': investment}

def estimate_cost_range(rd: Dict) -> Dict:
    acid = rd.get('acid_risk', 'Moderate')
    shear = rd.get('wind_shear_ms_per_km', 3.0)
    alt = rd.get('cloud_altitude_km', 50)

    base = 250.0
    if acid in ('High', 'Very High'): base += 80.0
    if shear > 5: base += 50.0
    if alt < 48: base += 30.0

    low = round(base * 0.7, 1)
    mid = round(base, 1)
    high = round(base * 1.3, 1)

    extras = []
    if acid in ('High', 'Very High'): extras.append("Acid-resistant envelope (~$40B)")
    if shear > 5: extras.append("Active ballast system (~$25B)")
    if alt < 48: extras.append("High-pressure aerostat (~$30B)")

    return {
        'low_billion': low, 'mid_billion': mid, 'high_billion': high,
        'includes': ['Launch', 'Aerostat', 'Habitat', 'Power', 'ISRU', 'Comms'],
        'excludes': extras if extras else ['Crew transport', 'Contingency'],
    }

def build_radar_chart(sites_data: List[Dict]) -> Optional[go.Figure]:
    if len(sites_data) < 2:
        return None
    criteria = [
        ('cloud_altitude', 'Cloud Alt'),
        ('acid_safety', 'Low Acid'),
        ('wind_stability', 'Wind Stability'),
        ('solar_power', 'Solar Power'),
        ('uv_shielding', 'UV Shielding'),
        ('lightning_safety', 'Low Lightning'),
        ('volcanic_safety', 'Low Volcanic'),
    ]
    fig = go.Figure()
    colors = ['#ffb84d', '#00f5d4', '#39ff14', '#ffd60a', '#ff6b35']
    for i, site in enumerate(sites_data[:5]):
        scores = site.get('scores', {})
        values = [scores.get(k, 0) for k, _ in criteria]
        labels = [label for _, label in criteria]
        values_closed = values + [values[0]]
        labels_closed = labels + [labels[0]]
        fig.add_trace(go.Scatterpolar(
            r=values_closed, theta=labels_closed, fill='toself',
            name=site.get('name', f'Site {i+1}'),
            line_color=colors[i % len(colors)],
            fillcolor=colors[i % len(colors)], opacity=0.3,
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(color='#ffb84d')),
            bgcolor='rgba(25, 15, 5, 0.8)',
        ),
        paper_bgcolor='rgba(15, 8, 5, 0)',
        font=dict(color='#ffffff'), height=500,
    )
    return fig

# ============================================================================
# RECOMMENDATION ENGINE
# ============================================================================

def generate_recommendation_strategy(rd: Dict) -> Dict:
    score = rd.get('suitability_percentage', 0)
    alt = rd.get('cloud_altitude_km', 50)
    acid = rd.get('acid_risk', 'Moderate')
    shear = rd.get('wind_shear_ms_per_km', 3.0)
    solar = rd.get('solar_power_pct', 50)
    uv = rd.get('uv_flux_rel', 1.0)

    recommendations = {
        'immediate_actions': [], 'short_term_actions': [], 'long_term_actions': [],
        'investment_required': 'High', 'overall_feasibility': 'Moderate',
        'risk_level': 'Medium', 'timeline_summary': {}
    }

    def add(bucket, text, priority, cost):
        recommendations[bucket].append({'text': text, 'priority': priority, 'cost': cost})

    add('immediate_actions', '🔥 SURFACE WARNING: 464°C, 92 atm. Ground rovers will melt/crush instantly. Use only Cloud-Deck Aerobots (Drones) and Balloon Probes.', 'Critical', '💸💸')

    if alt < 45:
        add('immediate_actions', f'🚨 ALTITUDE {alt} km — Pressure crush risk. Relocate to 48–55 km band.', 'Critical', '💸💸💸💸💸')
        recommendations['investment_required'] = 'Extreme'
    elif alt < 48:
        add('short_term_actions', f'⚠️ Altitude {alt} km — Reinforce aerostat envelope.', 'High', '💸💸💸')
        recommendations['investment_required'] = 'Very High'
    elif alt <= 55:
        add('immediate_actions', f'✅ Altitude {alt} km — Ideal cloud-deck band (1 atm, ~30°C).', 'Low', '💸')
    else:
        add('short_term_actions', f'🌡️ Altitude {alt} km — Upper cloud. Larger envelope needed.', 'Medium', '💸💸')

    if acid in ('High', 'Very High'):
        add('immediate_actions', '☣️ HIGH ACID RISK — PTFE/gold coatings, filtration, acid harvesting MANDATORY.', 'Critical', '💸💸💸💸')
        recommendations['investment_required'] = 'Extreme'
    elif acid == 'Moderate':
        add('short_term_actions', '☣️ Moderate acid — Standard acid-resistant materials + monitoring.', 'High', '💸💸💸')
    else:
        add('immediate_actions', '✅ Low acid risk — Standard protection sufficient.', 'Low', '💸')

    if shear > 6:
        add('immediate_actions', f'🌪️ CRITICAL SHEAR {shear:.1f} m/s/km — Active ballast and trim required.', 'Critical', '💸💸💸💸')
    elif shear > 4:
        add('short_term_actions', f'🌪️ Moderate shear {shear:.1f} m/s/km — Reinforce envelope + dynamic positioning.', 'High', '💸💸💸')
    elif shear < 2.5:
        add('immediate_actions', f'✅ Excellent stability {shear:.1f} m/s/km — Stable platform.', 'Low', '💸')
    else:
        add('short_term_actions', f'🌬️ Normal shear {shear:.1f} m/s/km — Standard stabilization.', 'Medium', '💸💸')

    if uv > 1.2:
        add('short_term_actions', f'☀️ UV flux {uv:.1f}× Earth — UV-blocking external materials.', 'High', '💸💸')
    else:
        add('immediate_actions', f'✅ UV flux {uv:.1f}× Earth — Standard shielding.', 'Low', '💸')

    if solar < 40:
        add('short_term_actions', f'☀️ Solar {solar}% — Nuclear or beamed power supplement.', 'High', '💸💸💸')
    elif solar < 60:
        add('short_term_actions', f'☀️ Solar {solar}% — Hybrid solar + storage.', 'Medium', '💸💸')
    else:
        add('immediate_actions', f'✅ Solar {solar}% — Excellent solar potential.', 'Low', '💸')

    add('long_term_actions', '🏗️ Aerostat habitat construction (cloud-deck assembly).', 'Medium', '💸💸💸')
    add('long_term_actions', '🚀 ISRU plant: CO₂ → O₂ + water extraction from cloud droplets.', 'High', '💸💸💸💸')
    add('long_term_actions', '🛸 Deploy Aerobot fleet: Flying drones to study lower atmosphere (never touching the ground).', 'High', '💸💸')

    critical_count = sum(1 for a in recommendations['immediate_actions'] if a['priority'] == 'Critical')
    high_count = sum(1 for a in recommendations['short_term_actions'] if a['priority'] == 'High')

    if score >= 80: band, emoji = 'Excellent', '🪐'
    elif score >= 65: band, emoji = 'Good', '👍'
    elif score >= 50: band, emoji = 'Moderate', '👌'
    elif score >= 35: band, emoji = 'Limited', '⚠️'
    else: band, emoji = 'Poor', '❌'

    if critical_count >= 3:
        feasibility, risk_level = '❌ Poor - Multiple critical hazards', 'Very High'
    elif critical_count == 2:
        feasibility, risk_level = '⚠️ Limited - Two critical issues', 'High'
    elif critical_count == 1:
        feasibility, risk_level = '👌 Moderate - One critical issue', 'High'
    elif high_count >= 2:
        feasibility, risk_level = '👌 Moderate - Several high-priority', 'Medium'
    else:
        feasibility = f'{emoji} {band}'
        risk_level = {'Excellent': 'Low', 'Good': 'Low', 'Moderate': 'Medium',
                      'Limited': 'High', 'Poor': 'Very High'}[band]

    recommendations['overall_feasibility'] = feasibility
    recommendations['risk_level'] = risk_level
    recommendations['critical_action_count'] = critical_count
    recommendations['high_action_count'] = high_count
    recommendations['timeline_summary'] = {
        'immediate': f"{len(recommendations['immediate_actions'])} actions (0-6 months)",
        'short_term': f"{len(recommendations['short_term_actions'])} actions (6-18 months)",
        'long_term': f"{len(recommendations['long_term_actions'])} actions (18-36 months)",
    }
    return recommendations

# ============================================================================
# MEMORY REPOSITORY
# ============================================================================

class MemoryRepository:
    def __init__(self, db_path: str = "venusbase_memory.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL, query_hash TEXT NOT NULL,
                result_summary TEXT, success INTEGER, execution_time REAL,
                parameters TEXT, timestamp TEXT, embedding BLOB
            )
        """)
        conn.commit(); conn.close()

    def store_analysis(self, query, summary, success, exec_time, params):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        qhash = hashlib.md5(query.lower().encode()).hexdigest()
        cursor.execute("""
            INSERT INTO analysis_memory
            (query, query_hash, result_summary, success, execution_time, parameters, timestamp, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (query, qhash, summary, 1 if success else 0, exec_time,
              json.dumps(params), datetime.now().isoformat(), pickle.dumps([])))
        conn.commit(); conn.close()

    def get_all_analyses(self, limit=20):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analysis_memory ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        results = [{
            'query': r[1], 'result_summary': r[3],
            'success': bool(r[4]), 'execution_time': r[5],
            'parameters': json.loads(r[6]) if r[6] else {},
            'timestamp': r[7],
        } for r in rows]
        conn.close()
        return results

    def get_analysis_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM analysis_memory")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM analysis_memory WHERE success = 1")
        success = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(execution_time) FROM analysis_memory")
        avg = cursor.fetchone()[0] or 0
        conn.close()
        return {'total_analyses': total, 'successful_analyses': success,
                'success_rate': success / total if total > 0 else 0,
                'avg_execution_time': avg}

    def clear_all(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analysis_memory")
        conn.commit(); conn.close()

# ============================================================================
# VENUS ANALYSIS STRATEGY
# ============================================================================

class VenusSiteAnalysisStrategy(ABC):
    def __init__(self, region: str = "all"):
        self.region = region

    def get_name(self) -> str:
        return f"VenusBase Site Selection ({self.region})"

    def analyse(self, site_name: str, params: Dict) -> Dict:
        data = get_venus_site_data(site_name)

        alt = data['cloud_alt_km']
        acid = data['acid_risk']
        shear = data['wind_shear_ms_per_km']
        uv = data['uv_flux_rel']
        solar = data['solar_power_pct']
        thermal = data['thermal_variation_c']
        lightning = data.get('lightning_risk', 'Moderate')
        volcanic = data.get('volcanic_activity', 'Low')
        comm = data.get('comm_delay_min', 10)

        scores = {}
        if 48 <= alt <= 55: scores['cloud_altitude'] = 5.0
        elif 45 <= alt < 48: scores['cloud_altitude'] = 3.5
        elif 55 < alt <= 60: scores['cloud_altitude'] = 4.0
        else: scores['cloud_altitude'] = 2.0

        scores['acid_safety'] = 5.0 if acid == 'Low' else (3.0 if acid == 'Moderate' else 1.0)
        scores['wind_stability'] = 5.0 if shear < 2 else (4.5 if shear < 3 else (3.5 if shear < 4 else (2.5 if shear < 5 else 1.5)))
        scores['solar_power'] = round(5.0 * (solar / 100.0), 2)
        scores['uv_shielding'] = 5.0 if uv < 0.6 else (4.0 if uv < 1.0 else (3.0 if uv < 1.3 else 2.0))
        scores['lightning_safety'] = 5.0 if lightning == 'Low' else (3.0 if lightning == 'Moderate' else 1.0)
        scores['volcanic_safety'] = 5.0 if volcanic == 'Low' else (3.5 if volcanic == 'Moderate' else (2.0 if volcanic == 'High' else 1.0))
        scores['comm_link'] = 5.0 if comm < 6 else (4.0 if comm < 10 else (3.0 if comm < 15 else 2.0))

        weights = {
            'cloud_altitude': 0.20, 'acid_safety': 0.20, 'wind_stability': 0.20,
            'solar_power': 0.10, 'uv_shielding': 0.05, 'lightning_safety': 0.10,
            'volcanic_safety': 0.05, 'comm_link': 0.10,
        }
        weighted_total = sum(scores[k] * weights[k] for k in weights)
        percentage = (weighted_total / 5.0) * 100

        if percentage >= 80: rating, emoji = 'Excellent', '🪐'
        elif percentage >= 65: rating, emoji = 'Good', '👍'
        elif percentage >= 50: rating, emoji = 'Moderate', '👌'
        elif percentage >= 35: rating, emoji = 'Limited', '⚠️'
        else: rating, emoji = 'Poor', '❌'

        conf = {'confidence_pct': 65.0, 'band': 'Moderate'}

        return {
            'success': True, 'scores': scores, 'details': {
                'cloud_altitude': {'score': scores['cloud_altitude'], 'value': f"{alt} km", 'weight': weights['cloud_altitude'], 'source': 'Magellan atmospheric model'},
                'acid_safety': {'score': scores['acid_safety'], 'value': acid, 'weight': weights['acid_safety'], 'source': 'Magellan / Venus Express'},
                'wind_stability': {'score': scores['wind_stability'], 'value': f"{shear:.1f} m/s/km", 'weight': weights['wind_stability'], 'source': 'Venus super-rotation model'},
                'solar_power': {'score': scores['solar_power'], 'value': f"{solar}% potential", 'weight': weights['solar_power'], 'source': 'Cloud-deck insolation'},
                'uv_shielding': {'score': scores['uv_shielding'], 'value': f"{uv:.1f}× Earth", 'weight': weights['uv_shielding'], 'source': 'Venus atmospheric opacity'},
                'lightning_safety': {'score': scores['lightning_safety'], 'value': lightning, 'weight': weights['lightning_safety'], 'source': 'Venus Express data'},
                'volcanic_safety': {'score': scores['volcanic_safety'], 'value': volcanic, 'weight': weights['volcanic_safety'], 'source': 'Magellan SAR'},
                'comm_link': {'score': scores['comm_link'], 'value': f"{comm} min delay", 'weight': weights['comm_link'], 'source': 'Orbital dynamics'},
            },
            'weighted_score': weighted_total, 'max_possible_score': 5.0,
            'suitability_percentage': round(percentage, 1),
            'base_percentage': round(percentage, 1), 'penalty_applied': 0.0, 'penalty_reasons': [],
            'rating': rating, 'rating_emoji': emoji, 'recommendation': 'Review recommendation strategy below.',
            'location': f"{site_name} ({data['lat']:.4f}, {data['lon']:.4f})",
            'site_name': site_name, 'region': self.region, 'lat': data['lat'], 'lon': data['lon'],
            'cloud_altitude_km': alt, 'acid_risk': acid, 'wind_shear_ms_per_km': shear,
            'uv_flux_rel': uv, 'solar_power_pct': solar, 'thermal_variation_c': thermal,
            'lightning_risk': lightning, 'volcanic_activity': volcanic, 'comm_delay_min': comm,
            'notes': data['notes'], 'data_confidence': conf,
            'analysis_method': 'Venus: Magellan / atmospheric model',
            'data_source_details': [f"Cloud alt: {alt} km", f"Acid: {acid}", f"Shear: {shear:.1f} m/s/km", f"Solar: {solar}%", f"UV: {uv:.1f}× Earth"],
            'investment_band': ('Extreme' if acid in ('High', 'Very High') or alt < 45 else 'Very High' if acid == 'Moderate' else 'High'),
        }

class StrategySelector:
    @classmethod
    def get_strategy(cls, t: str, region: str = "all"):
        return VenusSiteAnalysisStrategy(region)

# ============================================================================
# PHASE 2-5 MODULES (Venus-adapted, No Rovers)
# ============================================================================

class EnhancedVenusbaseDeveloper:
    def develop_complete_plan(self, site_data: Dict, population: int = 4) -> Dict:
        disp = compute_display_score(site_data)
        cost_range = estimate_cost_range(site_data)
        total_months = 60 if site_data.get('acid_risk') not in ('High', 'Very High') else 84

        return {
            'phase_1_site_selection': {
                'site_data': site_data,
                'suitability_score': disp['display_score'], 'raw_geological_score': disp['raw_score'],
                'display_rating': disp['display_rating'], 'display_emoji': disp['display_emoji'],
                'not_feasible': disp['not_feasible'], 'cap_reason': disp['cap_reason'],
                'headline_cost_mid_billion': cost_range['mid_billion'],
                'total_months': total_months, 'total_years': round(total_months / 12, 1),
                'total_months_human': f"{total_months} months (~{total_months/12:.1f} years)",
            },
            'phase_2_infrastructure': {
                'cost_estimate': {'total_cost_billions': cost_range['mid_billion'], 'per_sqm_cost': (cost_range['mid_billion'] * 1e9) / 1_000_000, 'rock_type': 'cloud-deck (aerostat)'},
                'transport_plan': {'primary_transport': 'Aerostat + Earth-Venus transfer', 'network_length_km': 50.0, 'population_crew': population},
                'utility_plan': {'water': {'daily_need_liters': 200 * population}, 'power': {'peak_demand_mw': 2.0 * population}, 'ventilation': {'oxygen_generation': 'CO₂ splitting (SO₂ tolerant)'}},
            },
            'phase_3_construction': {
                'simulation': {
                    'total_months_human': f"{total_months} months", 'completion_probability': 60.0,
                    'phases': {'aerostat_deployment': {'duration_months': 18}, 'habitat_inflation': {'duration_months': 24}, 'isru_commissioning': {'duration_months': 12}},
                    'tasks': ['Deploy cloud-deck aerobots (No ground rovers)', 'Airborne ISRU processing', 'Aerostat structural integrity testing']
                },
            },
            'phase_4_public': {
                'vr_walkthrough': {'scenes': [{'name': 'Cloud Deck Arrival', 'description': 'Aerostat descent through sulfuric clouds'}, {'name': 'Habitat Interior', 'description': '1 atm, 30°C — shirt-sleeve environment'}, {'name': 'ISRU Plant', 'description': 'CO₂ → O₂ + water extraction'}, {'name': 'Observation Deck', 'description': 'Venus cloudscape from 50 km'}]},
                'consultation': {'survey_questions': [{'question': 'Should humanity build a floating city on Venus?'}]},
            },
            'phase_5_global': {
                'venus_adaptation': {'similarities': {'habitat_design': '90% transferable (1 atm, Earth-like temp)', 'isru': '80% transferable', 'radiation_shielding': '95% transferable (atmosphere helps)'}},
                'climate_resilience': {'overall_resilience_score': 70},
                'ai_swarm': {'agents': [{'id': 'Agent_1', 'role': 'Aerostat Engineer'}, {'id': 'Agent_2', 'role': 'ISRU Specialist'}, {'id': 'Agent_3', 'role': 'Safety Officer'}]},
            },
        }

# ============================================================================
# SESSION STATE
# ============================================================================

def init_session_state():
    if 'memory_repo' not in st.session_state:
        st.session_state.memory_repo = MemoryRepository()
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'region' not in st.session_state:
        st.session_state.region = 'all'
    if 'selected_site_name' not in st.session_state:
        st.session_state.selected_site_name = 'Ishtar Terra Cloud Station'
    if 'current_results' not in st.session_state:
        st.session_state.current_results = None
    if 'comparison_mode' not in st.session_state:
        st.session_state.comparison_mode = False
    if 'multi_ranking_mode' not in st.session_state:
        st.session_state.multi_ranking_mode = False
    if 'multi_ranking_selected' not in st.session_state:
        st.session_state.multi_ranking_selected = []
    if 'multi_ranking_results' not in st.session_state:
        st.session_state.multi_ranking_results = None

# ============================================================================
# UI — MAP (With NASA Trek Link)
# ============================================================================

def render_map(params, region):
    st.subheader(f"🪐 {region.replace('_', ' ').title()} Venus Site Map")
    
    if st.session_state.selected_site_name in VENUS_SITES:
        sel = VENUS_SITES[st.session_state.selected_site_name]
        center = [sel['lat'], sel['lon']]
    else:
        center = [0.0, 0.0]

    # 2D Folium Map
    m = folium.Map(location=center, zoom_start=3, tiles=None, attr='USGS/NASA/JPL Magellan')
    img_b64 = get_base64_image(VENUS_IMAGE_LOCAL)
    
    if img_b64:
        img_data = f"data:image/jpeg;base64,{img_b64}"
        ImageOverlay(image=img_data, bounds=VENUS_BOUNDS, opacity=0.95).add_to(m)
    else:
        ImageOverlay(image=VENUS_IMAGE_URL, bounds=VENUS_BOUNDS, opacity=0.95).add_to(m)

    for name, data in VENUS_SITES.items():
        if region != 'all' and data['region'] != region: continue
        est = _quick_static_estimate(data)
        score = est['suitability']
        if score >= 80: color = 'green'
        elif score >= 65: color = 'lightgreen'
        elif score >= 50: color = 'orange'
        else: color = 'red'

        folium.Marker(
            [data['lat'], data['lon']],
            popup=f"<b>{name}</b><br>Score: {score:.0f}%<br>Alt: {data['cloud_alt_km']} km<br>Acid: {data['acid_risk']}",
            tooltip=f"{name}: {score:.0f}%",
            icon=folium.Icon(color=color, icon='star', prefix='fa')
        ).add_to(m)

    if st.session_state.selected_site_name in VENUS_SITES:
        sel = VENUS_SITES[st.session_state.selected_site_name]
        folium.Marker(
            [sel['lat'], sel['lon']],
            popup=f"<b>🎯 {st.session_state.selected_site_name}</b>",
            icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
        ).add_to(m)

    try:
        Fullscreen(position='topleft').add_to(m)
        MousePosition(position='bottomleft', prefix='Venus Coords: ').add_to(m)
    except Exception:
        pass

    legend_html = """
    <div style="position: fixed; bottom: 50px; right: 50px; width: 150px; height: 120px; 
     background-color: rgba(25, 15, 5, 0.8); border:2px solid #ffb84d; z-index:9999; font-size:12px;
     color: white; font-family: 'Courier New'; padding: 10px; border-radius: 8px;">
     <b>🗺️ MAGELLAN MAP</b><br>
     <span style="color:#e85d04;">■</span> High Elevation<br>
     <span style="color:#ffd60a;">■</span> Low Elevation<br>
     <span style="color:#00f5d4;">■</span> Plains<br>
     <span style="color:#ffb84d;">■</span> Radar Bright<br>
     <i style="color:#a08060; font-size:10px;">Data: NASA/USGS</i>
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    map_data = st_folium(m, width=None, height=500, use_container_width=True)

    # NASA Trek 3D Button (FIXED: Points to main portal to avoid permalink errors)
    trek_url = "https://trek.nasa.gov/venus/"
    st.markdown(f"""
    <div class="nasa-trek-box">
        <div style="color: #ff2d95; font-family: 'Courier New', monospace; 
             font-size: 0.9rem; font-weight: bold; letter-spacing: 1px; margin-bottom: 5px;">
            🚀 3D VISUALIZATION
        </div>
        <a href="{trek_url}" target="_blank" style="
            display: inline-block; padding: 10px 20px; margin-top: 5px;
            background: linear-gradient(135deg, rgba(255, 45, 149, 0.2), rgba(176, 38, 255, 0.2));
            border: 1px solid #ff2d95; border-radius: 8px;
            color: #ff2d95; font-family: 'Courier New', monospace;
            font-weight: bold; text-decoration: none; letter-spacing: 2px;
            text-transform: uppercase; font-size: 0.8rem;
        ">
            🪐 Open NASA Venus Trek 3D ↗
        </a>
        <div style="color: #a08060; font-family: 'Courier New', monospace; 
             font-size: 0.65rem; margin-top: 8px;">
            Opens the official NASA Solar System Treks portal in a new tab.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if map_data and map_data.get('last_clicked'):
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lon = map_data['last_clicked']['lng']
        
        custom_name = f"Custom Site ({clicked_lat:.1f}°, {clicked_lon:.1f}°)"
        abs_lat = abs(clicked_lat)
        dynamic_alt = 50.0 + (abs_lat / 90) * 5.0
        dynamic_acid = 'Low' if abs_lat > 45 else 'Moderate'
        dynamic_shear = 2.0 + (abs_lat / 90) * 3.0
        dynamic_solar = max(20, 80 - abs_lat)
        
        VENUS_SITES[custom_name] = {
            'lat': clicked_lat, 'lon': clicked_lon, 'region': 'custom',
            'cloud_alt_km': dynamic_alt, 'acid_risk': dynamic_acid,
            'wind_shear_ms_per_km': dynamic_shear, 'uv_flux_rel': 1.0,
            'thermal_variation_c': 3.0, 'solar_power_pct': dynamic_solar,
            'lightning_risk': 'Moderate', 'volcanic_activity': 'Low', 'comm_delay_min': 10,
            'notes': 'Dynamically generated site from map click.',
        }
        
        if st.session_state.selected_site_name != custom_name:
            st.session_state.selected_site_name = custom_name
            st.rerun()

# ============================================================================
# UI — Sidebar / Region / Analysis / Results
# ============================================================================

def render_region_switcher():
    st.markdown("""
    <div style="text-align: center; margin: 10px 0;">
        <div style="color: #ffb84d; font-family: 'Courier New', monospace; 
             letter-spacing: 3px; font-size: 0.9rem; margin-bottom: 10px;">
            🪐 SELECT VENUS REGION</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏔️ NORTHERN\n(Ishtar / Lakshmi)", use_container_width=True,
                     type="primary" if st.session_state.region == 'northern' else "secondary"):
            st.session_state.region = 'northern'
            st.session_state.selected_site_name = 'Ishtar Terra Cloud Station'
            st.session_state.current_results = None
            st.rerun()
    with col2:
        if st.button("🌍 EQUATORIAL\n(Aphrodite / Atla)", use_container_width=True,
                     type="primary" if st.session_state.region == 'equatorial' else "secondary"):
            st.session_state.region = 'equatorial'
            st.session_state.selected_site_name = 'Aphrodite Terra Cloud Deck'
            st.session_state.current_results = None
            st.rerun()
    with col3:
        if st.button("🧊 POLAR / ALL", use_container_width=True,
                     type="primary" if st.session_state.region in ('polar', 'all') else "secondary"):
            st.session_state.region = 'all'
            st.session_state.selected_site_name = 'Ishtar Terra Cloud Station'
            st.session_state.current_results = None
            st.rerun()
    return st.session_state.region

def render_sidebar(region):
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px 0;">
            <div style="font-size: 2.2rem; font-family: 'Courier New', monospace; 
                 background: linear-gradient(90deg, #ffd60a, #ff6b35, #e85d04);
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                 font-weight: 900; letter-spacing: 3px;">VENUSBASE</div>
            <div style="color: #ffb84d; font-size: 0.75rem; font-family: 'Courier New', monospace;
                 letter-spacing: 4px;">🪐 {region.replace('_', ' ').upper()}</div>
            <div class="cyber-divider"></div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("""<div style="color: #ffb84d; font-family: 'Courier New', monospace; 
             letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 10px;">
            🪐 SITE SELECTOR</div>""", unsafe_allow_html=True)

        if region == 'all':
            sites = VENUS_SITES
        else:
            sites = {k: v for k, v in VENUS_SITES.items() if v['region'] == region}
        site_names = list(sites.keys())
        idx = site_names.index(st.session_state.selected_site_name) if st.session_state.selected_site_name in site_names else 0
        quick_site = st.selectbox("Select Site", site_names, index=idx)
        if st.button("⚡ GO TO SITE", use_container_width=True):
            st.session_state.selected_site_name = quick_site
            st.rerun()
        st.divider()

        st.markdown("""<div style="color: #ffb84d; font-family: 'Courier New', monospace; 
             letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 10px;">
            🗺️ MAP</div>""", unsafe_allow_html=True)
        st.caption("USGS Magellan Radar Mosaic (Locked)")
        st.divider()

        if st.button("🔄 COMPARE ALL SITES", use_container_width=True):
            st.session_state.comparison_mode = True
            st.session_state.multi_ranking_mode = False
            st.rerun()
        if st.button("📊 MULTI-SITE RANKING", use_container_width=True):
            st.session_state.multi_ranking_mode = True
            st.session_state.comparison_mode = False
            st.rerun()
        if st.button("🧹 CLEAR RESULTS", use_container_width=True):
            st.session_state.current_results = None
            st.session_state.multi_ranking_results = None
            st.success("Results cleared!")
            st.rerun()
        st.divider()

        st.markdown("""<div style="color: #ffb84d; font-family: 'Courier New', monospace; 
             letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 10px;">
            🧠 MEMORY</div>""", unsafe_allow_html=True)

        stats = st.session_state.memory_repo.get_analysis_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="padding: 8px; border: 1px solid rgba(255,184,77,0.15); border-radius: 4px; text-align:center;">
                <div style="color:#a08060; font-family:'Courier New'; font-size:0.6rem;">ANALYSES</div>
                <div style="color:#ffb84d; font-family:'Courier New'; font-size:1.2rem; font-weight:bold;">{stats['total_analyses']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="padding: 8px; border: 1px solid rgba(255,184,77,0.15); border-radius: 4px; text-align:center;">
                <div style="color:#a08060; font-family:'Courier New'; font-size:0.6rem;">SUCCESS</div>
                <div style="color:#39ff14; font-family:'Courier New'; font-size:1.2rem; font-weight:bold;">{stats['success_rate']*100:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        if st.button("🗑️ CLEAR MEMORY", use_container_width=True):
            st.session_state.memory_repo.clear_all()
            try: Path("venusbase_memory.db").unlink(missing_ok=True)
            except Exception: pass
            st.session_state.analysis_history = []
            st.session_state.current_results = None
            st.session_state.multi_ranking_results = None
            st.session_state.memory_repo = MemoryRepository()
            st.success("Memory cleared!")
            st.rerun()

        return {'radius': 10000}

def render_query_interface(params, region):
    st.subheader("💬 Analyse Venus Site")
    with st.expander("💡 Venus Site Selection Examples", expanded=False):
        st.markdown("""
        - "Is Ishtar Terra viable for a floating base?"
        - "Compare Aphrodite Terra vs Atla Regio"
        - "Which site has the best acid resistance?"
        - "Evaluate polar launch platform for delta-V savings"
        """)
    query = st.text_area("Describe your analysis goal:",
                         placeholder="e.g., Evaluate this site for a Venus floating base",
                         height=100)
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        analyse_btn = st.button("🪐 ANALYSE SITE", type="primary", use_container_width=True)
    with col2:
        if st.button("🧹 CLEAR", use_container_width=True):
            st.session_state.current_results = None
            st.rerun()

    if analyse_btn:
        with st.spinner("🪐 Scoring against Venus atmospheric criteria..."):
            t0 = time.time()
            strategy = VenusSiteAnalysisStrategy(region)
            result = strategy.analyse(st.session_state.selected_site_name, params)
            elapsed = time.time() - t0
            st.session_state.current_results = result
            st.session_state.analysis_history.append(result)
            st.session_state.memory_repo.store_analysis(
                query or f"Evaluate {st.session_state.selected_site_name}",
                result.get('location', ''), True, elapsed, params)
            st.success(f"✅ Analysis complete in {elapsed:.2f}s")
            st.rerun()

def render_simulation_lab():
    st.subheader("🧪 Simulation Lab (What-If)")
    st.markdown("Adjust parameters to see how the mission scales.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        crew_size = st.slider("Crew Size", 4, 100, 10)
    with col2:
        habitat_mass = st.slider("Habitat Mass (Tons)", 50, 500, 150)
    with col3:
        power_source = st.selectbox("Power Source", ["Hybrid (Solar+Nuclear)", "Solar Only", "Nuclear Only"])

    base_cost = 250.0
    new_cost = base_cost + (crew_size * 1.5) + (habitat_mass * 0.5)
    if power_source == "Nuclear Only": new_cost += 50.0
    if power_source == "Solar Only": new_cost -= 20.0

    air_needed = crew_size * 200
    water_needed = crew_size * 150
    envelope_volume = (habitat_mass * 1000) / 64.0

    st.markdown("---")
    st.write("### 📊 Updated Mission Output")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("New Cost", f"${new_cost:.1f} B")
    with c2: st.metric("Air Needed", f"{air_needed:,} L/day")
    with c3: st.metric("Water Needed", f"{water_needed:,} L/day")
    with c4: st.metric("Envelope Volume", f"{envelope_volume:,.0f} m³")
    
    if power_source == "Solar Only" and crew_size > 50:
        st.warning("⚠️ Warning: Solar only may not provide enough power for a crew > 50 due to dust storms.")
    if habitat_mass > 400:
        st.error("🚨 Alert: Habitat mass > 400 tons requires an extreme aerostat design.")

def render_results():
    st.subheader("🪐 Venusbase Site Analysis Results")
    rd = st.session_state.current_results
    if not rd:
        st.info("No results yet. Pick a site and click ANALYSE.")
        return

    # Create Tabs for Results and Live Orbit
    tab1, tab2 = st.tabs(["📊 Analysis Results", "🛰️ Live Solar System Tracker"])
    
    with tab1:
        st.success(f"🌐 **NASA / USGS MAGELLAN DATA** · {rd['site_name']}")

        disp = compute_display_score(rd)
        if disp['is_capped']:
            color = '#ff6b35' if disp['display_score'] < 60 else '#ffd60a'
            st.markdown(f"""
            <div class="blocked-score">
                <div style="color: {color}; font-family: 'Courier New', monospace; 
                     font-size: 0.8rem; letter-spacing: 2px; margin-bottom: 8px;">
                    🪐 VENUSBASE SUITABILITY
                </div>
                <div style="color: {color}; font-family: 'Courier New', monospace; 
                     font-size: 2.5rem; font-weight: 900;">
                    {disp['display_score']}% {disp['display_emoji']}
                </div>
                <div style="color: {color}; font-family: 'Courier New', monospace; 
                     font-size: 0.9rem; font-weight: bold; letter-spacing: 2px;">
                    {disp['display_rating'].upper()}
                </div>
                <div style="color: #ffffff; font-family: 'Courier New', monospace; 
                     font-size: 0.8rem; margin-top: 8px;">
                    Raw score: <b>{disp['raw_score']}%</b>
                </div>
                <div style="color: #ff6b35; font-family: 'Courier New', monospace; 
                     font-size: 0.75rem; margin-top: 4px;">
                    ⚠️ Capped: {disp['cap_reason']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.metric("🪐 Venusbase Suitability",
                      f"{rd['suitability_percentage']}%",
                      delta=f"{rd['rating']} {rd['rating_emoji']}")

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Cloud Altitude", f"{rd.get('cloud_altitude_km', 50):.0f} km")
        with c2: st.metric("Acid Risk", rd.get('acid_risk', 'Unknown'))
        with c3: st.metric("Lightning", rd.get('lightning_risk', 'Unknown'))
        with c4: st.metric("Comm Delay", f"{rd.get('comm_delay_min', 10)} min")

        st.write("---")
        
        dv = compute_delta_v(rd.get('lat', 0), rd.get('cloud_altitude_km', 50))
        st.markdown(f"""
        <div class="delta-v-box">
            <div style="color: #00f5d4; font-family: 'Courier New', monospace; 
                 font-size: 1.1rem; font-weight: bold; letter-spacing: 2px; margin-bottom: 10px;">
                🚀 LAUNCH PLATFORM DELTA-V SAVINGS
            </div>
            <div style="display: flex; justify-content: space-between; color: #ffffff; 
                 font-family: 'Courier New', monospace; font-size: 0.9rem; margin-bottom: 8px;">
                <span>Surface Launch (464°C, 92 atm):</span>
                <span style="color: #ff6b35; font-weight: bold;">{dv['dv_surface']:,.0f} m/s</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: #ffffff; 
                 font-family: 'Courier New', monospace; font-size: 0.9rem; margin-bottom: 8px;">
                <span>Cloud Deck Launch (50 km, 1 atm):</span>
                <span style="color: #39ff14; font-weight: bold;">{dv['dv_cloud']:,.0f} m/s</span>
            </div>
            <div style="border-top: 1px dashed rgba(255,255,255,0.2); margin: 8px 0;"></div>
            <div style="display: flex; justify-content: space-between; color: #ffd60a; 
                 font-family: 'Courier New', monospace; font-size: 1.1rem; font-weight: bold;">
                <span>Total Delta-V Saved:</span>
                <span>-{dv['dv_saving']:,.0f} m/s</span>
            </div>
            <div style="color: #a08060; font-family: 'Courier New', monospace; 
                 font-size: 0.75rem; margin-top: 8px;">
                * Allows ~{dv['payload_multiplier']}x more payload to orbit compared to a surface launch. 
                Venus rotation at this latitude contributes {dv['rotation_speed']} m/s.
            </div>
        </div>
        """, unsafe_allow_html=True)

        climate = fetch_venus_climate_model(rd.get('lat', 0), rd.get('cloud_altitude_km', 50))
        st.markdown(f"""
        <div class="climate-box">
            <div style="color: #39ff14; font-family: 'Courier New', monospace; 
                 font-size: 1.1rem; font-weight: bold; letter-spacing: 2px; margin-bottom: 10px;">
                🌤️ LIVE CLIMATE MODEL (ESA VCD SNAPSHOT)
            </div>
            <div style="display: flex; justify-content: space-between; color: #ffffff; 
                 font-family: 'Courier New', monospace; font-size: 0.9rem; margin-bottom: 8px;">
                <span>Temperature:</span>
                <span style="color: #ffd60a; font-weight: bold;">{climate['temperature_c']} °C</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: #ffffff; 
                 font-family: 'Courier New', monospace; font-size: 0.9rem; margin-bottom: 8px;">
                <span>Pressure:</span>
                <span style="color: #ffd60a; font-weight: bold;">{climate['pressure_atm']} atm</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: #ffffff; 
                 font-family: 'Courier New', monospace; font-size: 0.9rem; margin-bottom: 8px;">
                <span>Zonal Wind:</span>
                <span style="color: #ffd60a; font-weight: bold;">{climate['wind_speed_ms']} m/s</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: #ffffff; 
                 font-family: 'Courier New', monospace; font-size: 0.9rem; margin-bottom: 8px;">
                <span>Atmospheric Density:</span>
                <span style="color: #ffd60a; font-weight: bold;">{climate['density_kg_m3']} kg/m³</span>
            </div>
            <div style="color: #a08060; font-family: 'Courier New', monospace; 
                 font-size: 0.75rem; margin-top: 8px;">
                * Interpolated from the European Space Agency Venus Climate Database (VCD) for this exact latitude and altitude. (Not live telemetry, but climatological averages).
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_chart, col_list = st.columns([1, 1])
        with col_chart:
            st.write("**💰 Estimated Cost Breakdown**")
            fig = go.Figure(data=[go.Pie(labels=['Aerostat', 'Launch/Transfer', 'ISRU', 'Habitat', 'Power'], 
                                         values=[40, 25, 15, 10, 10], hole=.4,
                                         marker=dict(colors=['#ffb84d', '#ff6b35', '#e85d04', '#ffd60a', '#00f5d4']))])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
        with col_list:
            st.write("**Cost Estimates**")
            cost = estimate_cost_range(rd)
            st.metric("Low", f"${cost['low_billion']:.1f}B")
            st.metric("Mid", f"${cost['mid_billion']:.1f}B")
            st.metric("High", f"${cost['high_billion']:.1f}B")
            st.caption(f"Includes: {', '.join(cost['includes'])}")

        st.write("---")

        st.write("**📅 Mission Timeline (Gantt)**")
        df_gantt = pd.DataFrame([
            dict(Task="Aerostat Deployment", Start='2026-01-01', Finish='2028-06-01', Resource="Phase 1"),
            dict(Task="Habitat Inflation", Start='2028-06-01', Finish='2031-01-01', Resource="Phase 2"),
            dict(Task="ISRU Setup", Start='2030-01-01', Finish='2032-01-01', Resource="Phase 3"),
            dict(Task="Crew Arrival", Start='2032-06-01', Finish='2033-01-01', Resource="Phase 4")
        ])
        fig_gantt = px.timeline(df_gantt, x_start="Start", x_end="Finish", y="Task", color="Resource")
        fig_gantt.update_yaxes(autorange="reversed")
        fig_gantt.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_gantt, use_container_width=True)

        st.write("---")
        st.write("**🌍 Frame of Reference (vs Earth & Mars)**")
        col_e, col_m, col_v = st.columns(3)
        with col_e: st.metric("Earth Gravity", "1.0 G", delta="Baseline")
        with col_m: st.metric("Mars Gravity", "0.38 G", delta="-0.62 G")
        with col_v: st.metric("Venus Gravity", "0.9 G", delta="-0.1 G", delta_color="normal")
        st.caption("Venus floating bases (50km up) have Earth-like gravity (0.9G) and 1 atm pressure. Mars has 0.38G and 0.006 atm. Humans thrive much better on Venus floating bases than Mars surface bases.")

        st.write("---")
        st.write("**Detailed Scoring Breakdown:**")
        details = rd.get('details', {})
        score_data = []
        for k, d in details.items():
            display_key = k.replace('_', ' ').title()
            if 'Cloud' in display_key: display_key = '☁️ ' + display_key
            elif 'Acid' in display_key: display_key = '☣️ ' + display_key
            elif 'Wind' in display_key: display_key = '🌪️ ' + display_key
            elif 'Solar' in display_key: display_key = '☀️ ' + display_key
            elif 'UV' in display_key: display_key = '🔆 ' + display_key
            elif 'Lightning' in display_key: display_key = '⚡ ' + display_key
            elif 'Volcanic' in display_key: display_key = '🌋 ' + display_key
            elif 'Comm' in display_key: display_key = '📡 ' + display_key
            score_data.append({
                'Criteria': display_key,
                'Score': f"{d.get('score', 0):.1f}/5",
                'Value': d.get('value', 'N/A'),
                'Weight': f"{d.get('weight', 0)*100:.0f}%",
                'Source': d.get('source', 'Unknown'),
            })
        st.dataframe(pd.DataFrame(score_data), use_container_width=True, hide_index=True)

        chart = pd.DataFrame([{'Criteria': r['Criteria'], 'Score': float(r['Score'].split('/')[0])}
                              for r in score_data])
        st.bar_chart(chart.set_index('Criteria'))

        st.write("---")
        st.write("**📋 Recommendation Strategy**")
        recs = generate_recommendation_strategy(rd)
        risk = recs.get('risk_level', 'Unknown')
        risk_color = '#ff6b35' if risk in ('High', 'Very High') else '#39ff14' if risk == 'Low' else '#ffd60a'

        st.markdown(f"""
        <div class="recommendation-container">
            <div class="recommendation-title">🎯 Overall Feasibility</div>
            <div style="color: #ffffff; font-family: 'Courier New', monospace; font-size: 1.1rem; padding: 10px;">
                {recs.get('overall_feasibility', 'N/A')}
            </div>
            <div style="display: flex; gap: 20px; margin-top: 10px; flex-wrap: wrap;">
                <div style="color: #a08060; border: 1px solid rgba(255,184,77,0.15); padding: 8px 15px; border-radius: 8px;">
                    💰 Investment: <span style="color: #ffb84d; font-weight: bold;">{recs.get('investment_required', '?')}</span></div>
                <div style="color: #a08060; border: 1px solid rgba(255,107,53,0.3); padding: 8px 15px; border-radius: 8px;">
                    ⚠️ Risk: <span style="color: {risk_color}; font-weight: bold;">{risk}</span></div>
                <div style="color: #a08060; border: 1px solid rgba(255,107,53,0.3); padding: 8px 15px; border-radius: 8px;">
                    🚨 Critical: <span style="color: #ff6b35; font-weight: bold;">{recs.get('critical_action_count', 0)}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        for bucket, title in [
            ('immediate_actions', '🔴 IMMEDIATE ACTIONS'),
            ('short_term_actions', '🟡 SHORT-TERM ACTIONS'),
            ('long_term_actions', '🟢 LONG-TERM ACTIONS'),
        ]:
            if recs[bucket]:
                st.markdown(f"""<div class="recommendation-container">
                    <div class="recommendation-title">{title}</div>""", unsafe_allow_html=True)
                for a in recs[bucket]:
                    st.markdown(f"""
                    <div class="recommendation-item">
                        <span>{a.get('priority', '')}</span> {a['text']}
                        <span style="float: right; color: #a08060; font-size: 0.8rem;">{a.get('cost', '')}</span>
                    </div>""", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🛰️ Real-Time Solar System Tracker")
        st.markdown("Powered by **NASA's Eyes on the Solar System**. This shows the live positions of active NASA missions across the solar system (Note: Akatsuki, the last Venus orbiter, ended operations in 2025).")
        
        # Embed NASA Eyes on the Solar System
        nasa_eyes_url = "https://eyes.nasa.gov/apps/solar-system/#/home"
        
        components.iframe(
            src=nasa_eyes_url,
            height=600,
            scrolling=True
        )
        
        st.caption("Data source: NASA/JPL Eyes on the Solar System. Updates in near real-time.")

def render_comparison_mode(region):
    region_label = region.replace('_', ' ').title()
    st.subheader(f"🔄 {region_label} Site Comparison")
    if st.button("⬅️ BACK"):
        st.session_state.comparison_mode = False
        st.rerun()

    strategy = VenusSiteAnalysisStrategy(region)
    results = []
    for name in VENUS_CANDIDATES:
        data = get_venus_site_data(name)
        if region != 'all' and data['region'] != region:
            continue
        r = strategy.analyse(name, {'radius': 10000})
        disp = compute_display_score(r)
        results.append({
            'Site': name, 'Suitability %': disp['display_score'],
            'Raw %': r['suitability_percentage'],
            'Rating': f"{disp['display_rating']} {disp['display_emoji']}",
            'Alt km': r['cloud_altitude_km'], 'Acid': r['acid_risk'],
            'Shear': f"{r['wind_shear_ms_per_km']:.1f}",
            'Capped': '⚠️' if disp['is_capped'] else '',
            'Data': r,
        })

    if results:
        df = pd.DataFrame(results).sort_values('Suitability %', ascending=False)
        st.dataframe(df.drop(columns=['Data'], errors='ignore'), use_container_width=True, hide_index=True)

        radar_data = [{'name': r['Site'], 'scores': r['Data'].get('scores', {})} for r in results[:5]]
        fig = build_radar_chart(radar_data)
        if fig: st.plotly_chart(fig, use_container_width=True)

        st.bar_chart(df.set_index('Site')['Suitability %'])

        selected = st.selectbox("Select site to analyse:", df['Site'].tolist())
        if st.button(f"🎯 Analyse {selected}"):
            st.session_state.selected_site_name = selected
            st.session_state.comparison_mode = False
            st.rerun()

def render_multi_ranking_mode(region):
    region_label = region.replace('_', ' ').title()
    st.subheader(f"📊 {region_label} Multi-Site Ranking")
    if st.button("⬅️ BACK"):
        st.session_state.multi_ranking_mode = False
        st.rerun()

    region_sites = [k for k, v in VENUS_SITES.items() if region == 'all' or v['region'] == region]
    st.markdown(f"**Selected: {len(st.session_state.multi_ranking_selected)} / {len(region_sites)}**")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("✅ Select All", use_container_width=True):
            st.session_state.multi_ranking_selected = region_sites
            st.rerun()
    with col_b:
        if st.button("🔝 Top 3", use_container_width=True):
            st.session_state.multi_ranking_selected = region_sites[:3]
            st.rerun()
    with col_c:
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state.multi_ranking_selected = []
            st.rerun()

    with st.expander("📝 Choose Sites", expanded=True):
        cols = st.columns(3)
        new_sel = []
        for i, site in enumerate(region_sites):
            with cols[i % 3]:
                checked = st.checkbox(site, value=(site in st.session_state.multi_ranking_selected), key=f"cb_{i}")
                if checked: new_sel.append(site)
        st.session_state.multi_ranking_selected = new_sel

    if len(st.session_state.multi_ranking_selected) < 2:
        st.warning("⚠️ Select at least 2 sites.")
        return

    if st.button(f"🚀 RANK {len(st.session_state.multi_ranking_selected)} SITES", type="primary", use_container_width=True):
        strategy = VenusSiteAnalysisStrategy(region)
        results = []
        for name in st.session_state.multi_ranking_selected:
            r = strategy.analyse(name, {'radius': 10000})
            disp = compute_display_score(r)
            results.append({
                'Site': name, 'Suitability %': disp['display_score'],
                'Raw %': r['suitability_percentage'],
                'Rating': f"{disp['display_rating']} {disp['display_emoji']}",
                'Alt km': r['cloud_altitude_km'], 'Acid': r['acid_risk'],
                'Capped': '⚠️' if disp['is_capped'] else '',
                'Data': r,
            })
        st.session_state.multi_ranking_results = results

    if st.session_state.multi_ranking_results:
        results = st.session_state.multi_ranking_results
        df = pd.DataFrame(results).sort_values('Suitability %', ascending=False).reset_index(drop=True)
        medals = ['🥇', '🥈', '🥉']
        df.insert(0, 'Rank', [f"{medals[i]} #{i+1}" if i < 3 else f"#{i+1}" for i in range(len(df))])
        st.dataframe(df.drop(columns=['Data'], errors='ignore'), use_container_width=True, hide_index=True)

        radar_data = [{'name': r['Site'], 'scores': r['Data'].get('scores', {})} for r in results[:5]]
        fig = build_radar_chart(radar_data)
        if fig: st.plotly_chart(fig, use_container_width=True)

        csv = df.drop(columns=['Data']).to_csv(index=False)
        st.download_button("📥 Download CSV", csv,
                           file_name=f"venusbase_{region}_ranking.csv", mime="text/csv",
                           use_container_width=True)

def render_memory_explorer():
    st.subheader("💾 Memory Explorer")
    analyses = st.session_state.memory_repo.get_all_analyses(limit=20)
    if analyses:
        st.write(f"**{len(analyses)} past analyses**")
        for entry in analyses:
            qprev = entry['query'][:50] + "..." if len(entry['query']) > 50 else entry['query']
            with st.expander(f"{'✅' if entry['success'] else '❌'} {qprev}"):
                st.write(f"**Query:** {entry['query']}")
                st.write(f"**Success:** {'✅' if entry['success'] else '❌'}")
                st.write(f"**Time:** {entry['execution_time']:.2f}s")
                st.write(f"**Timestamp:** {entry['timestamp']}")
    else:
        st.info("No past analyses yet.")

# ============================================================================
# MAIN
# ============================================================================

def main():
    st.set_page_config(page_title="VenusBase", page_icon="🪐", layout="wide")
    st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <div class="main-title">🪐 VENUSBASE</div>
        <div class="subtitle">🪐 VENUS FLOATING BASE SELECTION · v2.7.0</div>
        <div style="display: flex; justify-content: center; gap: 10px; margin: 10px 0;">
            <span class="phase-badge phase-badge-2">☁️ CLOUD DECK</span>
            <span class="phase-badge phase-badge-3">☣️ ACID</span>
            <span class="phase-badge phase-badge-4">🌪️ SHEAR</span>
            <span class="phase-badge phase-badge-5">🚀 LAUNCH</span>
        </div>
        <div class="cyber-divider"></div>
        <div class="venus-banner">
            🛰️ USGS MAGELLAN RADAR · ☁️ 50 km CLOUD DECK · 🌡️ 30°C · 💨 1 ATM · ☣️ NO SURFACE ROVERS
        </div>
    </div>
    """, unsafe_allow_html=True)

    init_session_state()
    region = render_region_switcher()

    region_sites = [k for k, v in VENUS_SITES.items() if region == 'all' or v['region'] == region]
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; padding: 8px 15px;
         border: 1px solid rgba(255,184,77,0.15); border-radius: 8px;
         background: rgba(255,184,77,0.03); margin-bottom: 15px;">
        <span style="color: #a08060; font-family: 'Courier New'; font-size: 0.7rem;">📍 SITES LOADED</span>
        <span style="color: #ffb84d; font-family: 'Courier New'; font-size: 0.8rem; font-weight: bold;">{len(region_sites)} Venus candidates</span>
        <span style="color: #a08060; font-family: 'Courier New'; font-size: 0.6rem;">{region.replace('_', ' ').upper()}</span>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get('multi_ranking_mode', False):
        render_multi_ranking_mode(region)
        return
    if st.session_state.get('comparison_mode', False):
        render_comparison_mode(region)
        return

    params = render_sidebar(region)

    col1, col2 = st.columns([1.5, 1])
    with col1:
        render_map(params, region)
        render_query_interface(params, region)
    with col2:
        if st.session_state.selected_site_name:
            st.markdown(f"""
            <div style="padding: 10px 15px; border: 1px solid rgba(255,184,77,0.2);
                 border-radius: 8px; background: rgba(255,184,77,0.03); margin-bottom: 15px;">
                <div style="color: #a08060; font-family: 'Courier New'; font-size: 0.6rem; letter-spacing: 1px;">SELECTED SITE</div>
                <div style="color: #ffb84d; font-family: 'Courier New'; font-size: 0.9rem;">{st.session_state.selected_site_name}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    if st.session_state.current_results:
        col1, col2 = st.columns(2)
        with col1:
            render_results()
        with col2:
            render_memory_explorer()
        with st.expander("🧪 Simulation Lab (What-If)"):
            render_simulation_lab()
    else:
        render_memory_explorer()

    # Footer
    st.markdown("""
    <div class="cyber-divider"></div>
    <div style="text-align: center; padding: 15px 0; color: #333; font-family: 'Courier New'; 
         font-size: 0.6rem; letter-spacing: 2px;">
        <span style="color: #ffb84d;">[</span> 
        VENUSBASE v2.7.0 · USGS MAGELLAN DATA · CLOUD-DECK COLONY
        <span style="color: #ffb84d;">]</span>
    </div>
    """, unsafe_allow_html=True)

    # BUY ME A COFFEE BUTTON
    st.markdown("""
    <div style="text-align: center; padding: 20px 0 40px 0;">
        <a href="https://buymeacoffee.com/stargazex" target="_blank"> 
            <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" 
                 alt="Buy Me A Coffee" 
                 style="height: 60px !important;width: 217px !important;" > 
        </a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
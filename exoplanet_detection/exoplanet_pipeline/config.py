"""
Central configuration for the ISRO BAH 2026 exoplanet detection pipeline.

All pipeline modules import constants from this module so thresholds, paths,
and mission-specific defaults stay in one place.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

# ---------------------------------------------------------------------------
# Project layout
# ---------------------------------------------------------------------------

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
PACKAGE_ROOT: Final[Path] = Path(__file__).resolve().parent

DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
RAW_DATA_DIR: Final[Path] = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Final[Path] = DATA_DIR / "processed"
CACHE_DIR: Final[Path] = DATA_DIR / "cache"

OUTPUT_DIR: Final[Path] = PROJECT_ROOT / "output"
FIGURES_DIR: Final[Path] = OUTPUT_DIR / "figures"
REPORTS_DIR: Final[Path] = OUTPUT_DIR / "reports"
MODELS_DIR: Final[Path] = PROJECT_ROOT / "models"
LOGS_DIR: Final[Path] = PROJECT_ROOT / "logs"

PIPELINE_DIRS: Final[tuple[Path, ...]] = (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    CACHE_DIR,
    OUTPUT_DIR,
    FIGURES_DIR,
    REPORTS_DIR,
    MODELS_DIR,
    LOGS_DIR,
)

# ---------------------------------------------------------------------------
# Pipeline runtime
# ---------------------------------------------------------------------------

PIPELINE_NAME: Final[str] = "exoplanet_detection"
PIPELINE_VERSION: Final[str] = "0.1.0"

RANDOM_SEED: Final[int] = 42
N_JOBS: Final[int] = -1  # -1 = use all available CPU cores
MAX_WORKERS: Final[int] = 4
CHUNK_SIZE: Final[int] = 256

# ---------------------------------------------------------------------------
# Logging (consumed by logger.py)
# ---------------------------------------------------------------------------

LOG_LEVEL: Final[str] = "INFO"
LOG_FORMAT: Final[str] = "json"  # "json" | "text"
LOG_TO_FILE: Final[bool] = True
LOG_TO_CONSOLE: Final[bool] = True
LOG_FILE_NAME: Final[str] = "pipeline.log"
LOG_MAX_BYTES: Final[int] = 10 * 1024 * 1024  # 10 MiB
LOG_BACKUP_COUNT: Final[int] = 5
LOG_INCLUDE_TIMESTAMP: Final[bool] = True
LOG_INCLUDE_CALLER: Final[bool] = True

# ---------------------------------------------------------------------------
# Data acquisition (data_downloader.py)
# ---------------------------------------------------------------------------

SUPPORTED_MISSIONS: Final[tuple[str, ...]] = ("TESS", "Kepler", "K2")

DEFAULT_MISSION: Final[str] = "TESS"
DEFAULT_SECTOR: Final[int | None] = None
DEFAULT_TARGET: Final[str | None] = None

# MAST / lightkurve
MAST_BASE_URL: Final[str] = "https://mast.stsci.edu/api/v0/invoke"
MAST_TIMEOUT_SEC: Final[float] = 120.0
MAST_MAX_RETRIES: Final[int] = 3
MAST_RETRY_BACKOFF_SEC: Final[float] = 2.0

LIGHTCURVE_SEARCH_CACHE: Final[bool] = True
DOWNLOAD_QUALITY_BITMASK: Final[str] = "default"  # passed to lightkurve quality mask
MIN_OBSERVATIONS: Final[int] = 100
MAX_GAP_DAYS: Final[float] = 5.0

# Synthetic / offline demo mode (no network)
USE_SYNTHETIC_DATA: Final[bool] = False
SYNTHETIC_N_STARS: Final[int] = 50
SYNTHETIC_DURATION_DAYS: Final[float] = 27.4
SYNTHETIC_CADENCE_MIN: Final[float] = 2.0

# ---------------------------------------------------------------------------
# Time-series preprocessing
# ---------------------------------------------------------------------------

TIME_COLUMN: Final[str] = "time"
FLUX_COLUMN: Final[str] = "flux"
FLUX_ERR_COLUMN: Final[str] = "flux_err"
NORMALIZED_FLUX_COLUMN: Final[str] = "flux_norm"

FLUX_NORMALIZATION: Final[str] = "median"  # "median" | "mean"
OUTLIER_SIGMA: Final[float] = 5.0
MIN_VALID_FRACTION: Final[float] = 0.75

# ---------------------------------------------------------------------------
# Detrending (detrender.py)
# ---------------------------------------------------------------------------

DETREND_METHOD: Final[str] = "flatten"  # "flatten" | "savgol" | "biweight" | "poly"
DETREND_WINDOW_LENGTH: Final[int] = 401  # odd integer, in cadences
DETREND_POLY_DEGREE: Final[int] = 3
DETREND_BREAKTOLERANCE: Final[float] = 0.5

SAVGOL_WINDOW: Final[int] = 101
SAVGOL_POLYORDER: Final[int] = 3

BIWEIGHT_MAX_ITER: Final[int] = 10
BIWEIGHT_C: Final[float] = 6.0

SIGMA_CLIP_NSIGMA: Final[float] = 4.0
SIGMA_CLIP_MAXITERS: Final[int] = 5

# ---------------------------------------------------------------------------
# Period search (period_finder.py)
# ---------------------------------------------------------------------------

PERIOD_SEARCH_METHOD: Final[str] = "bls"  # "bls" | "tls" | "bls_tls"
PERIOD_MIN_DAYS: Final[float] = 0.5
PERIOD_MAX_DAYS: Final[float] = 30.0
PERIOD_OVERSAMPLE_FACTOR: Final[float] = 3.0
PERIOD_NTERMS: Final[int] = 1

# Box Least Squares (BLS)
BLS_DURATION_MIN_HOURS: Final[float] = 0.5
BLS_DURATION_MAX_HOURS: Final[float] = 24.0
BLS_NDURATIONS: Final[int] = 10
BLS_FREQUENCY_FACTOR: Final[float] = 0.25
BLS_MIN_SNR: Final[float] = 7.0
BLS_MIN_TRANSIT_COUNT: Final[int] = 2

# Transit Least Squares (TLS) — used for confirmation after BLS triage
TLS_SIGNAL_THRESHOLD: Final[float] = 5.0
TLS_SNR_THRESHOLD: Final[float] = 7.0
TLS_MIN_PERIOD: Final[float] = PERIOD_MIN_DAYS
TLS_MAX_PERIOD: Final[float] = PERIOD_MAX_DAYS

# Phase folding
PHASE_BINS: Final[int] = 200
PHASE_CENTER: Final[float] = 0.0

# Significance
SDE_THRESHOLD: Final[float] = 7.0  # Signal Detection Efficiency
FAP_THRESHOLD: Final[float] = 0.01  # False Alarm Probability

# ---------------------------------------------------------------------------
# Transit shape features (shape_features.py)
# ---------------------------------------------------------------------------

TRANSIT_DURATION_HOURS: Final[float] = 3.0  # default guess for fitting window
TRANSIT_DEPTH_PPT: Final[float] = 1.0  # parts per thousand

# Trapezoid / analytic model bounds
DEPTH_MIN_PPT: Final[float] = 0.05
DEPTH_MAX_PPT: Final[float] = 500.0
DURATION_MIN_HOURS: Final[float] = 0.25
DURATION_MAX_HOURS: Final[float] = 48.0

# Shape discriminators (planet U-shape vs EB V-shape)
SHAPE_ASYMMETRY_MAX: Final[float] = 0.35
SHAPE_V_DEPTH_RATIO_MIN: Final[float] = 0.15  # secondary eclipse indicator
SHAPE_INGRESS_EGRESS_RATIO_MAX: Final[float] = 2.5
SHAPE_ODDEVEN_DEPTH_TOLERANCE: Final[float] = 0.05

FEATURE_NAMES: Final[tuple[str, ...]] = (
    "period_days",
    "transit_depth_ppt",
    "transit_duration_hours",
    "impact_parameter",
    "ingress_duration_hours",
    "egress_duration_hours",
    "odd_even_depth_ratio",
    "secondary_depth_ppt",
    "phase_offset",
    "snr",
    "sde",
    "fap",
    "shape_asymmetry",
    "ingress_egress_ratio",
    "transit_count",
)

# ---------------------------------------------------------------------------
# Astrophysical vetting (vetting.py)
# ---------------------------------------------------------------------------

VETTING_TESTS_ENABLED: Final[bool] = True
VETTING_MIN_PASS_FRACTION: Final[float] = 0.70

# Individual vetting thresholds
VET_ODD_EVEN_MISMATCH_MAX: Final[float] = 0.20
VET_SECONDARY_ECLIPSE_MAX_PPT: Final[float] = 0.50
VET_GHOST_DIAGNOSTIC_MAX: Final[float] = 0.30
VET_CENTROID_OFFSET_MAX_ARCSEC: Final[float] = 1.0
VET_PERIOD_ALIASED_TOLERANCE: Final[float] = 0.02
VET_SNR_MIN: Final[float] = BLS_MIN_SNR
VET_TRANSIT_COUNT_MIN: Final[int] = BLS_MIN_TRANSIT_COUNT
VET_DURATION_PERIOD_RATIO_MAX: Final[float] = 0.25
VET_DEPTH_SNR_MIN: Final[float] = 7.0
VET_RESIDUAL_RMS_MAX: Final[float] = 1.5e-3
VET_MARSHALL_TEST_PVALUE_MIN: Final[float] = 0.05
VET_ROLLING_RMS_SPIKE_MAX: Final[float] = 3.0

# ---------------------------------------------------------------------------
# Classification (classifier.py)
# ---------------------------------------------------------------------------

CLASS_LABELS: Final[tuple[str, ...]] = (
    "transit",
    "eclipsing_binary",
    "blend",
    "other",
)

BINARY_LABEL: Final[str] = "transit"
DEFAULT_CLASSIFIER: Final[str] = "ensemble"  # "rules" | "ml" | "ensemble"

CLASSIFIER_MODEL_PATH: Final[Path] = MODELS_DIR / "classifier.joblib"
CLASSIFIER_CALIBRATION_PATH: Final[Path] = MODELS_DIR / "calibration.joblib"

CONFIDENCE_THRESHOLD: Final[float] = 0.65
HIGH_CONFIDENCE_THRESHOLD: Final[float] = 0.85
PHYSICS_VETO_ENABLED: Final[bool] = True

# Rule-based shortcuts
RULE_MIN_SNR_FOR_TRANSIT: Final[float] = 7.0
RULE_MAX_SECONDARY_FOR_PLANET: Final[float] = 0.10
RULE_MAX_ODD_EVEN_FOR_PLANET: Final[float] = 0.15

# ML ensemble weights (rules + models)
ENSEMBLE_RULE_WEIGHT: Final[float] = 0.35
ENSEMBLE_ML_WEIGHT: Final[float] = 0.65

# ---------------------------------------------------------------------------
# Habitability scoring (habitability.py)
# ---------------------------------------------------------------------------

HABITABILITY_ENABLED: Final[bool] = True

# Stellar reference defaults when metadata is missing
DEFAULT_STELLAR_TEFF_K: Final[float] = 5700.0
DEFAULT_STELLAR_RADIUS_RSUN: Final[float] = 1.0
DEFAULT_STELLAR_MASS_MSUN: Final[float] = 1.0

# HZ boundaries (Kasting et al. simplified, in AU)
HZ_INNER_AU: Final[float] = 0.95
HZ_OUTER_AU: Final[float] = 1.67

# Earth Similarity Index (ESI) reference values
ESI_REF_RADIUS_REARTH: Final[float] = 1.0
ESI_REF_MASS_MEARTH: Final[float] = 1.0
ESI_REF_DENSITY_GCM3: Final[float] = 5.51
ESI_REF_ESCAPE_VEL_KMS: Final[float] = 11.19
ESI_REF_SURFACE_TEMP_K: Final[float] = 288.0

ESI_WEIGHTS: Final[dict[str, float]] = {
    "radius": 0.57,
    "density": 1.07,
    "escape_velocity": 0.70,
    "surface_temperature": 5.58,
}

HABITABILITY_MIN_ESI: Final[float] = 0.0
HABITABILITY_MAX_ESI: Final[float] = 1.0

# ---------------------------------------------------------------------------
# Visualization (visualizer.py)
# ---------------------------------------------------------------------------

FIGURE_DPI: Final[int] = 150
FIGURE_FORMAT: Final[str] = "png"
FIGURE_FACECOLOR: Final[str] = "white"

PLOT_STYLE: Final[str] = "seaborn-v0_8-darkgrid"
COLOR_TRANSIT: Final[str] = "#2ecc71"
COLOR_ECLIPSE: Final[str] = "#e74c3c"
COLOR_BLEND: Final[str] = "#f39c12"
COLOR_OTHER: Final[str] = "#95a5a6"
COLOR_PHASED: Final[str] = "#3498db"
COLOR_RAW: Final[str] = "#bdc3c7"
COLOR_DETRENDED: Final[str] = "#2c3e50"

VETTING_SHEET_TITLE: Final[str] = "Exoplanet Candidate Vetting Sheet"
REPORT_MAX_PAGES: Final[int] = 3

# ---------------------------------------------------------------------------
# run_pipeline.py orchestration
# ---------------------------------------------------------------------------

PIPELINE_STAGES: Final[tuple[str, ...]] = (
    "download",
    "detrend",
    "period_search",
    "shape_features",
    "vetting",
    "classify",
    "habitability",
    "visualize",
)

STOP_ON_DOWNLOAD_FAILURE: Final[bool] = True
SAVE_INTERMEDIATE: Final[bool] = True
INTERMEDIATE_FORMAT: Final[str] = "parquet"  # "parquet" | "csv" | "pickle"

RESULTS_FILENAME: Final[str] = "pipeline_results.json"
SUMMARY_FILENAME: Final[str] = "pipeline_summary.csv"


def ensure_pipeline_dirs() -> None:
    """Create standard pipeline directories if they do not exist."""
    for directory in PIPELINE_DIRS:
        directory.mkdir(parents=True, exist_ok=True)

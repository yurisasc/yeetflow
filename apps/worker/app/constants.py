"""
Application constants and configuration values.
"""

# API Configuration
API_V1_PREFIX = "/api/v1"
API_TITLE = "YeetFlow Worker"
API_VERSION = "0.1.0"

# Pagination Configuration
MAX_RUN_LIST_LIMIT = 200

# Authentication Configuration
BOOTSTRAP_USER_EMAIL = "system@yeetflow.local"

# Service Information
SERVICE_NAME = "yeetflow-worker"

# HTTP Status Ranges (upper bound exclusive for 5xx)
SERVER_ERROR_MAX = 600  # exclusive upper bound for 5xx (500-599)

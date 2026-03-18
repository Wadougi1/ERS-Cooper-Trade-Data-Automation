"""
Module: config.py
Project: ERS Cooper Trade Data Automation
Description: Handles environment variables and API credentials for the ERS Project.
Author: Douglas Akwasi Kwarteng
Date: 2025
"""

import os

# FAS/PSD API Key
# Recommendation: Set this as an environment variable in your shell or CI/CD pipeline.
# Example: export FAS_API_KEY="your_actual_key_here"
FAS_API_KEY = os.getenv("FAS_API_KEY", "7099eTZAR5I3JIAb6DwJYN9KivJQypIDUVtIChbO")

# Global Request Timeout (seconds)
TIMEOUT = 30

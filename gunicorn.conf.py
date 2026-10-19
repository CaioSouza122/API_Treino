"""Gunicorn settings, loaded automatically when gunicorn starts from the project root.

A Gemini call takes ~20s, so the default (1 sync worker, 30s timeout) serves one
user at a time and kills slower generations with a 502.
"""

import os

bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = int(os.getenv('WEB_CONCURRENCY', '2'))
threads = int(os.getenv('GUNICORN_THREADS', '4'))
timeout = 120
accesslog = "-"

#!/usr/bin/env python
# filepath: /home/adeeb/Documents/checksqs/run_monitor.py
"""
Script to run the Prometheus metrics server for Celery monitoring.
This exposes Celery metrics that can be scraped by Prometheus.
"""
from celery_app import app
import celery_prometheus_exporter

if __name__ == '__main__':
    print("Starting Celery Prometheus metrics server on port 8888...")
    print("You can access the metrics at: http://localhost:8888/metrics")
    celery_prometheus_exporter.start_httpd('0.0.0.0:8888')

"""
Plotly Dash Enterprise Configuration
This file contains enterprise-specific configurations and optimizations
"""

import dash
from dash import dcc, html
import dash_enterprise_auth
import redis
import os

# Enterprise Authentication Configuration
def configure_enterprise_auth(app):
    """Configure enterprise authentication"""
    auth = dash_enterprise_auth.create_auth(app)
    
    # LDAP Configuration (if using LDAP)
    auth.config.update({
        'LDAP_HOST': os.getenv('LDAP_HOST', 'ldap://your-ldap-server.com'),
        'LDAP_BASE_DN': os.getenv('LDAP_BASE_DN', 'dc=company,dc=com'),
        'LDAP_USER_DN': os.getenv('LDAP_USER_DN', 'ou=users'),
        'LDAP_GROUP_DN': os.getenv('LDAP_GROUP_DN', 'ou=groups'),
    })
    
    return auth

# Redis Configuration for Caching
def configure_redis_cache():
    """Configure Redis for enterprise caching"""
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 0)),
        password=os.getenv('REDIS_PASSWORD', None)
    )
    return redis_client

# Performance Optimization Settings
ENTERPRISE_CONFIG = {
    'serve_locally': False,  # Use CDN for better performance
    'assets_folder': 'assets',
    'assets_url_path': '/assets/',
    'include_assets_files': True,
    'assets_ignore': '',
    'eager_loading': True
}

# Database Connection Pool Configuration
DATABASE_CONFIG = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_timeout': 30,
    'pool_recycle': 3600,
    'echo': False  # Set to True for SQL debugging
}

# Monitoring and Logging Configuration
MONITORING_CONFIG = {
    'enable_metrics': True,
    'metrics_endpoint': '/metrics',
    'log_level': 'INFO',
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Security Headers
SECURITY_HEADERS = {
    'X-Frame-Options': 'DENY',
    'X-Content-Type-Options': 'nosniff',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'"
}

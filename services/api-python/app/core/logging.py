"""
TrustNet Logging Configuration
Structured logging setup for Google Cloud environments.
"""

import logging
import logging.config
import sys
from typing import Dict, Any
import json
from pythonjsonlogger import jsonlogger

from .config import settings


class StructuredFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        
        # Add standard fields
        log_record['severity'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        if hasattr(record, 'processing_time'):
            log_record['processing_time_ms'] = record.processing_time


def setup_logging():
    """Configure application logging."""
    
    # Base logging configuration
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'structured': {
                '()': StructuredFormatter,
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
            },
            'simple': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'structured' if settings.STRUCTURED_LOGGING else 'simple',
                'stream': sys.stdout
            }
        },
        'loggers': {
            'app': {
                'level': settings.LOG_LEVEL,
                'handlers': ['console'],
                'propagate': False
            },
            'uvicorn': {
                'level': settings.LOG_LEVEL,
                'handlers': ['console'],
                'propagate': False
            },
            'uvicorn.access': {
                'level': settings.LOG_LEVEL,
                'handlers': ['console'],
                'propagate': False
            },
            'google.cloud': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': settings.LOG_LEVEL,
            'handlers': ['console']
        }
    }
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Configure Google Cloud libraries
    if settings.ENVIRONMENT == "production":
        # In production, use Google Cloud Logging
        try:
            from google.cloud import logging as cloud_logging
            client = cloud_logging.Client()
            client.setup_logging()
        except ImportError:
            # Fallback to console logging
            pass


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(f"app.{name}")


# Context manager for request logging
class RequestLogger:
    """Context manager for adding request context to logs."""
    
    def __init__(self, request_id: str, user_id: str = None):
        self.request_id = request_id
        self.user_id = user_id
        self.old_factory = logging.getLogRecordFactory()
    
    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            record.request_id = self.request_id
            if self.user_id:
                record.user_id = self.user_id
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)
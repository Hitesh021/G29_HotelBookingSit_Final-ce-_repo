import sys
print(f"Python path: {sys.path}")
try:
    import requests
    print(f"Successfully imported requests version: {requests.__version__}")
except ImportError as e:
    print(f"Import error: {e}") 
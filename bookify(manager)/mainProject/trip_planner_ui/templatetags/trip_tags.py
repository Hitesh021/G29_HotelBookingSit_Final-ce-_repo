from django import template
import json
from decimal import Decimal

register = template.Library()

class DecimalEncoder(json.JSONEncoder):
    # Custom JSON encoder to handle Decimal types gracefully
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convert Decimal to float for JSON serialization.
            # Be aware of potential precision issues with float if high precision is critical.
            # Alternatively, convert to string: return str(obj)
            return float(obj) 
        # Let the base class default method raise the TypeError for other types
        return json.JSONEncoder.default(self, obj)

@register.filter
def jsonify(value):
    """
    Safely convert a Python dictionary (potentially with Decimals) to a JSON string
    suitable for embedding in HTML attributes.
    Returns 'null' string if input is None or not serializable.
    """
    if value is None:
        return 'null'
    try:
        # Use the custom encoder to handle potential Decimal types
        return json.dumps(value, cls=DecimalEncoder)
    except TypeError:
        # If serialization fails for any other reason, return 'null'
        return 'null' 
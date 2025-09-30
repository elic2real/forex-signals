"""Application constants and error codes for better maintainability"""

# Error codes for API responses
class ErrorCodes:
    SUCCESS = 0
    INVALID_REQUEST = 1001
    MISSING_PARAMETER = 1002
    INVALID_PARAMETER = 1003
    AUTHENTICATION_FAILED = 2001
    AUTHORIZATION_FAILED = 2002
    RESOURCE_NOT_FOUND = 3001
    RESOURCE_CONFLICT = 3002
    RATE_LIMIT_EXCEEDED = 4001
    INTERNAL_SERVER_ERROR = 5001
    SERVICE_UNAVAILABLE = 5002
    EXTERNAL_SERVICE_ERROR = 5003

# HTTP status codes with descriptive names
class HTTPStatus:
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504

# Application configuration constants
class Config:
    # Database
    MAX_CONNECTION_POOL_SIZE = 20
    CONNECTION_TIMEOUT_SECONDS = 30
    
    # API rate limiting
    REQUESTS_PER_MINUTE = 60
    BURST_REQUESTS = 10
    
    # Firebase
    FCM_BATCH_SIZE = 500
    FCM_RETRY_ATTEMPTS = 3
    FCM_TIMEOUT_SECONDS = 10
    
    # Trading
    MAX_INSTRUMENTS_PER_REQUEST = 50
    DEFAULT_CANDLE_COUNT = 100
    MAX_CANDLE_COUNT = 5000
    
    # Caching
    PRICE_CACHE_SECONDS = 1
    POSITION_CACHE_SECONDS = 30
    INSTRUMENT_CACHE_SECONDS = 3600

# Error messages for better UX
class ErrorMessages:
    INVALID_INSTRUMENT = "Invalid trading instrument provided"
    INVALID_SIGNAL_ID = "Signal ID must be a valid string"
    MISSING_FCM_TOKEN = "FCM token is required for device registration"
    INVALID_FCM_TOKEN = "FCM token format is invalid"
    MARKET_CLOSED = "Markets are currently closed"
    SPREAD_TOO_WIDE = "Spread is too wide for trading"
    INSUFFICIENT_DATA = "Insufficient market data for analysis"
    POSITION_EXISTS = "Position already exists for this instrument"
    SERVICE_UNAVAILABLE = "Trading service is temporarily unavailable"
    RATE_LIMITED = "Too many requests, please try again later"
    AUTHENTICATION_REQUIRED = "Valid authentication is required"
    INTERNAL_ERROR = "An internal error occurred, please try again"

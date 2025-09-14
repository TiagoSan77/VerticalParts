# Configuração da API - VerticalParts

# URLs da API
API_BASE_URL = "http://localhost:5000"
API_PRODUCTION_URL = "http://192.168.0.19:5000"

# Endpoints principais
ENDPOINTS = {
    "login": "/api/login",
    "visitors": "/api/visitors", 
    "cards": "/api/cards",
    "users": "/api/users",
    "stats": "/api/stats",
    "search": "/api/search/visitors",
    "assign_card": "/api/cards/assign",
    "return_card": "/api/cards/return",
    "recent_returns": "/api/recent-returns"
}

# Headers padrão
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Configurações do sistema
SYSTEM_CONFIG = {
    "max_visitors": 1000,
    "total_cards": 11,
    "session_timeout": 3600,  # 1 hora
    "max_file_size": 5242880,  # 5MB para fotos
    "supported_image_types": ["image/jpeg", "image/png", "image/webp"]
}

# Status codes esperados
HTTP_STATUS = {
    "success": 200,
    "created": 201, 
    "bad_request": 400,
    "unauthorized": 401,
    "not_found": 404,
    "server_error": 500
}

# Tipos de cartão
CARD_TYPES = {
    "visitor": ["VISITANTE 001", "VISITANTE 002", "VISITANTE 003", "VISITANTE 004", "VISITANTE 005"],
    "service": ["PRESTADOR DE SERVIÇO 001", "PRESTADOR DE SERVIÇO 002", "PRESTADOR DE SERVIÇO 003"], 
    "temporary": ["PROVISÓRIO 001", "PROVISÓRIO 002", "PROVISÓRIO 003"]
}

# Tipos de usuário
USER_TYPES = {
    "admin": "admin",
    "common": "common"
}

# Status de visitante
VISITOR_STATUS = {
    "pending": "pending",
    "active": "active", 
    "left": "left"
}

# Motivos de visita
VISIT_REASONS = [
    "PRESTADOR DE SERVIÇO",
    "VISITA COMERCIAL", 
    "ENTREVISTA",
    "PROVISÓRIO"
]
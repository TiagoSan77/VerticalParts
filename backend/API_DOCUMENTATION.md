# 🚀 API Documentation - Sistema de Controle de Acesso VerticalParts

## 📋 Informações Gerais

- **Base URL**: `http://localhost:5000` ou `http://192.168.0.19:5000`
- **Formato**: JSON
- **CORS**: Habilitado para todas as origens

## 🔐 Rotas de Autenticação

### POST `/api/login`
Autentica um usuário no sistema.

**Body:**
```json
{
  "email": "admin@verticalparts.com.br",
  "password": "12345678"
}
```

**Response Success (200):**
```json
{
  "success": true,
  "message": "Login realizado com sucesso",
  "user": {
    "_id": "...",
    "username": "admin",
    "email": "admin@verticalparts.com.br",
    "name": "Administrador",
    "userType": "admin",
    "createdAt": "01/01/2025 00:00:00",
    "lastLogin": "13/09/2025 14:30:00"
  }
}
```

### POST `/api/change-password`
Altera a senha do usuário logado.

**Body:**
```json
{
  "userEmail": "admin@verticalparts.com.br",
  "currentPassword": "12345678",
  "newPassword": "novaSenha123",
  "changedBy": "Administrador"
}
```

## 👥 Rotas de Visitantes

### GET `/api/visitors`
Retorna todos os visitantes cadastrados.

**Response Success (200):**
```json
{
  "success": true,
  "visitors": [
    {
      "_id": "...",
      "id": 1694688000000,
      "name": "João Silva",
      "document": "123.456.789-00",
      "phone": "(11) 99999-9999",
      "visitReason": "VISITA COMERCIAL",
      "visitResponsible": "Maria Santos",
      "observations": "",
      "entryTime": "13/09/2025 14:30:00",
      "status": "active",
      "cardNumber": "VISITANTE 001",
      "registeredBy": "Recepção"
    }
  ]
}
```

### POST `/api/visitors`
Cadastra um novo visitante.

**Body:**
```json
{
  "name": "João Silva",
  "document": "123.456.789-00",
  "phone": "(11) 99999-9999",
  "visitReason": "VISITA COMERCIAL",
  "visitResponsible": "Maria Santos",
  "observations": "Reunião às 15h",
  "photo": "data:image/jpeg;base64,...",
  "registeredBy": "Recepção"
}
```

### PUT `/api/visitors/{visitor_id}`
Atualiza dados de um visitante.

**Body:**
```json
{
  "status": "active",
  "cardNumber": "VISITANTE 001",
  "cardAssignedAt": "13/09/2025 14:35:00",
  "cardAssignedBy": "Administrador"
}
```

### DELETE `/api/visitors/{visitor_id}?deletedBy=Administrador`
Deleta um visitante (apenas administradores).

## 🎫 Rotas de Cartões

### GET `/api/cards`
Retorna todos os cartões de acesso.

**Response Success (200):**
```json
{
  "success": true,
  "cards": [
    {
      "_id": "...",
      "number": "VISITANTE 001",
      "status": "available",
      "visitor": null
    },
    {
      "_id": "...",
      "number": "VISITANTE 002",
      "status": "in-use",
      "visitor": "João Silva"
    }
  ]
}
```

### POST `/api/cards/assign`
Atribui um cartão a um visitante.

**Body:**
```json
{
  "visitorId": "66e4a1b2c3d4e5f6a7b8c9d0",
  "cardNumber": "VISITANTE 001",
  "assignedBy": "Administrador"
}
```

### POST `/api/cards/return`
Devolve um cartão e registra saída do visitante.

**Body:**
```json
{
  "searchTerm": "João Silva"
}
```

## 👤 Rotas de Usuários (Apenas Administradores)

### GET `/api/users`
Retorna todos os usuários do sistema.

### POST `/api/users`
Cria um novo usuário.

**Body:**
```json
{
  "name": "Novo Usuário",
  "email": "novo@verticalparts.com.br",
  "password": "senha123",
  "userType": "common",
  "createdBy": "Administrador"
}
```

### PUT `/api/users/{user_email}/toggle-type`
Alterna o tipo de usuário (admin ↔ common).

**Body:**
```json
{
  "changedBy": "Administrador"
}
```

### PUT `/api/users/{user_email}/reset-password`
Reseta a senha de um usuário.

**Body:**
```json
{
  "newPassword": "novaSenha123",
  "resetBy": "Administrador"
}
```

### DELETE `/api/users/{user_email}`
Deleta um usuário do sistema.

## 📊 Rotas de Estatísticas e Relatórios

### GET `/api/stats`
Retorna estatísticas gerais do sistema.

**Response Success (200):**
```json
{
  "success": true,
  "stats": {
    "visitors": {
      "total": 10,
      "active": 3,
      "pending": 1
    },
    "cards": {
      "total": 11,
      "available": 8,
      "inUse": 3
    },
    "users": {
      "total": 5,
      "admin": 2,
      "common": 3
    }
  }
}
```

### GET `/api/recent-returns?limit=5`
Retorna as devoluções mais recentes.

### GET `/api/search/visitors?term=João`
Busca visitantes por nome, documento ou telefone.

## 🛠️ Usuários Pré-configurados

| E-mail | Senha | Tipo | Nome |
|--------|-------|------|------|
| admin@verticalparts.com.br | 12345678 | admin | Administrador |
| recepcao@verticalparts.com.br | recepcao123 | common | Recepção |
| seguranca@verticalparts.com.br | seguranca123 | common | Segurança |
| giovanna@verticalparts.com.br | 123456 | common | Giovanna |
| geovane.silva@verticalparts.com.br | 123456 | admin | Geovane Silva |

## 🎫 Cartões Pré-configurados

- **VISITANTE 001-005** (5 cartões)
- **PRESTADOR DE SERVIÇO 001-003** (3 cartões) 
- **PROVISÓRIO 001-003** (3 cartões)

**Total: 11 cartões**

## 📝 Códigos de Status HTTP

- **200**: Sucesso
- **201**: Criado com sucesso
- **400**: Dados inválidos ou incompletos
- **401**: Não autorizado (credenciais inválidas)
- **404**: Não encontrado
- **500**: Erro interno do servidor

## 💾 Estrutura do Banco de Dados

### Collections:
- **visitors**: Dados dos visitantes
- **cards**: Status e atribuições dos cartões
- **users**: Usuários do sistema
- **returns**: Histórico de devoluções

## 🔒 Segurança

- ✅ CORS habilitado
- ✅ Validação de dados obrigatórios
- ✅ Verificação de permissões (admin vs common)
- ✅ Histórico de alterações para auditoria
- ⚠️ Senhas em texto plano (desenvolvimento)

## 🚀 Como Testar

### Teste de Login:
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@verticalparts.com.br","password":"12345678"}'
```

### Teste de Estatísticas:
```bash
curl http://localhost:5000/api/stats
```

### Teste de Cartões:
```bash
curl http://localhost:5000/api/cards
```
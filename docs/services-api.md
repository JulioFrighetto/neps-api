# API de Serviços (Services)

Base URL: `/api/v1`

## Endpoints

### Listar todos os serviços

```
GET /services
```

**Query Parameters:**
| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| skip | int | 0 | Número de registros a pular |
| limit | int | 100 | Limite de registros retornados |

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Serviço de Estágio",
    "region_id": 1,
    "is_active": true,
    "user_id": 10,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
]
```

---

### Obter um serviço específico

```
GET /services/{service_id}
```

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| service_id | int | ID do serviço |

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Serviço de Estágio",
  "region_id": 1,
  "is_active": true,
  "user_id": 10,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

**Error Responses:**
- `404 Not Found` - Serviço não encontrado

---

### Criar um serviço

```
POST /services
```

**Request Body:**
```json
{
  "name": "Nome do Serviço",
  "region_id": 1,
  "is_active": true,
  "user_name": "Nome do Usuário",       // opcional
  "user_email": "email@exemplo.com"     // opcional
}
```

**Parâmetros:**
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| name | string | Sim | Nome do serviço (único) |
| region_id | int | Não | ID da região associada |
| is_active | bool | Não | Status do serviço (padrão: true) |
| user_name | string | Não | Nome do usuário responsável |
| user_email | string | Não | Email do usuário responsável |

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "Nome do Serviço",
  "region_id": 1,
  "is_active": true,
  "user_id": 10,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

**Error Responses:**
- `409 Conflict` - Já existe serviço com este nome
- `409 Conflict` - Já existe usuário com este email

---

### Atualizar um serviço

```
PATCH /services/{service_id}
```

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| service_id | int | ID do serviço |

**Request Body:**
```json
{
  "name": "Novo Nome",
  "region_id": 2,
  "is_active": false
}
```

**Parâmetros (todos opcionais):**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| name | string | Novo nome do serviço |
| region_id | int | Nova região associada |
| is_active | bool | Novo status |

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Novo Nome",
  "region_id": 2,
  "is_active": false,
  "user_id": 10,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-20T14:00:00"
}
```

**Error Responses:**
- `404 Not Found` - Serviço não encontrado

---

### Excluir um serviço

```
DELETE /services/{service_id}
```

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| service_id | int | ID do serviço |

**Response:** `204 No Content`

**Error Responses:**
- `404 Not Found` - Serviço não encontrado

---

## Endpoints de Regiões

Para obter a lista de regiões disponíveis (para popular selects, etc):

```
GET /regions
```

**Query Parameters:**
| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| skip | int | 0 | Número de registros a pular |
| limit | int | 100 | Limite de registros retornados |

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "São Paulo",
    "priority_education_institute": null,
    "is_active": true
  },
  {
    "id": 2,
    "name": "Rio de Janeiro",
    "priority_education_institute": 5,
    "is_active": true
  }
]
```

---

```
GET /regions/{region_id}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "São Paulo",
  "priority_education_institute": null,
  "is_active": true
}
```

---

## Schemas completos

### ServiceResponse
```typescript
interface ServiceResponse {
  id: number;
  name: string;
  region_id: number | null;
  is_active: boolean;
  user_id: number | null;
  created_at: string;  // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
}
```

### ServiceCreate
```typescript
interface ServiceCreate {
  name: string;
  region_id?: number | null;
  is_active?: boolean;
  user_name?: string | null;
  user_email?: string | null;
}
```

### ServiceUpdate
```typescript
interface ServiceUpdate {
  name?: string | null;
  region_id?: number | null;
  is_active?: boolean | null;
}
```

### RegionResponse
```typescript
interface RegionResponse {
  id: number;
  name: string;
  priority_education_institute: number | null;
  is_active: boolean;
}
```

---

## Exemplos de uso

### Listar serviços com região
```javascript
const response = await fetch('/api/v1/services');
const services = await response.json();
```

### Criar serviço vinculado a uma região
```javascript
const response = await fetch('/api/v1/services', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Centro de Estágios SP',
    region_id: 1,
    is_active: true
  })
});
```

### Atualizar região de um serviço
```javascript
const response = await fetch('/api/v1/services/1', {
  method: 'PATCH',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    region_id: 2
  })
});
```

### Carregar regiões para um select
```javascript
const response = await fetch('/api/v1/regions');
const regions = await response.json();
// regions.map(r => `<option value="${r.id}">${r.name}</option>`)
```
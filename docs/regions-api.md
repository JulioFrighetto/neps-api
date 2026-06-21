# API de Territórios (Regions)

Base URL: `/api/v1`

## Endpoints

### Listar todas as regiões

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

### Obter um território específica

```
GET /regions/{region_id}
```

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| region_id | int | ID da território |

**Response:** `200 OK`

```json
{
  "id": 1,
  "name": "São Paulo",
  "is_active": true
}
```

**Error Responses:**

- `404 Not Found` - Território não encontrada

---

### Criar uma território

```
POST /regions
```

**Request Body:**

```json
{
  "name": "Nome da Território",
  "is_active": true
}
```

**Parâmetros:**
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| name | string | Sim | Nome da território |
| is_active | bool | Não | Status da território (padrão: true) |

**Response:** `201 Created`

```json
{
  "id": 1,
  "name": "Nome da Território",
  "is_active": true
}
```

**Error Responses:**

- `422 Unprocessable Entity` - Dados inválidos

---

### Atualizar uma território

```
PATCH /regions/{region_id}
```

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| region_id | int | ID da território |

**Request Body:**

```json
{
  "name": "Novo Nome",
  "is_active": false
}
```

**Parâmetros (todos opcionais):**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| name | string | Novo nome da território |
| is_active | bool | Novo status |

**Response:** `200 OK`

```json
{
  "id": 1,
  "name": "Novo Nome",
  "is_active": false
}
```

**Error Responses:**

- `404 Not Found` - Território não encontrada

---

### Excluir uma território

```
DELETE /regions/{region_id}
```

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| region_id | int | ID da território |

**Response:** `204 No Content`

**Error Responses:**

- `404 Not Found` - Território não encontrada

**Observação:** A exclusão pode falhar se houver serviços ou outros registros dependentes associados a esta território.

---

## Schemas completos

### RegionResponse

```typescript
interface RegionResponse {
  id: number;
  name: string;
  is_active: boolean;
}
```

### RegionCreate

```typescript
interface RegionCreate {
  name: string;
  is_active?: boolean;
}
```

### RegionUpdate

```typescript
interface RegionUpdate {
  name?: string | null;
  is_active?: boolean | null;
}
```

---

## Exemplos de uso

### Listar todas as regiões

```javascript
const response = await fetch("/api/v1/regions");
const regions = await response.json();
```

### Criar uma território

```javascript
const response = await fetch("/api/v1/regions", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    name: "Brasília",
    is_active: true,
  }),
});
```

### Atualizar uma território

```javascript
const response = await fetch("/api/v1/regions/1", {
  method: "PATCH",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    name: "São Paulo - Capital",
  }),
});
```

### Excluir uma território

```javascript
const response = await fetch("/api/v1/regions/1", {
  method: "DELETE",
});
// Response: 204 No Content
```

### Listar regiões inativas

```javascript
const response = await fetch("/api/v1/regions?limit=100");
const allRegions = await response.json();
const inactiveRegions = allRegions.filter((r) => !r.is_active);
```

---

## Validações

- **name**: Obrigatório, máximo 50 caracteres
- **is_active**: Padrão é `true`

---

## Observações

- As regiões podem ter serviços associados (`Internships.region_id`)

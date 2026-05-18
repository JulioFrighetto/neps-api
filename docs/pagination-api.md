# Documentação de Paginação - NEPS API

Todas as rotas `GET` que retornam listas agora seguem o padrão de paginação.

## Formato de Resposta

Todas as rotas de listagem retornam um objeto `Page` com a seguinte estrutura:

```jso
{
  "items": [...],
  "total": 150,
  "skip": 0,
  "limit": 100,
  "has_next": true
}
```

Parâmetros de query:
- `skip` (padrão: 0) - número de registros a pular
- `limit` (padrão: 100) - número máximo de registros por página

## Rotas Atualizadas

| Método | Endpoint | Response Model |
|--------|----------|----------------|
| GET | `/api/v1/users/` | `Page[UserResponse]` |
| GET | `/api/v1/students/` | `Page[StudentResponse]` |
| GET | `/api/v1/students/by-course/{course_id}` | `Page[StudentResponse]` |
| GET | `/api/v1/students/by-institute/{institute_id}` | `Page[StudentResponse]` |
| GET | `/api/v1/services/` | `Page[ServiceResponse]` |
| GET | `/api/v1/service-rooms/` | `Page[ServiceRoomResponse]` |
| GET | `/api/v1/service-rooms/by-service/{service_id}` | `Page[ServiceRoomResponse]` |
| GET | `/api/v1/service-schedules/` | `Page[ServiceScheduleResponse]` |
| GET | `/api/v1/education-institutes/` | `Page[EducationInstituteResponse]` |
| GET | `/api/v1/cadastros/institutions/` | `Page[EducationInstituteResponse]` |
| GET | `/api/v1/internship-field` | `Page[InternshipFieldResponse]` |
| GET | `/api/v1/regions` | `Page[RegionResponse]` |
| GET | `/api/v1/rooms/` | `Page[RoomResponse]` |
| GET | `/api/v1/rooms/by-internship_field/{internship_field_id}` | `Page[RoomResponse]` |
| GET | `/api/v1/courses/` | `Page[CourseResponse]` |
| GET | `/api/v1/internships` | `Page[InternshipResponse]` |
| GET | `/api/v1/internships/by-field/{field_id}` | `Page[InternshipResponse]` |
| GET | `/api/v1/internships/by-education-institute/{edu_institute_id}` | `Page[InternshipResponse]` |
| GET | `/api/v1/internships/by-room/{room_id}` | `Page[InternshipResponse]` |

## Exemplo de Uso

```bash
# Primeira página com 10 itens por página
curl "http://localhost:8000/api/v1/users/?skip=0&limit=10"

# Segunda página
curl "http://localhost:8000/api/v1/users/?skip=10&limit=10"
```

## Atualização no Frontend

O frontend precisa adaptar os consumidores dessas rotas para tratar o novo formato:

**Antes:**
```javascript
const users = response.data; // array
```

**Depois:**
```javascript
const users = response.data.items; // array
const total = response.data.total;
const hasNext = response.data.has_next;
```
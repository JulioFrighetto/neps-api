# Histórico de Período — API

Este documento descreve o endpoint usado pelo frontend para montar a tela de histórico do período.

## Objetivo

A entidade `history` registra o vínculo e o desvínculo de alunos em um período.

Cada registro contém:

- o `period_id` do período;
- o `student_id` do aluno;
- o `schedule_id` do horário vinculado, quando disponível;
- o `room_id` da sala vinculada, quando disponível;
- `start_date` com a data de início do vínculo;
- `end_date` com a data de fim do vínculo, quando o aluno é desvinculado.

---

## Endpoint

### Listar histórico de um período

```
GET /api/v1/histories/by-period/{period_id}
```

**Descrição:**

Retorna a lista paginada de vínculos históricos de um período específico, incluindo dados básicos do aluno e do período.

**Permissões:**

- `admin` pode consultar qualquer período;
- `education_institute` pode consultar apenas períodos visíveis para sua instituição.

**Path Parameters:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `period_id` | int | ID do período |

**Query Parameters:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `page` | int | 1 | Página atual |
| `per_page` | int | 10 | Quantidade de itens por página |

**Resposta `200 OK`:**

```json
{
  "items": [
    {
      "id": 1,
      "period_id": 12,
      "student_id": 42,
      "schedule_id": 33,
      "room_id": 7,
      "start_date": "2026-05-20",
      "end_date": null,
      "created_at": "2026-05-20T10:30:00",
      "updated_at": "2026-05-20T10:30:00",
      "student": {
        "id": 42,
        "name": "Maria Silva",
        "cpf": "123.456.789-00"
      },
      "period": {
        "id": 12,
        "name": "2026.1",
        "start_date": "2026-02-01",
        "end_date": "2026-06-30"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 1,
    "total_pages": 1
  },
  "filters": null
}
```

---

## Regras de negócio do histórico

- Ao vincular um aluno ao período, o backend cria um registro em `history` com `end_date = null`.
- Ao desvincular o aluno do período, o backend preenche `end_date` no histórico ativo correspondente.
- O endpoint de histórico não altera dados, apenas consulta os registros já gravados.

---

## Campos úteis para a tela

O frontend pode usar os seguintes dados para montar a lista ou timeline do histórico:

- `student.name` para exibir o nome do aluno;
- `student.cpf` para identificação rápida;
- `room_id` para identificar a sala usada no vínculo;
- `schedule_id` para identificar o horário específico do vínculo;
- `period.name` para contextualizar o período;
- `start_date` e `end_date` para o intervalo do estágio;
- `end_date = null` para indicar vínculo ainda ativo.

---

## Exemplo de consumo

```javascript
const response = await fetch(`/api/v1/histories/by-period/${periodId}?page=1&per_page=10`, {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});

const data = await response.json();
```

---

## Observação para o frontend

Se a tela precisar de filtros adicionais, os candidatos naturais são:

- `student_id`;
- intervalo de datas (`start_date` / `end_date`);
- status ativo/inativo do vínculo.

Esses filtros ainda não foram expostos na API, mas podem ser adicionados depois se a UI precisar refinar a listagem.

---

## Histórico por Schedule

### Listar histórico de um schedule

```
GET /api/v1/histories/by-schedule/{schedule_id}
```

**Descrição:**

Retorna a lista paginada de vínculos históricos de um schedule específico.

**Permissões:**

- `admin` pode consultar qualquer schedule;
- `service` pode consultar apenas schedules das salas do próprio serviço.

**Path Parameters:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `schedule_id` | int | ID do schedule |

**Query Parameters:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `page` | int | 1 | Página atual |
| `per_page` | int | 10 | Quantidade de itens por página |

**Resposta `200 OK`:**

```json
{
  "items": [
    {
      "id": 1,
      "period_id": 12,
      "student_id": 42,
      "schedule_id": 33,
      "room_id": 7,
      "start_date": "2026-05-20",
      "end_date": null,
      "created_at": "2026-05-20T10:30:00",
      "updated_at": "2026-05-20T10:30:00",
      "student": {
        "id": 42,
        "name": "Maria Silva",
        "cpf": "123.456.789-00"
      },
      "period": {
        "id": 12,
        "name": "2026.1",
        "start_date": "2026-02-01",
        "end_date": "2026-06-30"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 1,
    "total_pages": 1
  },
  "filters": null
}
```

**Observação:**

Esse endpoint filtra pelo `schedule_id` salvo no histórico. Para vínculos antigos sem schedule associado, o item não aparece na listagem por schedule.

## Histórico por Sala

### Listar histórico de uma sala

```
GET /api/v1/histories/by-room/{room_id}
```

**Descrição:**

Retorna a lista paginada de vínculos históricos de uma sala específica.

**Permissões:**

- `admin` pode consultar qualquer sala;
- `service` pode consultar apenas as salas do próprio serviço.

**Path Parameters:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `room_id` | int | ID da sala |

**Query Parameters:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `page` | int | 1 | Página atual |
| `per_page` | int | 10 | Quantidade de itens por página |

**Resposta `200 OK`:**

```json
{
  "items": [
    {
      "id": 1,
      "period_id": 12,
      "student_id": 42,
      "room_id": 7,
      "start_date": "2026-05-20",
      "end_date": null,
      "created_at": "2026-05-20T10:30:00",
      "updated_at": "2026-05-20T10:30:00",
      "student": {
        "id": 42,
        "name": "Maria Silva",
        "cpf": "123.456.789-00"
      },
      "period": {
        "id": 12,
        "name": "2026.1",
        "start_date": "2026-02-01",
        "end_date": "2026-06-30"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 1,
    "total_pages": 1
  },
  "filters": null
}
```

**Observação:**

Esse endpoint filtra pelo `room_id` salvo no histórico. Para vínculos antigos sem sala associada, o item não aparece na listagem por sala.

---

## Histórico por Schedule

### Listar histórico de um schedule

```
GET /api/v1/histories/by-schedule/{schedule_id}
```

**Descrição:**

Retorna a lista paginada de vínculos históricos de um schedule específico.

**Permissões:**

- `admin` pode consultar qualquer schedule;
- `service` pode consultar apenas schedules das salas do próprio serviço.

**Path Parameters:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `schedule_id` | int | ID do schedule |

**Query Parameters:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `page` | int | 1 | Página atual |
| `per_page` | int | 10 | Quantidade de itens por página |

**Resposta `200 OK`:**

```json
{
  "items": [
    {
      "id": 1,
      "period_id": 12,
      "student_id": 42,
      "schedule_id": 33,
      "room_id": 7,
      "start_date": "2026-05-20",
      "end_date": null,
      "created_at": "2026-05-20T10:30:00",
      "updated_at": "2026-05-20T10:30:00",
      "student": {
        "id": 42,
        "name": "Maria Silva",
        "cpf": "123.456.789-00"
      },
      "period": {
        "id": 12,
        "name": "2026.1",
        "start_date": "2026-02-01",
        "end_date": "2026-06-30"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 1,
    "total_pages": 1
  },
  "filters": null
}
```

**Observação:**

Esse endpoint filtra pelo `schedule_id` salvo no histórico. Para vínculos antigos sem schedule associado, o item não aparece na listagem por schedule.

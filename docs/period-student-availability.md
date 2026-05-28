# Gestão de períodos e horários disponíveis

Este documento descreve as rotas usadas para:

- listar alunos disponíveis para vinculação a um período;
- listar slots disponíveis para um aluno;
- vincular um aluno a um horário específico;
- remover um aluno de um horário.

## 1) Alunos de um período

### Rota

```http
GET /api/v1/periods/{period_id}?include=students
```

### Comportamento

Quando `include=students` é informado, a API retorna **todos os alunos ativos** da instituição, com indicador de vínculo de horário.

A resposta inclui:

- `students`: lista de alunos da instituição;
- `student_ids`: lista de IDs dos alunos;
- para cada aluno:
  - `has_slot`: boolean indicando se o aluno tem um horário vinculado;
  - `slot`: objeto com detalhes do horário vinculado (ou null se não tem).

### Exemplo

```http
GET /api/v1/periods/1?include=students
```

### Exemplo de resposta

```json
{
  "id": 1,
  "name": "2026.1",
  "students": [
    {
      "id": 1,
      "name": "Alexsander",
      "cpf": "00000000000",
      "semester": 1,
      "has_slot": true,
      "slot": {
        "room_id": 12,
        "room_name": "Sala A",
        "day_of_week": "MONDAY",
        "period": "AFTERNOON"
      },
      "course": {
        "id": 1,
        "name": "Teste"
      },
      "institution": {
        "id": 1,
        "name": "Instituição X"
      }
    },
    {
      "id": 2,
      "name": "Maria Silva",
      "cpf": "11111111111",
      "semester": 3,
      "has_slot": false,
      "slot": null,
      "course": {
        "id": 1,
        "name": "Teste"
      },
      "institution": {
        "id": 1,
        "name": "Instituição X"
      }
    }
  ],
  "student_ids": [1, 2]
}
```

## 2) Slots disponíveis para um aluno

### Rota

```http
GET /api/v1/rooms/available-slots?student_id={student_id}
```

### Query params opcionais

- `room_id`: filtra por uma sala específica.

### Comportamento

A rota retorna apenas os slots que:

- tenham `occupied < capacity`;
- não tenham conflito com outro horário já vinculado ao aluno;
- respeitem a regra de maca, quando o curso exigir.

### Exemplo de resposta

```json
[
  {
    "room_id": 1,
    "day_of_week": "FRIDAY",
    "period": "EVENING",
    "capacity": 2,
    "occupied": 0
  }
]
```

## 3) Vincular aluno a um horário específico

### Rota

```http
POST /api/v1/rooms/{room_id}/schedule/{day_of_week}/{period}/student
```

### Body

```json
{
  "student_id": 1
}
```

### Exemplo

```http
POST /api/v1/rooms/1/schedule/MONDAY/MORNING/student
```

### Possíveis respostas

- `200 OK`: aluno vinculado com sucesso;
- `409 Conflict`: aluno já possui horário em outra sala;
- `404 Not Found`: sala, período ou aluno não encontrado;
- `422 Unprocessable Entity`: erro de validação dos parâmetros.

## 4) Remover aluno de um horário

### Rota

```http
DELETE /api/v1/rooms/{room_id}/schedule/{day_of_week}/{period}/student
```

### Body

```json
{
  "student_id": 1
}
```

## Fluxo sugerido no frontend

### Para visualizar a tela de gestão

1. Carregar todos os alunos da instituição:
   - `GET /api/v1/periods/{period_id}?include=students`
2. Filtrar localmente:
   - Alunos COM horário: `has_slot === true`
   - Alunos SEM horário: `has_slot === false`

### Para atribuir um horário a um aluno

1. Carregar os slots disponíveis para o aluno:
   - `GET /api/v1/rooms/available-slots?student_id={student_id}`
2. O usuário seleciona um slot.
3. Vincular o aluno ao horário:
   - `POST /api/v1/rooms/{room_id}/schedule/{day_of_week}/{period}/student`

## Observações

- A lista de alunos retorna **todos os alunos ativos** da instituição, com indicador de vínculo (`has_slot`).
- O frontend pode filtrar pela propriedade `has_slot`:
  - `has_slot: true` → aluno já tem horário vinculado;
  - `has_slot: false` → aluno sem horário vinculado.
- Quando `has_slot: true`, o campo `slot` contém os detalhes do horário vinculado.
- A lista de slots disponíveis mostra apenas períodos com vagas.
- Se o curso do aluno exigir maca, a sala precisa ter maca disponível.
- A API pode retornar `409` se o aluno já estiver em outro horário no mesmo dia/período.

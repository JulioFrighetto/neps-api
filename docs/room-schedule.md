# Agenda de Sala — API

Este documento descreve os endpoints relacionados às agendas de sala (schedules).

**Visão geral**

- Ao criar uma `Room` a aplicação gera automaticamente uma `Schedule` vinculada à sala.
- A agenda tem 7 dias (MONDAY..SUNDAY) e 3 períodos por dia (MORNING, AFTERNOON, EVENING).
- Cada período pode conter múltiplos alunos, respeitando a capacidade (`room_capacity`) da sala.

**Enums aceitos**

- `dayOfWeek`: `MONDAY`, `TUESDAY`, `WEDNESDAY`, `THURSDAY`, `FRIDAY`, `SATURDAY`, `SUNDAY`
- `period`: `MORNING`, `AFTERNOON`, `EVENING`

---

## Mudança de contrato

As rotas deste módulo não recebem mais dados na URL/query string.

O frontend deve enviar os dados no body da requisição.

Rotas novas:

- `POST /api/v1/rooms/schedule`
- `POST /api/v1/rooms/schedule/student`
- `DELETE /api/v1/rooms/schedule/student`
- `POST /api/v1/rooms/available-slots`

---

**POST /api/v1/rooms/schedule**

Descrição: Retorna a agenda (estrutura aninhada) da sala.

Corpo (JSON):

```json
{
  "room_id": 12
}
```

Resposta (200):

```json
{
  "roomId": 12,
  "days": [
    {
      "dayOfWeek": "MONDAY",
      "periods": [
        { "period": "MORNING", "studentIds": [1, 2] },
        { "period": "AFTERNOON", "studentIds": [] },
        { "period": "EVENING", "studentIds": [] }
      ]
    },
    {
      "dayOfWeek": "TUESDAY",
      "periods": [
        { "period": "MORNING", "studentIds": [] },
        { "period": "AFTERNOON", "studentIds": [] },
        { "period": "EVENING", "studentIds": [] }
      ]
    }
    // ... demais dias
  ]
}
```

Erros comuns:

- `404 Sala não encontrada` — sala com `room_id` inexistente.
- `404 Agenda não encontrada` — se por algum motivo a agenda vinculada não existir.

---

**POST /api/v1/rooms/available-slots**

Descrição: Lista horários com vaga para um aluno (em uma sala específica ou em todas).

Corpo (JSON):

```json
{
  "student_id": 42,
  "room_id": 12
}
```

`room_id` é opcional.

Resposta (200):

```json
[
  {
    "room_id": 12,
    "day_of_week": "MONDAY",
    "period": "MORNING",
    "capacity": 10,
    "occupied": 4
  }
]
```

---

**POST /api/v1/rooms/schedule/student**

Descrição: Adiciona um aluno ao período especificado da sala.

Corpo (JSON):

```json
{
  "room_id": 12,
  "day_of_week": "MONDAY",
  "period": "MORNING",
  "period_id": 12,
  "student_id": 42
}
```

Resposta (200): o período atualizado:

```json
{
  "roomId": 12,
  "dayOfWeek": "MONDAY",
  "period": "MORNING",
  "studentIds": [1, 2, 42]
}
```

Erros e códigos de resposta:

- `404 Sala não encontrada` — sala inválida.
- `404 Período não encontrado` — se o `period_id` não existir.
- `404 Período ou aluno não encontrado` — se a combinação `room/day/period` ou o `student_id` não existirem.
- `409 Conflito` — usado quando a operação falha por regra de negócio, por exemplo:
  - alocar aluno já presente no mesmo período (dependendo da regra atual pode ser ignorado ou causar conflito);
  - exceder a capacidade da sala (`room.room_capacity`). Nesse caso a mensagem possui a razão.

---

**DELETE /api/v1/rooms/schedule/student**

Descrição: Remove um aluno do período informado e encerra o histórico ativo correspondente.

Corpo (JSON):

```json
{
  "room_id": 12,
  "day_of_week": "MONDAY",
  "period": "MORNING",
  "period_id": 12,
  "student_id": 42
}
```

Erros e códigos de resposta:

- `404 Sala não encontrada` — sala inválida.
- `404 Período não encontrado` — se o `period_id` não existir.
- `404 Aluno não encontrado neste horário` — se o aluno não estiver associado ao horário informado.

---

Comportamento importante:

- A agenda é criada automaticamente ao criar a sala: 7 dias × 3 períodos.
- Cada `SchedulePeriod` mantém uma lista de alunos (many-to-many). A aplicação valida a capacidade da sala ao adicionar novos alunos.
- O vínculo e o desvínculo atualizam o `history` do período informado, usando o `period_id` enviado no body.

---

Exemplos rápidos (curl)

Obter agenda:

```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <token>" \
  -d '{"room_id": 12}' \
  "https://<host>/api/v1/rooms/schedule"
```

Adicionar aluno ao período:

```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <token>" \
  -d '{"room_id": 12, "day_of_week": "MONDAY", "period": "MORNING", "period_id": 12, "student_id": 42}' \
  "https://<host>/api/v1/rooms/schedule/student"
```

Buscar horários disponíveis:

```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <token>" \
  -d '{"student_id": 42, "room_id": 12}' \
  "https://<host>/api/v1/rooms/available-slots"
```

---

Se quiser, eu adiciono testes básicos que validam:

- a criação automática da `Schedule` ao criar uma `Room`;
- que `POST /rooms/schedule` retorna 7 dias × 3 períodos;
- que `POST` respeita `room_capacity` e evita duplicatas.

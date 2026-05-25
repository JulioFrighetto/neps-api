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

**GET /api/v1/rooms/{room_id}/schedule**

Descrição: Retorna a agenda (estrutura aninhada) da sala.

Parâmetros:

- `room_id` (path): id da sala

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

**POST /api/v1/rooms/{room_id}/schedule/{day_of_week}/{period}/student**

Descrição: Adiciona um aluno ao período especificado da sala.

Parâmetros:

- `room_id` (path): id da sala
- `day_of_week` (path): um dos valores do enum `dayOfWeek`
- `period` (path): um dos valores do enum `period`

Corpo (JSON):

```json
{
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
- `404 Período ou aluno não encontrado` — se a combinação `room/day/period` ou o `student_id` não existirem.
- `409 Conflito` — usado quando a operação falha por regra de negócio, por exemplo:
  - alocar aluno já presente no mesmo período (dependendo da regra atual pode ser ignorado ou causar conflito);
  - exceder a capacidade da sala (`room.room_capacity`). Nesse caso a mensagem possui a razão.

---

Comportamento importante:

- A agenda é criada automaticamente ao criar a sala: 7 dias × 3 períodos.
- Cada `SchedulePeriod` mantém uma lista de alunos (many-to-many). A aplicação valida a capacidade da sala ao adicionar novos alunos.
- Não há endpoint de remoção nesta documentação; se precisar de um `DELETE` para remover aluno de um período, posso adicionar.

---

Exemplos rápidos (curl)

Obter agenda:

```bash
curl -s -H "Authorization: Bearer <token>" \
  "https://<host>/api/v1/rooms/12/schedule"
```

Adicionar aluno ao período:

```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <token>" \
  -d '{"student_id": 42}' \
  "https://<host>/api/v1/rooms/12/schedule/MONDAY/MORNING/student"
```

---

Se quiser, eu adiciono testes básicos que validam:

- a criação automática da `Schedule` ao criar uma `Room`;
- que `GET /rooms/{id}/schedule` retorna 7 dias × 3 períodos;
- que `POST` respeita `room_capacity` e evita duplicatas.

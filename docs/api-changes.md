# Alterações na API - Agenda de Sala

## Resumo das Alterações
Todas as rotas do módulo de agenda de sala agora recebem parâmetros exclusivamente no corpo da requisição (JSON) em vez de parâmetros na URL/query string.

## Renomeação de domínio

O termo "Unidade de Saúde" foi substituído por "Campo de Estágio" nas mensagens e rotas relacionadas ao domínio `internships`.

Além disso, o vínculo entre campo de estágio e usuário passou a ser de muitos para um:

- um campo de estágio pode ter vários usuários vinculados;
- cada usuário continua pertencendo a apenas um campo de estágio por vez.

## Rotas Atualizadas

### `POST /api/v1/rooms/schedule`
**Descrição:** Retorna a agenda completa de uma sala
**Antes:**
```bash
# Parâmetros na URL
(curl -X POST... -d '{"room_id": 12}')
```
**Depois:**
```bash
# Parâmetros no corpo da requisição (sem alteração neste caso)
(curl -X POST... -d '{"room_id": 12}')
```

### `POST /api/v1/rooms/schedule/student`
**Descrição:** Adiciona um aluno a um período específico
**Antes (exemplo antigo):**
```bash
# Usando query params (não aplicável aqui, mas outros endpoints podem ter mudado)
```
**Depois:**
```bash
# Todos os parâmetros agora no corpo
{
  "room_id": 12,
  "day_of_week": "MONDAY",
  "period": "MORNING",
  "period_id": 12,
  "student_id": 42
}
```

### `DELETE /api/v1/rooms/schedule/student`
**Descrição:** Remove um aluno de um período
**Antes:**
```bash
# Exemplo de parâmetros na URL (se aplicável)
```
**Depois:**
```bash
# Parâmetros no corpo
{
  "room_id": 12,
  "day_of_week": "MONDAY",
  "period": "MORNING",
  "period_id": 12,
  "student_id": 42
}
```

### `POST /api/v1/rooms/available-slots`
**Descrição:** Lista horários disponíveis para um aluno
**Antes:**
```bash
# Parâmetros na URL
```
**Depois:**
```bash
# Parâmetros no corpo
{
  "student_id": 42,
  "room_id": 12
}
```

## Impacto nas Implementações
- **Frontend:** Todos os chamados de API devem enviar dados no corpo da requisição com Content-Type: application/json
- **Backend:** Validação de parâmetros deve ser feita no corpo da requisição
- **Testes:** Atualizar testes para usar o novo formato de requisição

## Exemplos de Requisição Atualizadas

### Obter Agenda da Sala
```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <token>" \
  -d '{"room_id": 12}' \
  "https://<host>/api/v1/rooms/schedule"
```

### Adicionar Aluno ao Período
```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <token>" \
  -d '{"room_id": 12, "day_of_week": "MONDAY", "period": "MORNING", "period_id": 12, "student_id": 42}' \
  "https://<host>/api/v1/rooms/schedule/student"
```

### Buscar Horários Disponíveis
```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <token>" \
  -d '{"student_id": 42, "room_id": 12}' \
  "https://<host>/api/v1/rooms/available-slots"
```
# Alteracoes de contrato da API (URL -> Body)

Data: 2026-05-31

Este documento consolida todas as mudancas aplicadas para remover parametros da URL/path e receber os dados no corpo da requisicao.

Regra aplicada:
- Endpoints que antes recebiam `/{id}` ou segmentos similares foram migrados para endpoints sem path params.
- IDs e filtros obrigatorios passaram para JSON body.
- Listagens com query string (filtros/paginacao) permaneceram como query quando nao havia path param no endpoint original.

## Room Schedule

1. Agenda da sala
- Antes: `GET /api/v1/rooms/{room_id}/schedule`
- Agora: `POST /api/v1/rooms/schedule`
- Body: `room_id`

2. Horarios disponiveis
- Antes: `GET /api/v1/rooms/available-slots?student_id=...&room_id=...`
- Agora: `POST /api/v1/rooms/available-slots`
- Body: `student_id`, `room_id` (opcional)

3. Vincular aluno
- Antes: `POST /api/v1/rooms/schedule/student` (ja no body)
- Agora: `POST /api/v1/rooms/schedule/student` (mantido)
- Body: `room_id`, `day_of_week`, `period`, `period_id`, `student_id`

4. Desvincular aluno
- Antes: `DELETE /api/v1/rooms/schedule/student` (ja no body)
- Agora: `DELETE /api/v1/rooms/schedule/student` (mantido)
- Body: `room_id`, `day_of_week`, `period`, `period_id`, `student_id`

## Discipline

1. Detalhe do curso
- Antes: `GET /api/v1/disciplines/{discipline_id}`
- Agora: `POST /api/v1/disciplines/detail`
- Body: `discipline_id`

2. Atualizacao de curso
- Antes: `PUT /api/v1/disciplines/{discipline_id}` e `PATCH /api/v1/disciplines/{discipline_id}`
- Agora: `PUT /api/v1/disciplines/` e `PATCH /api/v1/disciplines/`
- Body: `discipline_id` + campos de `DisciplineUpdate`

## Education Institute

1. Detalhe da instituicao
- Antes: `GET /api/v1/education-institutes/{institute_id}`
- Agora: `POST /api/v1/education-institutes/detail`
- Body: `institute_id`

2. Atualizacao da instituicao
- Antes: `PATCH /api/v1/education-institutes/{institute_id}` e `PUT /api/v1/education-institutes/{institute_id}`
- Agora: `PATCH /api/v1/education-institutes/` e `PUT /api/v1/education-institutes/`
- Body: `institute_id` + campos de `EducationInstituteUpdate`

## Gestao

1. Detalhe do aluno (gestao)
- Antes: `GET /api/v1/students/{student_id}`
- Agora: `POST /api/v1/students/detail`
- Body: `student_id`, `include` (opcional)

2. Atualizacao do aluno (gestao)
- Antes: `PUT /api/v1/students/{student_id}` e `PATCH /api/v1/students/{student_id}`
- Agora: `PUT /api/v1/students` e `PATCH /api/v1/students`
- Body: `student_id` + campos de atualizacao

## Period

1. Detalhe do periodo
- Antes: `GET /api/v1/periods/{period_id}`
- Agora: `POST /api/v1/periods/detail`
- Body: `period_id`, `include` (opcional)

2. Vincular aluno ao periodo
- Antes: `POST /api/v1/periods/{period_id}/students`
- Agora: `POST /api/v1/periods/students`
- Body: `period_id`, `student_id`

3. Desvincular aluno do periodo
- Antes: `DELETE /api/v1/periods/{period_id}/students`
- Agora: `DELETE /api/v1/periods/students`
- Body: `period_id`, `student_id`

4. Atualizar periodo
- Antes: `PATCH /api/v1/periods/{period_id}`
- Agora: `PATCH /api/v1/periods/`
- Body: `period_id` + campos de `PeriodUpdate`

## Student

1. Detalhe do aluno
- Antes: `GET /api/v1/students/{student_id}`
- Agora: `POST /api/v1/students/detail`
- Body: `student_id`, `include` (opcional)

2. Listagem por curso
- Antes: `GET /api/v1/students/by-discipline/{discipline_id}`
- Agora: `POST /api/v1/students/by-discipline`
- Body: `discipline_id`, `page`, `per_page`

3. Listagem por instituicao
- Antes: `GET /api/v1/students/by-institute/{institute_id}`
- Agora: `POST /api/v1/students/by-institute`
- Body: `institute_id`, `page`, `per_page`

4. Atualizacao do aluno
- Antes: `PATCH /api/v1/students/{student_id}`
- Agora: `PATCH /api/v1/students/`
- Body: `student_id` + campos de `StudentUpdate`

## Region

1. Detalhe da regiao
- Antes: `GET /api/v1/regions/{region_id}`
- Agora: `POST /api/v1/regions/detail`
- Body: `region_id`

2. Atualizacao da regiao
- Antes: `PATCH /api/v1/regions/{region_id}`
- Agora: `PATCH /api/v1/regions`
- Body: `region_id` + campos de `RegionUpdate`

## Room

1. Detalhe da sala
- Antes: `GET /api/v1/rooms/{room_id}`
- Agora: `POST /api/v1/rooms/detail`
- Body: `room_id`

2. Salas por servico
- Antes: `GET /api/v1/rooms/by-internships/{internship_id}`
- Agora: `POST /api/v1/rooms/by-internships`
- Body: `internship_id`, `page`, `per_page`

3. Atualizacao da sala
- Antes: `PATCH /api/v1/rooms/{room_id}`
- Agora: `PATCH /api/v1/rooms/`
- Body: `room_id` + campos de `RoomUpdate`

## Internships

1. Detalhe do servico
- Antes: `GET /api/v1/internshipss/{internship_id}`
- Agora: `POST /api/v1/internshipss/detail`
- Body: `internship_id`

2. Atualizacao do servico
- Antes: `PATCH /api/v1/internshipss/{internship_id}`
- Agora: `PATCH /api/v1/internshipss/`
- Body: `internship_id` + campos de `InternshipsUpdate`

3. Substituicao do servico
- Antes: `PUT /api/v1/internshipss/{internship_id}`
- Agora: `PUT /api/v1/internshipss/`
- Body: `internship_id` + campos de `InternshipsCreate`

## Internships Room

1. Detalhe da sala de servico
- Antes: `GET /api/v1/internships-rooms/{internships_room_id}`
- Agora: `POST /api/v1/internships-rooms/detail`
- Body: `internships_room_id`

2. Salas por servico
- Antes: `GET /api/v1/internships-rooms/by-internships/{internship_id}`
- Agora: `POST /api/v1/internships-rooms/by-internships`
- Body: `internship_id`, `page`, `per_page`

3. Atualizacao da sala de servico
- Antes: `PATCH /api/v1/internships-rooms/{internships_room_id}`
- Agora: `PATCH /api/v1/internships-rooms/`
- Body: `internships_room_id` + campos de `InternshipsRoomUpdate`

## Internships Schedule

1. Detalhe da agenda
- Antes: `GET /api/v1/internships-schedules/{internships_schedule_id}`
- Agora: `POST /api/v1/internships-schedules/detail`
- Body: `internships_schedule_id`

2. Agendas por sala
- Antes: `GET /api/v1/internships-schedules/by-room/{internships_room_id}`
- Agora: `POST /api/v1/internships-schedules/by-room`
- Body: `internships_room_id`

3. Agendas por sala e dia
- Antes: `GET /api/v1/internships-schedules/by-room/{internships_room_id}/by-day/{week_day}`
- Agora: `POST /api/v1/internships-schedules/by-room/by-day`
- Body: `internships_room_id`, `week_day`

4. Atualizacao da agenda
- Antes: `PATCH /api/v1/internships-schedules/{internships_schedule_id}`
- Agora: `PATCH /api/v1/internships-schedules/`
- Body: `internships_schedule_id` + campos de `InternshipsScheduleUpdate`

## History

1. Historicos por periodo
- Antes: `GET /api/v1/histories/by-period/{period_id}`
- Agora: `POST /api/v1/histories/by-period`
- Body: `id` (period_id), `page`, `per_page`

2. Historicos por sala
- Antes: `GET /api/v1/histories/by-room/{room_id}`
- Agora: `POST /api/v1/histories/by-room`
- Body: `id` (room_id), `page`, `per_page`

3. Historicos por schedule
- Antes: `GET /api/v1/histories/by-schedule/{schedule_id}`
- Agora: `POST /api/v1/histories/by-schedule`
- Body: `id` (schedule_id), `page`, `per_page`

4. Historicos por aluno
- Antes: `GET /api/v1/histories/by-student/{student_id}`
- Agora: `POST /api/v1/histories/by-student`
- Body: `id` (student_id), `page`, `per_page`

## User

1. Detalhe do usuario
- Antes: `GET /api/v1/users/{user_id}`
- Agora: `POST /api/v1/users/detail`
- Body: `user_id`

2. Atualizacao do usuario
- Antes: `PATCH /api/v1/users/{user_id}`
- Agora: `PATCH /api/v1/users/`
- Body: `user_id` + campos de `UserUpdate`

3. Substituicao do usuario
- Antes: `PUT /api/v1/users/{user_id}`
- Agora: `PUT /api/v1/users/`
- Body: `user_id` + campos de `UserCreate`

4. Troca de senha
- Antes: `POST /api/v1/users/{user_id}/change-password`
- Agora: `POST /api/v1/users/change-password`
- Body: `user_id`, `current_password`, `new_password`

## Observacoes para frontend

1. Remover interpolacao de IDs no path para os endpoints acima.
2. Enviar sempre `Content-Type: application/json` nas rotas migradas.
3. Atualizar clients gerados (OpenAPI/codegen) para refletir novos metodos e payloads.
4. Revisar regras de cache HTTP para endpoints que mudaram de `GET` para `POST`.

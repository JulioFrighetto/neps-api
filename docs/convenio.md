# Convênio — Guia de integração para o frontend

API para gerenciar convênios (parceiros em fase de negociação/formalização), que
ao serem **firmados** geram automaticamente uma Instituição de Ensino vinculada.

Base URL: `/api/v1/convenios`

Todas as rotas exigem autenticação (`Authorization: Bearer <access_token>`).

---

## Status do convênio

| Valor          | Significado                                  |
| -------------- | --------------------------------------------- |
| `EM_ANALISE`   | Em análise (padrão ao criar)                  |
| `NAO_FIRMADO`  | Não firmado                                   |
| `FIRMADO`      | Firmado — dispara a criação da instituição    |

Enviar qualquer outro valor no campo `status` retorna `422 Unprocessable Entity`.

**Regra de negócio importante:** quando o `status` é definido (ou alterado) para
`FIRMADO` e o convênio ainda não tem uma instituição vinculada
(`education_institute_id` nulo), o backend cria automaticamente uma Instituição
de Ensino com os mesmos dados do convênio (`name`, `cnpj`, `address`, `phone`,
`email`, `priority`, `is_active`) e preenche `education_institute_id` na
resposta. Se o convênio já estiver firmado (já tem instituição vinculada), reenviar
`status: "FIRMADO"` é seguro — não cria duplicata.

Opcionalmente, ao firmar você pode enviar `user_name` / `user_email` para criar
também o usuário de acesso da instituição (dispara e-mail de boas-vindas com
link de definição de senha).

---

## Modelo de dados (`ConvenioResponse`)

```jsonc
{
  "id": 1,
  "name": "Hospital Exemplo",
  "description": "Convênio para estágio em enfermagem",
  "is_active": true,
  "cnpj": "12.345.678/0001-99",
  "address": "Rua Exemplo, 123",
  "phone": "(51) 99999-9999",
  "email": "contato@hospitalexemplo.com",
  "priority": 0,              // 0 = prioritário, 1 = não prioritário
  "status": "EM_ANALISE",     // EM_ANALISE | NAO_FIRMADO | FIRMADO
  "education_institute_id": null, // preenchido automaticamente ao firmar
  "created_at": "2026-07-14T22:27:59",
  "updated_at": "2026-07-14T22:27:59"
}
```

---

## Endpoints

### Listar (completo, paginado, com filtros)

`GET /api/v1/convenios/`

Query params (todos opcionais):

| Param                     | Tipo   | Descrição                                  |
| -------------------------- | ------ | ------------------------------------------- |
| `page`                    | int    | Padrão `1`                                  |
| `per_page`                | int    | Padrão `10`, máx `500`                      |
| `name_like`               | string | Busca parcial (case-insensitive) por nome   |
| `cnpj`                    | string | Igualdade exata                             |
| `is_active`               | bool   | Filtra ativos/inativos                      |
| `priority`                | int    | `0` ou `1`                                  |
| `status`                  | string | `EM_ANALISE` \| `NAO_FIRMADO` \| `FIRMADO`  |
| `education_institute_id`  | int    | Convênios já vinculados a uma instituição   |

Resposta: `Page<ConvenioResponse>`

```jsonc
{
  "items": [ /* ConvenioResponse[] */ ],
  "pagination": { "page": 1, "per_page": 10, "total": 3, "total_pages": 1 },
  "filters": { "applied": ["status"], "available": ["name_like", "cnpj", "is_active", "priority", "status", "education_institute_id"] }
}
```

Use este endpoint para a **tela de listagem** — já traz `description` e `status`
para exibir na tabela, e o filtro deve ser montado a partir de `filters.available`.

### Listar resumido (para selects/autocomplete)

`GET /api/v1/convenios/list`

Mesmos filtros do endpoint acima (via query string). Retorna itens enxutos:

```jsonc
{ "id": 1, "name": "Hospital Exemplo", "status": "FIRMADO" }
```

### Detalhe

`POST /api/v1/convenios/detail`

Body: `{ "convenio_id": 1 }` → `ConvenioResponse`. `404` se não existir.

### Criar

`POST /api/v1/convenios/`

Body (`ConvenioCreate`):

```jsonc
{
  "name": "Hospital Exemplo",       // obrigatório
  "description": "texto livre",     // opcional
  "is_active": true,                // opcional, padrão true
  "cnpj": "12.345.678/0001-99",     // opcional
  "address": "Rua Exemplo, 123",    // opcional
  "phone": "(51) 99999-9999",       // opcional
  "email": "contato@exemplo.com",   // opcional
  "priority": 0,                    // opcional, 0 ou 1
  "status": "EM_ANALISE",           // opcional, padrão EM_ANALISE
  "user_name": null,                // opcional — só usado se já criar firmado
  "user_email": null,               // opcional — dispara criação de usuário + e-mail
  "region_ids": null                // opcional — regiões da instituição gerada ao firmar
}
```

Retorna `201` com `ConvenioResponse`. Se `status` já vier `"FIRMADO"`, a
instituição é criada na hora e `education_institute_id` já vem preenchido.

### Atualizar (parcial ou total — mesmo contrato)

`PATCH /api/v1/convenios/` ou `PUT /api/v1/convenios/`

Body (`ConvenioUpdate` + `convenio_id`):

```jsonc
{
  "convenio_id": 1,
  "status": "FIRMADO",
  "user_email": "contato@hospitalexemplo.com" // opcional, só se quiser criar acesso
}
```

Retorna `ConvenioResponse` atualizado. `404` se o convênio não existir.

Este é o endpoint que a tela deve chamar quando o usuário mudar o status no
combo/select — basta enviar `convenio_id` + `status` (e demais campos que
tiverem sido editados).

---

## Fluxo sugerido de tela

1. **Listagem**: `GET /convenios/` com filtros de `name_like`, `status`,
   `is_active`, `priority`. Exibir coluna de status com as 3 opções.
2. **Cadastro**: formulário com os mesmos campos de Instituição de Ensino +
   `description` + seletor de `status` (padrão "Em Análise").
3. **Mudança de status para "Firmado"**: chamar `PATCH /convenios/` com
   `status: "FIRMADO"`. Após a resposta, `education_institute_id` estará
   preenchido — pode ser usado para linkar/navegar até a tela da instituição
   criada (`GET /education-institutes/` ou `POST /education-institutes/detail`
   com esse id).
4. **Filtro por relacionamento**: usar `education_institute_id` para listar
   convênios já vinculados a uma instituição específica.

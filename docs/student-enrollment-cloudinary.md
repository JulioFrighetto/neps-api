# Fluxo de Cadastro de Aluno com Upload de Documento PDF

## Visão Geral

Para criar um aluno, é necessário enviar um documento PDF (máximo 5MB) que será armazenado no Cloudinary. O fluxo funciona em dois passos:

1. **Frontend**: Faz upload do PDF direto para Cloudinary
2. **Frontend**: Envia os dados do aluno + URL do PDF para o Backend

## Passo 1: Upload do PDF para Cloudinary (Frontend)

### Credenciais do Cloudinary

- **Cloud Name**: `dpsxz0o9k` (extraído da URL)
- **Upload Preset**: (será fornecido pelo backend em um endpoint)
- **API Key**: `574Ug7upPLPuuP0ZpQueViQeTRA`

### Alternativa A: Upload via Formulário (Recomendado)

```javascript
async function uploadPdfToCloudinary(file) {
  // Validações
  if (!file) throw new Error("Nenhum arquivo selecionado");
  if (file.type !== "application/pdf")
    throw new Error("Apenas PDFs são aceitos");
  if (file.size > 5 * 1024 * 1024) throw new Error("Arquivo maior que 5MB");

  const formData = new FormData();
  formData.append("file", file);
  formData.append("upload_preset", "seu_upload_preset"); // Será fornecido
  formData.append("resource_type", "auto");

  const response = await fetch(
    "https://api.cloudinary.com/v1_1/dpsxz0o9k/image/upload",
    {
      method: "POST",
      body: formData,
    },
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error?.message || "Erro ao fazer upload");
  }

  return data.secure_url; // URL do arquivo
}
```

### Alternativa B: Upload via Signed Request (Mais Seguro)

```javascript
async function uploadPdfWithSignature(file) {
  // 1. Solicitar assinatura ao backend
  const signatureResponse = await fetch(
    "http://localhost:8000/api/v1/cloudinary/signature",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ timestamp: Math.floor(Date.now() / 1000) }),
    },
  );

  const { signature, timestamp, upload_preset } =
    await signatureResponse.json();

  // 2. Fazer upload com a assinatura
  const formData = new FormData();
  formData.append("file", file);
  formData.append("upload_preset", upload_preset);
  formData.append("timestamp", timestamp);
  formData.append("signature", signature);
  formData.append("api_key", "574Ug7upPLPuuP0ZpQueViQeTRA");

  const response = await fetch(
    "https://api.cloudinary.com/v1_1/dpsxz0o9k/image/upload",
    {
      method: "POST",
      body: formData,
    },
  );

  const data = await response.json();
  if (!response.ok) throw new Error("Erro ao fazer upload");

  return data.secure_url;
}
```

## Passo 2: Criar Aluno com URL do PDF (Frontend)

Após obter a URL do PDF do Cloudinary, envie para o backend:

### Request

```http
POST http://localhost:8000/api/v1/students/
Content-Type: application/json

{
  "name": "ALEXSANDER BATISTA DONAY",
  "cpf": "003.534.560-80",
  "email": "alexdonay@gmail.com",
  "phone": "54999932318",
  "discipline_id": 1,
  "semester": 1,
  "institution_id": 3,
  "document_url": "https://res.cloudinary.com/dpsxz0o9k/image/upload/v1234567890/student_docs/abc123.pdf"
}
```

### Response (201 Created)

```json
{
  "id": 1,
  "name": "ALEXSANDER BATISTA DONAY",
  "cpf": "003.534.560-80",
  "email": "alexdonay@gmail.com",
  "phone": "54999932318",
  "discipline_id": 1,
  "semester": 1,
  "institution_id": 3,
  "status": "PENDING",
  "is_active": true,
  "document_url": "https://res.cloudinary.com/dpsxz0o9k/image/upload/v1234567890/student_docs/abc123.pdf",
  "created_at": "2026-05-28T10:30:00",
  "updated_at": "2026-05-28T10:30:00"
}
```

## Exemplo Completo (React)

```javascript
import { useState } from "react";
import axios from "axios";

export function EnrollmentForm() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    cpf: "",
    email: "",
    phone: "",
    discipline_id: 1,
    semester: 1,
    institution_id: 3,
  });

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.size > 5 * 1024 * 1024) {
        alert("Arquivo deve ter no máximo 5MB");
        return;
      }
      if (selectedFile.type !== "application/pdf") {
        alert("Apenas arquivos PDF são aceitos");
        return;
      }
      setFile(selectedFile);
    }
  };

  const uploadPdfToCloudinary = async (pdfFile) => {
    const formData = new FormData();
    formData.append("file", pdfFile);
    formData.append("upload_preset", "student_documents"); // Configure isso no Cloudinary
    formData.append("resource_type", "auto");

    try {
      const response = await axios.post(
        "https://api.cloudinary.com/v1_1/dpsxz0o9k/image/upload",
        formData,
      );
      return response.data.secure_url;
    } catch (error) {
      throw new Error(`Erro ao fazer upload do PDF: ${error.message}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      alert("Por favor, selecione um arquivo PDF");
      return;
    }

    setLoading(true);
    try {
      // 1. Upload do PDF para Cloudinary
      const documentUrl = await uploadPdfToCloudinary(file);

      // 2. Criar aluno no backend
      const response = await axios.post(
        "http://localhost:8000/api/v1/students/",
        {
          ...formData,
          document_url: documentUrl,
        },
      );

      console.log("Aluno criado com sucesso:", response.data);
      alert("Aluno cadastrado com sucesso!");

      // Limpar formulário
      setFile(null);
      setFormData({
        name: "",
        cpf: "",
        email: "",
        phone: "",
        discipline_id: 1,
        semester: 1,
        institution_id: 3,
      });
    } catch (error) {
      console.error("Erro:", error);
      alert(`Erro ao cadastrar aluno: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Nome"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        required
      />

      <input
        type="text"
        placeholder="CPF"
        value={formData.cpf}
        onChange={(e) => setFormData({ ...formData, cpf: e.target.value })}
        required
      />

      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        required
      />

      <input
        type="tel"
        placeholder="Telefone"
        value={formData.phone}
        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
        required
      />

      <input
        type="number"
        placeholder="Semestre"
        value={formData.semester}
        onChange={(e) =>
          setFormData({ ...formData, semester: parseInt(e.target.value) })
        }
        required
      />

      <div>
        <label>
          Documento PDF (máximo 5MB) *
          <input
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            required
          />
        </label>
        {file && (
          <p>
            Arquivo: {file.name} ({(file.size / 1024 / 1024).toFixed(2)}MB)
          </p>
        )}
      </div>

      <button type="submit" disabled={loading}>
        {loading ? "Cadastrando..." : "Cadastrar Aluno"}
      </button>
    </form>
  );
}
```

## Configuração do Cloudinary (Backend)

Caso queira uma camada adicional de segurança, crie um endpoint para gerar assinaturas:

```python
# app/core/cloudinary_utils.py
import cloudinary
import hashlib
import json
from time import time

CLOUDINARY_CLOUD_NAME = "dpsxz0o9k"
CLOUDINARY_API_KEY = "574Ug7upPLPuuP0ZpQueViQeTRA"
CLOUDINARY_API_SECRET = "seu_api_secret"  # Configure isso

def generate_cloudinary_signature(timestamp):
    """Gera assinatura para upload seguro ao Cloudinary"""
    signature_data = f"timestamp={timestamp}{CLOUDINARY_API_SECRET}"
    signature = hashlib.sha256(signature_data.encode()).hexdigest()
    return {
        "timestamp": timestamp,
        "signature": signature,
        "upload_preset": "student_documents",
        "cloud_name": CLOUDINARY_CLOUD_NAME,
        "api_key": CLOUDINARY_API_KEY,
    }
```

## Validações no Backend (FastAPI)

Já implementadas em `StudentCreate`:

- ✅ `document_url` é obrigatório (string não-vazia)
- ✅ CPF, email, telefone são opcionais
- ✅ `institution_id` mapeado para `edu_institute_id`
- ✅ Aceita `name`, `phone`, `semester`

## Checklist de Implementação

- [ ] Frontend: Implementar upload de PDF para Cloudinary
- [ ] Frontend: Enviar dados do aluno com `document_url`
- [ ] Backend: Migração do banco para adicionar coluna `document_url`
- [ ] Backend: Validações do documento PDF
- [ ] Testes: Testar fluxo completo

## Comandos Úteis (Backend)

### Criar migração para adicionar coluna

```bash
# Com Alembic (se configurado)
alembic revision --autogenerate -m "Add document_url to students"
alembic upgrade head
```

### Testar endpoint POST

```bash
curl -X POST http://localhost:8000/api/v1/students/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Teste",
    "cpf": "123.456.789-00",
    "email": "teste@example.com",
    "phone": "11999999999",
    "discipline_id": 1,
    "semester": 1,
    "institution_id": 1,
    "document_url": "https://res.cloudinary.com/dpsxz0o9k/image/upload/v1234567890/test.pdf"
  }'
```

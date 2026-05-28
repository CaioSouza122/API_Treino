# API de Treinos com IA e Persistência de Dados

Esta é uma API robusta e pronta para produção construída em Python com **Flask**, integrada ao modelo de inteligência artificial de última geração **Gemini 2.5 Flash** e com banco de dados **SQLite** para persistir os treinos gerados.

A API possui suporte nativo a **CORS (Cross-Origin Resource Sharing)**, permitindo que ela seja consumida diretamente por qualquer outro projeto externo (como sites em React, Vue, Next.js, aplicativos móveis ou outros servidores).

---

## 🚀 Tecnologias Utilizadas

- **Flask**: Web framework leve e flexível para Python.
- **Flask-SQLAlchemy**: Integração e mapeamento objeto-relacional (ORM) para persistência SQL.
- **Flask-CORS**: Habilita o compartilhamento de recursos de origens cruzadas, essencial para integração com frontends externos.
- **Marshmallow**: Validação estrita de dados de entrada e serialização/desserialização de JSON.
- **Google GenAI SDK**: Integração oficial com a inteligência artificial do Gemini.
- **Python-dotenv**: Gerenciamento limpo de configurações e segredos via arquivo `.env`.

---

## 🛠️ Como Configurar e Executar

### 1. Pré-requisitos
Certifique-se de ter o Python 3.8+ instalado em sua máquina.

### 2. Instalar as Dependências
No terminal, execute o comando para instalar todos os pacotes necessários:
```bash
pip install -r requirements.txt
```

### 3. Configurar Segredos e Variáveis
Copie o arquivo `.env.example` para `.env` ou edite diretamente o arquivo `.env` gerado na pasta raiz.
Substitua `SUA_CHAVE_DE_API_AQUI` pela sua chave real do Gemini:
```env
GEMINI_API_KEY=AIzaSy... (sua chave obtida no Google AI Studio)
```

#### 🗄️ Configurando o Banco de Dados (SQLite vs PostgreSQL):
* **Padrão (SQLite):** Por padrão, se você deixar a linha do banco comentada no `.env`, a API criará e usará o arquivo `apipi.db` automaticamente na raiz. Não precisa configurar nada.
* **PostgreSQL:** Para usar o seu banco PostgreSQL, remova o `#` da variável `DATABASE_URL` no `.env` e preencha a string de conexão:
  ```env
  DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
  ```

> **Autenticação opcional:** Se você quiser proteger a API para que apenas seus aplicativos possam chamá-la, defina um token em `API_AUTH_KEY` (exemplo: `API_AUTH_KEY=meu_token_secreto`). Se deixar esse campo vazio, as requisições não exigirão autenticação (perfeito para fase de testes locais).

#### 🛡️ Segurança Adicional:
* **CORS Restrito:** No arquivo `.env`, você pode definir `ALLOWED_ORIGINS=https://meusite.com` para bloquear que outros domínios façam requisições para sua API em produção.
* **Rate Limiting:** A rota `/treino` possui um limite padrão de **5 requisições por minuto por IP** para evitar abusos na sua chave do Gemini. Se excedido, a API retornará o status `429 Too Many Requests` com uma resposta estruturada.



### 4. Iniciar a API
Execute o arquivo principal:
```bash
python App.py
```
A API será iniciada no endereço: `http://localhost:5000`
O banco de dados SQLite `apipi.db` será criado automaticamente no primeiro acesso.

---

## 📡 Endpoints da API (Documentação)

Todos os endpoints estão sob o prefixo `/api/v1`.

### 1. Verificar Status da API
* **Método:** `GET`
* **Rota:** `/api/v1/health`
* **Descrição:** Retorna se o servidor está ativo.
* **Exemplo de Resposta (JSON):**
  ```json
  {
    "status": "operante",
    "mensagem": "API de Treinos com IA rodando com sucesso!"
  }
  ```

### 2. Criar Novo Treino (Gera via Gemini e salva no Banco de Dados)
* **Método:** `POST`
* **Rota:** `/api/v1/treino`
* **Cabeçalhos requeridos (se `API_AUTH_KEY` estiver configurado):** `X-API-KEY: <sua_chave>`
* **Corpo da Requisição (JSON):**
  ```json
  {
    "objetivo": "Ganho de massa muscular nos braços",
    "nivel": "intermediario"
  }
  ```
  *(Nota: O campo `nivel` é opcional e assume `"iniciante"` por padrão. Valores permitidos: `"iniciante"`, `"intermediario"`, `"avancado"`)*
* **Exemplo de Resposta (JSON - HTTP 201):**
  ```json
  {
    "id": 1,
    "objetivo": "Ganho de massa muscular nos braços",
    "nivel": "intermediario",
    "treino_gerado": "### Treino de Braços - Nível Intermediário\n\n1. **Rosca Direta com Barra** - 3 séries de 10 repetições...\n2. **Tríceps Testa** - 3 séries de 12 repetições...\n3. **Rosca Martelo** - 3 séries de 10 repetições...",
    "criado_em": "2026-05-28T18:38:00Z"
  }
  ```

### 3. Listar Todos os Treinos Persistidos
* **Método:** `GET`
* **Rota:** `/api/v1/treinos`
* **Cabeçalhos requeridos (se `API_AUTH_KEY` estiver configurado):** `X-API-KEY: <sua_chave>`
* **Exemplo de Resposta (JSON - HTTP 200):**
  ```json
  [
    {
      "id": 1,
      "objetivo": "Ganho de massa muscular nos braços",
      "nivel": "intermediario",
      "treino_gerado": "...",
      "criado_em": "2026-05-28T18:38:00Z"
    }
  ]
  ```

### 4. Obter um Treino Específico por ID
* **Método:** `GET`
* **Rota:** `/api/v1/treino/<id>`
* **Cabeçalhos requeridos (se `API_AUTH_KEY` estiver configurado):** `X-API-KEY: <sua_chave>`

### 5. Deletar um Treino por ID
* **Método:** `DELETE`
* **Rota:** `/api/v1/treino/<id>`
* **Cabeçalhos requeridos (se `API_AUTH_KEY` estiver configurado):** `X-API-KEY: <sua_chave>`

---

## 🔌 Como Consumir esta API em Outros Projetos (Frontend / Frontend Web)

Como o CORS está configurado para liberar qualquer origem (`*`), você pode consumir a API diretamente via **JavaScript/TypeScript** no seu frontend de outro projeto:

### Exemplo em JavaScript (usando `fetch`):

```javascript
// Exemplo de como gerar um novo treino
async function gerarTreino() {
  const url = 'http://localhost:5000/api/v1/treino';
  const payload = {
    objetivo: 'Definição abdominal e cardio',
    nivel: 'iniciante'
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // 'X-API-KEY': 'sua_chave_se_estiver_habilitada'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Erro na API:', errorData);
      return;
    }

    const treino = await response.json();
    console.log('Treino gerado com sucesso:', treino);
    alert(`Treino ID: ${treino.id}\n\n${treino.treino_gerado}`);
  } catch (error) {
    console.error('Erro de conexão:', error);
  }
}
```

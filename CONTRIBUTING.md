# Guia de Contribuição 🤝

Obrigado por seu interesse em contribuir para a **API de Treinos com IA**!

Para manter a qualidade e profissionalismo do código, pedimos que siga os padrões abaixo ao contribuir.

---

## 📌 Padrão de Branches

Trabalhamos com o fluxo de branches estruturado. Nunca faça commits diretos na branch `main`.

- `main`: Branch de produção, contendo código estável e testado.
- `develop` ou `feature/<nome-da-funcionalidade>`: Branches para desenvolvimento de novas funcionalidades.
- `bugfix/<descricao-do-bug>`: Branches para correção de problemas.
- `refactor/<descricao-da-melhoria>`: Branches para refatoração de código e arquitetura.

---

## 💬 Mensagens de Commit (Conventional Commits)

Utilizamos a convenção **Conventional Commits** em português ou inglês:

- `feat:` Nova funcionalidade adicionada.
- `fix:` Correção de bug.
- `docs:` Alteração em documentações (`README.md`, `CONTRIBUTING.md`).
- `style:` Ajustes na formatação do código (espaçamentos, linter).
- `refactor:` Alteração de código que não adiciona recurso nem corrige bug.
- `test:` Adição ou modificação de testes automatizados.
- `ci:` Alterações nos arquivos de integração contínua (GitHub Actions).

*Exemplo:* `feat: adiciona limitador de taxa na rota de geração de treinos`

---

## 🧪 Testes Automatizados

Antes de submeter um Pull Request, garanta que todos os testes passem:

```bash
make test
# Ou diretamente com Pytest:
pytest tests/
```

Garantimos que a cobertura de testes permaneça alta e que nenhuma mudança quebre os contratos REST existentes.

---

## 📋 Checklist do Pull Request

- [ ] A branch foi criada a partir de `main` ou `develop`.
- [ ] Todos os testes automatizados passaram.
- [ ] O código segue o guia de estilo PEP8 / Flake8.
- [ ] O `README.md` foi atualizado caso novas rotas ou variáveis de ambiente tenham sido criadas.

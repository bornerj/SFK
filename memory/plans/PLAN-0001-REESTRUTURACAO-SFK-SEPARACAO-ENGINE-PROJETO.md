# PLAN-0001 — Reestruturação do SFK: separação Engine ↔ Projeto ↔ Tooling

> **Status:** WAITING_APPROVAL (nada será executado até aprovação explícita)
> **Data:** 2026-07-07
> **Autor:** sessão de arquitetura (Opus 4.8)
> **Tipo:** Estrutural (RULES §5 → exige PLAN aprovado)
> **Repos afetados:** repo do SFK (engine + tooling) e, na Fase 5, projetos que já usam SFK (ex.: JLR_Beauty via updater)

---

## 1. Contexto e Problema

O SFK é simultaneamente **produto** (este repo) e **template** copiado para dentro de outros projetos. A dor central ("os arquivos do framework se misturam com os do projeto") tem causa raiz precisa: **o SFK mistura três categorias de arquivos com ciclos de vida opostos e trata todas como uma coisa só**, jogando todas na raiz do projeto-alvo.

| Cat | O que é | Quem edita | No `update` | Embarca no projeto? |
|-----|---------|------------|-------------|---------------------|
| **A. Engine** | `kernel/*` (RULES, SOUL, BOOTSTRAP, index.toml, agents, skills, workflows, scripts) | Só o SFK | Trocado inteiro | Sim (read-only) |
| **B. Estado do projeto** | `memory/*`, `docs/*`, `project.toml`, `SYSTEM.md` | IA + dev, por projeto | Preservado | Sim (é o cérebro do projeto) |
| **C. Tooling do mantenedor** | `jb_kit_turbo.py`, `sfk_updater.py`, `new-project.*`, `update-project.*` | Só o mantenedor | N/A | Nunca embarca |

### Evidências do projeto real (JLR_Beauty)
- Raiz colide SFK + produto + lixo: `kernel/ memory/ docs/` ao lado de `apps/ cms/ data/ docker/ nginx/ docker-compose.yml` + `arvore.txt` (526 KB), `tmp/` (jpeg 1.1 MB), `null`.
- `project.toml` e `SYSTEM.md` estão dentro de `kernel/` (categoria B misturada em A).
- `EVOLUTION_MEMORY.md` = **9 linhas mortas** vs `MODIFICATION_LOG.md` = **8.073 linhas vivas** → duplicidade confirmada.
- `docs/evolutive_changes/` virou gaveta de lixo (20+ arquivos ad-hoc: seeds SQL, roadmaps, `oldmodification_log.md`).
- Duplicatas reais por drift template↔realidade: `docs/INTEGRATIONS.md` × `docs/config/INTEGRATIONS.md`; `docs/DEPLOY_ENV_REFERENCES.md` × `docs/config/DEPLOY_ENV_REFERENCE.md`; `docs/config/TESTING_GUIDE.md` × `kernel/TESTING_GUIDE.md`.

### Dores adicionais do desenvolvedor (a endereçar no mesmo refactor)
- **D1 — Retomada:** ao voltar após pausa, não se sabe o estado atual nem onde está; gasta-se token pedindo à IA para investigar 8.073 linhas.
- **D2 — Interfaces externas:** WhatsApp/Stripe/PayPal/APIs espalhadas; sem local único e fixo.
- **D3 — Migrações de banco:** SQLs (criação, migração MySQL→PostgreSQL, cópia de dados, seeds) soltos e sem ordem; sem timeline de "o que mudou e quando".
- **D4 — Regras esquecidas:** governança depende do LLM reler 579 linhas e *lembrar*; sem trava real → o dev precisa lembrar a IA de salvar DECISION/MODIFICATION.

### Bugs de referência no template (achados)
- `RULES.md §12.3` aponta `kernel/AUDIT_CHECKLIST.md` — **não existe** (real: `memory/logs/SESSION-AUDIT-CHECKLIST.md`).
- `RULES.md §11` aponta `docs/config/DEPLOY_ENV_REFERENCE.md` — inexistente no template; no JLR virou arquivo duplicado.

---

## 2. Princípio Diretor

> **Engine em `.sfk/` (invisível, trocável). Estado do projeto na raiz (visível, permanente). Tooling do mantenedor em `bin/` (nunca embarca).**

Decisões travadas com o usuário:
- Config do projeto na **raiz**: `sfk.toml` (ex-`project.toml`) + `SYSTEM.md`.
- `.sfk/` = **zona única de engine** (kernel + VERSION + MANIFEST). Nenhum estado de projeto dentro.
- Enforcement da D4 via **git hook que bloqueia** (com `--no-verify` de escape).
- **Um plano faseado** (este).

---

## 3. Desenho-alvo

### Projeto que usa SFK
```
projeto/
├── .sfk/                         # CAT A — engine, read-only, trocado inteiro no update
│   ├── VERSION                   # "0.7.0"
│   ├── MANIFEST                  # arquivos que o SFK é dono (guia do updater)
│   └── kernel/
│       ├── BOOTSTRAP.md RULES.md SOUL.md index.toml OPERATING_CARD.md
│       ├── ARCHITECTURE.md TESTING_GUIDE.md SYSTEM-TEMPLATE.md
│       ├── agents/ skills/ workflows/ scripts/
│       └── hooks/pre-commit      # trava determinística (D4)
├── sfk.toml                      # CAT B — config + [[integrations]] + [db] location
├── SYSTEM.md                     # CAT B — padrões de engenharia do projeto
├── memory/
│   ├── progress.md               # PAINEL DE RETOMADA (D1) — único lido ao voltar
│   ├── MODIFICATION_LOG.md
│   ├── plans/ decisions/
│   └── logs/ (DEBUG-HISTORY, BUILD-HISTORY=ledger de migração, SESSION-AUDIT-CHECKLIST, DRIFT-RULES)
├── docs/
│   ├── project/                  # governado pelo kernel (OVERVIEW, REQUIREMENTS, SCOPE, SETUP)
│   ├── integrations/             # CAT B — uma pasta p/ toda interface externa (D2)
│   └── config/                   # referências técnicas do projeto (sem gaveta de lixo)
├── db/migrations/ db/seeds/      # SQL numerado e sequencial (D3) — local declarado no sfk.toml
├── CLAUDE.md .clauderules .cursor/ .windsurfrules   # ponteiros finos → .sfk/kernel/BOOTSTRAP.md
├── .gitattributes                # /.sfk/** linguist-vendored
└── src/ apps/ ...                # produto
```

### Repo do SFK (dogfooding — usa o próprio `.sfk/`)
```
SFK/
├── .sfk/kernel/...               # o engine que é copiado
├── memory/ docs/ sfk.toml SYSTEM.md   # SFK como projeto de si mesmo
├── bin/                          # CAT C consolidada (era 3 lugares)
│   ├── new-project(.sh/.ps1) update-project(.sh/.ps1) manage-skill
│   └── lib/ (jb_kit_turbo.py, sfk_updater.py)
├── _blueprint/                   # overrides de template limpo (mantido, fora da vista)
└── README CHANGELOG LICENSE CONTRIBUTING
```

---

## 4. Fases de Execução

### FASE 0 — Correções sem risco (não dependem de mover nada)
**Objetivo:** valor imediato + destravar a D4 na base.
- Adicionar em `RULES.md` a **Lei de Fronteira de Arquivos** (nova lei fundamental): engine `.sfk/` read-only; estado do projeto na raiz; a IA nunca trata engine como produto nem edita `.sfk/` salvo manutenção explícita do SFK.
- Corrigir bug de referência: `kernel/AUDIT_CHECKLIST.md` → `memory/logs/SESSION-AUDIT-CHECKLIST.md`.
- Corrigir/normalizar referência a `DEPLOY_ENV_REFERENCE.md` (nome único, singular).
- **Validação:** grep não encontra mais referências a `AUDIT_CHECKLIST.md`; RULES contém a nova lei.
- **Risco:** baixo.

### FASE 1 — Mover engine para `.sfk/kernel/`
**Objetivo:** eliminar a colisão na raiz.
- `git mv kernel/ .sfk/kernel/`; criar `.sfk/VERSION` e `.sfk/MANIFEST`.
- **Reescrita de paths** (script guiado): todo `kernel/…` → `.sfk/kernel/…` em: RULES, SOUL, BOOTSTRAP, index.toml, ARCHITECTURE, TESTING_GUIDE, 20 agents, 58 skills, 11 workflows, CLAUDE.md, `.clauderules`, `.cursor/rules`, `.windsurfrules`, `jb_kit_turbo.py`, `sfk_updater.py`, README, QUICKSTART.
- `memory/…` e `docs/…` **não mudam** de path (permanecem na raiz).
- Adicionar `.gitattributes`: `/.sfk/** linguist-vendored`.
- **Validação:** grep por `(^|[^.])kernel/` fora de `.sfk/` retorna zero (exceto histórico/changelog); sessão de bootstrap lê `.sfk/kernel/BOOTSTRAP.md` sem erro.
- **Risco:** médio (é o grosso). Mitigação: script de reescrita idempotente + diff revisado antes do commit.

### FASE 2 — Consolidar tooling em `bin/`
**Objetivo:** tirar categoria C da raiz e dos 3 locais.
- `tools/*` + `new-project.*` + `update-project.*` → `bin/` (`bin/lib/` para os `.py`, wrappers finos `.sh/.ps1`).
- Decidir `import_skill.py`: se é ação do dev → `bin/manage-skill`; senão permanece runtime em `.sfk/kernel/scripts/`.
- Ajustar `jb_kit_turbo.py` (`BLUEPRINT_DIRS`, `EXTRA_CONFIG_FILES`) para o novo layout: copiar `.sfk/`, `memory/`, `docs/`, `sfk.toml`, `SYSTEM.md`, ponteiros e `.gitattributes`.
- **Validação:** `bin/new-project` gera um projeto-teste com o layout-alvo correto (`.sfk/` + raiz limpa).
- **Risco:** médio (scaffolder é crítico). Mitigação: teste de scaffold em pasta temp antes do commit.

### FASE 3 — Config na raiz + governança de memória/docs (D1, D2, D3 e ponto 4)
**Objetivo:** resolver as dores de organização de estado.
- **Rename** `project.toml` → `sfk.toml`; mover `SYSTEM.md` para a raiz; atualizar todas as referências.
- **D1:** redefinir `memory/progress.md` como **Painel de Retomada** — **Markdown com estrutura fixa** (RETOMAR AQUI / Em aberto / Status por módulo) + **frontmatter TOML/YAML mínimo** (`updated, active_plan, phase, status, blockers`) para parse determinístico pelo hook e pelo `/status`. Formato deliberadamente **não-JSON** (JSON custa mais tokens, quebra fácil, diff ruim; TOML é o formato-casa do SFK). BOOTSTRAP passa a ler só este arquivo na retomada.
- **D2:** criar convenção `docs/integrations/` (um arquivo por serviço) + `sfk.toml [[integrations]]` como índice único; regra em RULES.
- **Deploy/env:** `sfk.toml [hosting.*]`+`[environments.*]` = fonte de verdade das env vars (só nomes, nunca valores); `docs/deploy/` = runbook por alvo (domínios, onde setar, webhook, checklist de troca); histórico de provedor anterior preservado em `docs/deploy/_history/` + `DECISION`. Consolidar os duplicados `DEPLOY_ENV_REFERENCE.md`/`DEPLOY_ENV_REFERENCES.md`; vars de serviço externo (ex.: Stripe) migram para `docs/integrations/`. Nova regra dura em RULES: **repo guarda nomes+local, nunca valores.**
- **D3:** definir `db/migrations/` e `db/seeds/` numerados; `sfk.toml [db] migrations_path`; `BUILD-HISTORY.md` vira **ledger de aplicação** (data/ambiente); regra em RULES.
- **Ponto 4 (EVOLUTION):** remover `docs/evolutive_changes/EVOLUTION_MEMORY.md` e `_blueprint/.../EVOLUTION_MEMORY.md`; remover suas 3 referências em `RULES.md §9.1/§11`; governar (ou aposentar) `docs/evolutive_changes/`.
- **Validação:** grep por `EVOLUTION_MEMORY` retorna zero; scaffold novo já nasce com `docs/integrations/` e `db/` documentados; `progress.md` com template do Painel.
- **Risco:** baixo/médio.

### FASE 4 — De-duplicar e comprimir a Camada 1 (ponto 6 + D4)
**Objetivo:** uma fonte por regra + retenção.
- Consolidar regra única de classificação NEW/EXISTING (hoje em 5 lugares) → definição canônica em RULES; demais apontam.
- Consolidar preservação de headings de docs (hoje em 3 lugares).
- `SOUL.md` fica só persona/tom/comunicação; delega processo à RULES por ponteiro.
- Criar `.sfk/kernel/OPERATING_CARD.md` (≤20 linhas, sempre carregado) com os inegociáveis.
- **D4:** criar `.sfk/kernel/hooks/pre-commit` que **bloqueia** commit se: mudança de código sem toque em `MODIFICATION_LOG`, ou plano `-DONE` sem `Git Record`. Instalação do hook no scaffold/update. `--no-verify` como escape documentado.
- **Validação:** cada regra-chave tem exatamente uma definição autoritativa (grep de contagem); hook bloqueia commit de teste sem log e libera com log.
- **Risco:** médio (hook pode incomodar). Mitigação: escopo do hook conservador + escape documentado.

### FASE 5 — Migração de projetos existentes via `sfk_updater.py`
**Objetivo:** migrar JLR_Beauty (e outros) do layout antigo para o novo sem perder estado.
- Updater lê o layout antigo, move `kernel/` → `.sfk/kernel/`, reescreve paths, renomeia `project.toml` → `sfk.toml`, instala hooks e ponteiros.
- Tratar sujeira real detectada: arquivos duplicados (`INTEGRATIONS`, `DEPLOY_ENV`), `TESTING_GUIDE` vazado, gaveta `evolutive_changes/`, lixo (`arvore.txt`, `tmp/`, `null`) — relatório + ação sugerida (não apagar sem confirmação).
- **Validação:** rodar o updater em cópia de JLR_Beauty; bootstrap da IA funciona; nenhum arquivo de `memory/`/`docs/project` perdido; relatório de duplicatas gerado.
- **Risco:** alto (dados reais). Mitigação: dry-run + backup + rodar só em cópia primeiro.

---

## 5. Inventário de reescrita de paths (Fase 1)
- Padrão a substituir: `kernel/` → `.sfk/kernel/` (exceto dentro de CHANGELOG histórico).
- Padrão a substituir: `project.toml` → `sfk.toml` (Fase 3).
- **Não** substituir: `memory/`, `docs/` (permanecem na raiz).
- Ferramenta: script de reescrita idempotente + revisão de diff obrigatória antes do commit de cada fase.

---

## 6. Riscos globais e Rollback
- Cada fase = um commit isolado e reversível (`git revert`).
- Fases 1, 2, 5 exigem teste em pasta temp/cópia antes do commit.
- Ordem garante que nada quebra: F0 (aditivo) → F1 (move+reescreve) → F2 (tooling) → F3 (config/memória) → F4 (regras/hook) → F5 (migração externa).
- Aprovação de commit e push seguem o Git Kernel (dupla autorização) — nada é commitado/pushed sem seu OK explícito.

---

## 7. Git Record of Delivery
> A preencher na execução. Nenhum plano vira `-DONE` sem esta seção completa (RULES §10.5).
- Passo 1 (Pre-commit review): _pendente_
- Passo 2 (Commit authorization): _pendente_
- Passo 3 (Commit confirmation): _pendente_
- Passo 4 (Push authorization e resultado): _pendente_
- Push status: PENDING

---

## 8. Checklist de aprovação (o que preciso do usuário)
- [ ] Aprovar o desenho-alvo (seção 3) e o princípio diretor (seção 2).
- [ ] Aprovar a ordem das 6 fases.
- [ ] Autorizar início pela **Fase 0** (sem risco) — ou indicar outra fase.
- [ ] Confirmar que a migração do JLR_Beauty (Fase 5) roda **só em cópia** primeiro.

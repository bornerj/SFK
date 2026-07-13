# PLAN-0004 — Scaffolder de projeto novo: parar de copiar o histórico real do SFK

> **Status:** DONE — F1–F4 implementadas, validadas e commitadas em `main` (commit combinado com `PLAN-0003`, dependência entre os dois).
> **Tipo:** SIMPLE CODE (bug fix, um arquivo) · **Categoria de arquivo:** C (tooling do mantenedor → `bin/lib/`)
> **Origem:** Achado colateral durante investigação do `PLAN-0003`, confirmado pelo usuário.

---

## 1. Situação (STAR — Situation)

Ao investigar o bug do `sfk_updater.py` (`PLAN-0003`), foi identificado que o scaffolder
de **projeto novo** tem o mesmo problema de princípio, na direção oposta:
`jb_kit_turbo.py::copy_blueprint()` copia a árvore inteira de `memory/`, `docs/`, `db/`
e `.sfk/` do repositório SFK via `shutil.copytree`, com um `ignore_filter` que só filtra
lixo técnico (`.git`, `node_modules`, `__pycache__`, etc.) — não filtra por conteúdo.

`apply_blueprint_overrides()` substitui 4 arquivos específicos por versões em branco
(`_blueprint/SYSTEM.md`, `_blueprint/memory/progress.md`,
`_blueprint/memory/logs/DRIFT-RULES.md`, `_blueprint/memory/logs/BUILD-HISTORY.md`).
`reset_starter_docs()` reescreve mais 2 (`memory/MODIFICATION_LOG.md`,
`memory/logs/DEBUG-HISTORY.md`) e garante (`mkdir`, sem limpar) que
`memory/plans/`/`memory/decisions/` existam.

**O que sobra sem tratamento nenhum — confirmado por inspeção direta do repo:**
- `memory/plans/PLAN-0001-*.md`, `PLAN-0002-*.md`, `PLAN-0003-*.md` — entregas reais
  deste repositório SFK, não templates.
- `memory/PR-0001-DESCRIPTION.md` — descrição de PR real deste repositório.

(`docs/`, `db/`, `.sfk/`, e `memory/decisions/DECISION-XXX.md` já estão limpos hoje —
verificado; não precisam de mudança.)

Usuário confirmou o princípio: **só o framework** (`.sfk/` + esqueleto em branco de
`memory/`, `docs/`, `db/`) deve propagar para projetos novos; nada da história de
desenvolvimento deste repositório específico.

## 2. Tarefa (STAR — Task)

Impedir que arquivos de histórico real (planos, decisões, PRs deste repositório)
cheguem a um projeto novo escaffoldado — automaticamente, sem exigir manutenção manual
de uma lista toda vez que um novo `PLAN-000N` for criado aqui.

**Critério de filtro (aproveita a própria convenção de nomes já em uso):** um arquivo é
**template** quando o número de sequência no nome é o placeholder literal (`XXXX`/`XXX`
— ex.: `PLAN-XXXX-DONE-subject.md`, `DECISION-XXX.md`, `PR-XXXX-DESCRIPTION.md`); é
**histórico real** quando tem um número de verdade (`PLAN-0001`, `PR-0001`, um futuro
`DECISION-001`). Regex: nome do arquivo começa com `(PLAN|DECISION|PR)-` seguido de
dígitos → histórico real, nunca propaga. Autoaplicável a qualquer `PLAN-000N` futuro
sem precisar tocar o filtro de novo.

## 3. Ação (STAR — Action) — Fases

| Fase | Entrega | Risco |
|------|---------|-------|
| **F1 — Filtro real-vs-template** | Nova função utilitária em `jb_kit_turbo.py` (ex.: `is_real_repo_history(name: str) -> bool`, regex `^(PLAN|DECISION|PR)-\d+`), **exportável** (será importada pelo `PLAN-0003` para o mesmo propósito no bootstrap do updater — ver dependência lá). Aplicada dentro de `ignore_filter()` (ou callback próprio) para que `copy_blueprint()` nunca escreva esses arquivos no destino — filtro na origem, não limpeza depois de copiar. | baixo |
| **F2 — Cobertura de `memory/PR-*-DESCRIPTION.md`** | Mesmo filtro cobre esse caso (está na raiz de `memory/`, dentro do mesmo `copytree`); confirmar que `PR-XXXX-DESCRIPTION.md` (template) continua sendo copiado normalmente. | baixo |
| **F3 — Testes & validação** | Scaffold de projeto novo (fixture temp dir) → confirmar: `memory/plans/` contém **só** `PLAN-XXXX-DONE-subject.md`; `memory/decisions/` contém **só** `DECISION-XXX.md`; `memory/` (raiz) contém **só** `PR-XXXX-DESCRIPTION.md`, não `PR-0001-*`; `.sfk/`, `docs/`, `db/` inalterados (regressão); `memory/MODIFICATION_LOG.md`/`DEBUG-HISTORY.md`/`progress.md`/`DRIFT-RULES.md`/`BUILD-HISTORY.md` continuam em branco como já eram. `py_compile` limpo. | baixo |
| **F4 — Memória & fechamento** | `memory/logs/DEBUG-HISTORY.md` (ERR-000X, dogfooding); `memory/MODIFICATION_LOG.md`; `memory/progress.md`; fechamento do plano com Git Record. | baixo |

**Nota de sequenciamento:** `PLAN-0003` (F1/F2) importa o utilitário criado aqui. Rodar
`PLAN-0004` primeiro evita implementar o filtro duas vezes.

## 4. Resultado esperado (STAR — Result)

- Um projeto novo escaffoldado nunca mais recebe `PLAN-000N`/`PR-000N` reais deste
  repositório — só os templates com placeholder (`XXXX`/`XXX`).
- Nenhuma regressão no restante do scaffold (`.sfk/`, `docs/`, `db/`, os 6 arquivos já
  tratados por `apply_blueprint_overrides`/`reset_starter_docs`).
- Validação: rodar o scaffolder numa pasta temp, inspecionar `memory/` resultante.

## 5. Riscos e mitigações

- **Regex falso-positivo/negativo:** mitigado por manter o padrão simples e ancorado
  (`^(PLAN|DECISION|PR)-\d+`) — mesma convenção de nomenclatura já documentada em
  `RULES.md §9`; qualquer arquivo fora desse padrão não é afetado.
- **Import cruzado com `sfk_updater.py` (`PLAN-0003`):** os dois scripts já vivem em
  `bin/lib/`; import direto de módulo (`from jb_kit_turbo import is_real_repo_history`)
  é suficiente, sem precisar de um terceiro módulo compartilhado.

## 6. Fora de escopo (explícito, anti-scope-drift)

- Não mexe em `sfk_updater.py` — isso é o `PLAN-0003`.
- Não reorganiza a estrutura de `_blueprint/` nem os 6 arquivos já tratados.
- Não adiciona um mecanismo genérico de "export-ignore" (`.gitattributes`-like) — o
  regex simples resolve o caso real conhecido sem nova infraestrutura.

## 7. Git Record of Delivery
- Step 1 (Pre-commit review): feito — arquivos listados e resumidos ao usuário, validações (py_compile + fixture) executadas antes do pedido de autorização.
- Step 2 (Commit authorization): usuário autorizou commit único combinado com `PLAN-0003`.
- Step 3 (Commit confirmation): _este commit_
- Step 4 (Push authorization and result): usuário autorizou (junto com commit adicional do ERR-0003) — `git push origin main` → `a0377d5..d7086d7`.
- Push status: COMPLETED

## 8. Checklist de aprovação (preciso de você antes de codar) — CONCLUÍDO
- [x] Aprovar o critério de filtro (regex baseado em placeholder vs. número real).
- [x] Confirmar a ordem de execução: `PLAN-0004` antes do `PLAN-0003` (F1/F2 de lá
      dependem do utilitário criado aqui).
- [x] Autorizar início pela F1.

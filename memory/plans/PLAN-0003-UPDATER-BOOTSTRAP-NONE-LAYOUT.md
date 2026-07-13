# PLAN-0003 — sfk_updater.py: instalação bootstrap para projetos sem SFK (layout `none`)

> **Status:** DONE — F1–F5 implementadas, validadas e commitadas em `main` (commit combinado com `PLAN-0004`, dependência entre os dois).
> **Tipo:** SIMPLE-a-COMPLEX CODE (bug fix estrutural em ferramenta central) · **Categoria de arquivo:** C (tooling do mantenedor → `bin/lib/`)
> **Origem:** Bug reportado pelo usuário via SFK Launcher (GUI) — botão "➕ Adicionar o SFK a um projeto que já existe".

---

## 1. Situação (STAR — Situation)

O usuário tentou usar o botão "Adicionar o SFK a um projeto existente" do SFK Launcher
num projeto pequeno, já iniciado, **sem nenhum SFK instalado**. O painel mostrou:

```
ERROR: '.../reports/dashboard' is not an SFK project
(no .sfk/kernel/BOOTSTRAP.md or kernel/BOOTSTRAP.md).
```

Investigação (RAG + 5 Whys, `@debugger`):
1. `sfk_gui.py::UpdateProjectView` (linha ~626) chama `bin/lib/sfk_updater.py` tanto para
   "Adicionar" quanto para "Atualizar" (mesma ação, header diferente — decisão registrada
   no `MODIFICATION_LOG.md` de 2026-07-08, Fase 3 do PLAN-0002).
2. `sfk_updater.py::detect_layout()` retorna `"current"` / `"legacy"` / `"none"`.
3. `main()` (linhas 371-378) trata `"none"` como **erro fatal** — comportamento
   documentado no próprio docstring do arquivo (`NONE → not an SFK project (aborts)`).
4. **Causa raiz:** o updater nunca implementou de fato um terceiro caminho para
   "projeto sem SFK nenhum". O botão "Adicionar" promete esse caminho, mas ele não existe
   — é o guard antigo de "isso não é um projeto SFK" que ficou como está.
5. Não é a GUI chamando o script errado — é o script que não tem o caso de uso.

**Achado colateral — confirmado pelo usuário, tratado em `PLAN-0004` (plano separado):**
`jb_kit_turbo.py::copy_blueprint()` (scaffolder de projeto novo) copia a árvore inteira
de `memory/` via `shutil.copytree`, incluindo os arquivos **reais** deste repositório
(`memory/plans/PLAN-0001-*.md`, `PLAN-0002-*.md`, `PLAN-0003-*.md`,
`memory/PR-0001-DESCRIPTION.md`). `reset_starter_docs()` só limpa `MODIFICATION_LOG.md`
e `DEBUG-HISTORY.md` — o resto do histórico real do próprio SFK vaza para dentro de
projetos novos escaffoldados. Regra confirmada pelo usuário: só o **framework**
(`.sfk/` + esqueleto em branco de `memory/`, `docs/`, `db/`) deve propagar; nada da
história de desenvolvimento deste repositório. Ver `PLAN-0004` — inclui uma dependência
leve com este plano (seção 2 abaixo).

## 2. Tarefa (STAR — Task)

Dar ao `sfk_updater.py` um terceiro caminho real — **bootstrap** — para
`layout == "none"`: instalar o SFK dentro da pasta do projeto existente, **sem nunca
sobrescrever arquivos que já existem no projeto** (decisão confirmada com o usuário).
Diferente do scaffolder de "projeto novo" (que assume pasta vazia/`--force`), aqui a
regra é estritamente aditiva.

Restrições descobertas no RAG:
- `.sfk/MANIFEST` já é aditivo por natureza quando o destino não existe — não precisa
  de lógica nova, só parar de abortar antes de chegar lá.
- `sfk.toml`/`SYSTEM.md` hoje **nunca** são tocados pelo updater (são "project state").
  Para bootstrap, precisam ser **criados** (não existem ainda) a partir de templates
  limpos: `sfk.toml` da raiz do SFK (já é um template em branco — `[project] name = ""`);
  `SYSTEM.md` de `_blueprint/SYSTEM.md` (versão em branco; a raiz do SFK tem a versão
  **preenchida** real deste repo, não serve de template).
- `EXTRA_CONFIG_ITEMS` (`.clauderules`, `CLAUDE.md`, `.windsurfrules`, `.gitignore`,
  `.cursor`, `.gitattributes`) hoje fazem sync completo (sobrescreve se diferente) — modo
  correto para projetos já-SFK, mas destrutivo demais para o primeiro bootstrap num
  projeto com `.gitignore`/`CLAUDE.md` próprios. Bootstrap usa modo **novo-apenas**.
- `memory/MODIFICATION_LOG.md` e `memory/logs/DEBUG-HISTORY.md` da raiz do SFK são o
  **histórico real deste repositório** — não podem ser copiados como estão para um
  projeto de terceiro. Precisam do conteúdo em branco (mesmo texto que
  `jb_kit_turbo.py::reset_starter_docs()` já gera para projetos novos).
- `memory/plans/`, `memory/decisions/` e `memory/PR-*-DESCRIPTION.md` da raiz do SFK
  contêm entregas **reais** deste repositório — não devem ser copiados. Critério
  reutilizável (mesmo do `PLAN-0004`): um arquivo é **template** quando o número da
  sequência no nome é o placeholder literal (`XXXX`/`XXX`); é **histórico real** quando
  tem um número de verdade (`PLAN-0001`, `PR-0001`, um futuro `DECISION-001`). Reaproveita
  o filtro que o `PLAN-0004` cria no scaffolder (ver F1 daquele plano) via import — não
  duplica a regra em dois arquivos.
- `docs/project/*.md`, `docs/integrations/*.md`, `docs/deploy/README.md`, `db/*/README.md`
  na raiz do SFK já são templates genéricos (`[FILL IN]`) — seguros para cópia direta.

## 3. Ação (STAR — Action) — Fases

| Fase | Entrega | Risco |
|------|---------|-------|
| **F1 — Núcleo do bootstrap em `sfk_updater.py`** | `detect_layout("none")` deixa de abortar; novo branch de bootstrap monta um `SyncItem` plan **novo-apenas** cobrindo: (a) engine `.sfk/` via MANIFEST existente [sem mudança de lógica]; (b) `sfk.toml` + `SYSTEM.md` (blueprint em branco); (c) `EXTRA_CONFIG_ITEMS` em modo novo-apenas (só para `none`; `current`/`legacy` continuam com sync completo, sem regressão); (d) `docs/project/*`, `docs/integrations/*`, `docs/deploy/*`, `db/migrations/README.md`, `db/seeds/README.md` — cópia direta novo-apenas; (e) `memory/` — reaproveita `BLUEPRINT_NEW_ONLY_ITEMS` existente + novo conteúdo em branco para `MODIFICATION_LOG.md`/`DEBUG-HISTORY.md` + filtro real-vs-template de `memory/plans/`/`memory/decisions/`/`memory/PR-*-DESCRIPTION.md` (importado do utilitário criado no `PLAN-0004`, ver dependência na seção 2). Mensagem de console dedicada ("Detectado layout NONE — instalação inicial (bootstrap)") + notas pós-instalação (preencher `sfk.toml`, revisar `SYSTEM.md`, primeira sessão de IA relê o BOOTSTRAP). | médio (arquivo central, mas puramente aditivo) |
| **F2 — Reuso sem duplicação** | Pequeno refactor em `jb_kit_turbo.py`: extrair o conteúdo em branco de `MODIFICATION_LOG.md`/`DEBUG-HISTORY.md` (hoje inline em `reset_starter_docs()`) para funções/constantes importáveis, usadas tanto pelo scaffolder de projeto novo quanto pelo bootstrap do updater — sem duplicar template em dois arquivos. **Sem mudança de comportamento** no fluxo de projeto novo (mesma saída de texto). | baixo |
| **F3 — Docstring & mensagens** | Atualiza o docstring de `sfk_updater.py` (seção "Layouts detected") e `USAGE.md` para descrever o novo caminho `NONE → bootstrap` em vez de "aborta". Copy da `UpdateProjectView` no GUI revisada (sem mudança estrutural esperada) para garantir que a saída faça sentido no botão "Adicionar". | baixo |
| **F4 — Testes & validação** | (1) Fixture "projeto frio": pasta com `README.md`, um arquivo de código, `.gitignore` próprio, sem SFK → dry-run mostra plano correto (só adições); apply instala `.sfk/`, `sfk.toml`, `SYSTEM.md`, `memory/docs/db`; confirma que `README.md`/`.gitignore`/arquivo de código **não foram tocados**. (2) Regressão: fixture CURRENT (sync) e fixture LEGACY (migração) — saída idêntica à de antes da mudança. (3) `py_compile` nos dois arquivos. (4) Dry-run (somente leitura, seguro) contra o projeto real do usuário (`.../antigravity-awesome-skills/reports/dashboard`) para confirmar que o caso relatado está resolvido — **aplicar de verdade só com nova autorização explícita do usuário nesse momento**, fora deste plano de implementação. | baixo (dry-run) / médio (apply real, gated por aprovação separada) |
| **F5 — Memória & fechamento** | `memory/logs/DEBUG-HISTORY.md` (ERR-0001, deste repositório, dogfooding); `memory/MODIFICATION_LOG.md` por fase; `memory/progress.md` atualizado; `USAGE.md` atualizado (F3 já cobre o texto, aqui é o registro); fechamento do plano com Git Record. | baixo |

## 4. Resultado esperado (STAR — Result)

- Botão "Adicionar o SFK a um projeto existente" funciona de fato em projetos sem SFK:
  dry-run mostra plano aditivo, apply instala sem tocar em nada pré-existente.
- Fluxos "Atualizar" (current/legacy) permanecem **bit-a-bit iguais** ao comportamento
  atual — nenhuma regressão.
- Validação: reproduzir o erro original antes do fix, confirmar que some depois, mais os
  testes de regressão da F4.

## 5. Riscos e mitigações

- **Sobrescrever arquivo do usuário:** mitigado por modo novo-apenas em todo o caminho
  de bootstrap (nenhum item do bootstrap sobrescreve arquivo já existente no destino).
- **Vazar histórico real do SFK para o projeto do usuário:** mitigado por gerar conteúdo
  em branco para `MODIFICATION_LOG.md`/`DEBUG-HISTORY.md` e não copiar `memory/plans/PLAN-000X`
  nem `memory/decisions/DECISION-XXX` reais (só o arquivo-template).
- **Hook pre-commit passa a bloquear o próximo commit do usuário** se ele não atualizar
  `MODIFICATION_LOG.md` — comportamento esperado/by design do SFK, será citado nas notas
  pós-instalação, não é um bug.
- **Regressão em current/legacy:** mitigada por manter o sync completo desses dois
  layouts intocado; só o layout `none` ganha o modo novo-apenas.

## 6. Fora de escopo (explícito, anti-scope-drift)

- O achado colateral do scaffolder de projeto novo é tratado em `PLAN-0004` (plano
  separado, aprovado com o usuário) — não é reimplementado aqui além do import do
  utilitário de filtro que aquele plano cria.
- Nenhuma mudança em `.sfk/kernel/` (engine) além do que já é sincronizado hoje.
- Nenhuma alteração no comportamento de `current`/`legacy` além de deixar de existir o
  branch `"none" → erro`.

**Dependência entre planos:** a F1 deste plano importa o filtro real-vs-template que o
`PLAN-0004` cria em `jb_kit_turbo.py`. Ordem sugerida: `PLAN-0004` primeiro (menor,
um arquivo só) — ver seção 8 para confirmar a ordem com o usuário.

## 7. Git Record of Delivery
- Step 1 (Pre-commit review): feito — arquivos listados e resumidos ao usuário, validações (py_compile + fixture fria + regressão LEGACY/CURRENT + dry-run no projeto real) executadas antes do pedido de autorização.
- Step 2 (Commit authorization): usuário autorizou commit único combinado com `PLAN-0004`.
- Step 3 (Commit confirmation): _este commit_
- Step 4 (Push authorization and result): usuário autorizou (junto com commit adicional do ERR-0003) — `git push origin main` → `a0377d5..d7086d7`.
- Push status: COMPLETED

## 8. Checklist de aprovação (preciso de você antes de codar) — CONCLUÍDO
- [x] Aprovar as fases F1–F5 acima.
- [x] Confirmar que o teste F4(4) pode rodar em **dry-run** contra o projeto real
      (`antigravity-awesome-skills/reports/dashboard`) — só leitura, nada é escrito.
- [x] Autorizar início pela F1.

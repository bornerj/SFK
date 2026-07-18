# PLAN-0005 — SFK Launcher GUI: compactar layout + alternador de idioma PT/EN

> **Status:** DONE — F1–F5 implementadas, validadas, commitadas e enviadas para `origin/main`.
> **Tipo:** DESIGN/UI (COMPLEX CODE) · **Categoria de arquivo:** C (tooling do mantenedor → `bin/`)
> **Origem:** Usuário reportou que a janela do SFK Launcher (`bin/sfk_gui.py`) é grande
> demais — o último card da Home ("Checar um projeto") fica cortado e exige
> redimensionamento manual — e pediu um alternador de idioma PT/EN no canto superior
> direito, junto com fontes/janela menores.

---

## 1. Situação (STAR — Situation)

Inspeção de `bin/sfk_gui.py` (956 linhas, Tkinter puro, zero-install) confirmou a causa
raiz do corte: `App.__init__` fixa `geometry("880x620")` / `minsize(720, 520)`
(linha 899-900), enquanto `HomeView` empilha 5 `ActionCard` de `height=92px` cada
(linha 205) mais título/subtítulo/paddings de `Theme.SPACE_XL=32` — a soma passa da
altura da janela, cortando o último card sem scroll.

Não existe nenhuma camada de i18n hoje: todos os textos (títulos, botões, checkboxes,
mensagens de console, diálogos `messagebox.askyesno`) estão hardcoded em português,
espalhados pelas 6 views (`HomeView`, `CheckProjectView`, `NewProjectView`,
`UpdateProjectView` — instanciada 2x para "add_existing"/"update_project" — e
`SkillsView`) e nos helpers compartilhados (`Header`, `ResultBanner`, `PathPicker`,
`ConsolePanel`, título da janela).

Decisões já validadas com o usuário (ver seção 8):
- Tradução cobre **tudo** (labels, botões, checkboxes, mensagens de console/erro e
  diálogos de confirmação) — não só a interface principal.
- Idioma escolhido **persiste** entre uma abertura e outra do launcher.
- Resolver o corte **encolhendo** fontes/espaçamentos/cards (não deixando do tamanho
  atual com scroll).

## 2. Tarefa (STAR — Task)

1. Compactar o layout (fontes, `Theme.SPACE_*`, altura do `ActionCard`, geometria da
   janela) o suficiente para os 5 cards da Home caberem sem corte no tamanho padrão,
   sem depender de redimensionamento manual.
2. Adicionar um alternador de idioma PT/EN, sempre visível no canto superior direito
   (em toda tela, não só na Home), que retraduz a interface **sem perder o que o
   usuário já digitou** (caminho de pasta, nome do projeto, etc. — ver §5 sobre por
   que não escolhi "reconstruir a view inteira").
3. Persistir a escolha de idioma entre sessões, fora do repositório (preferência de
   usuário, não estado de projeto).

## 3. Ação (STAR — Action) — Fases

| Fase | Entrega | Risco |
|------|---------|-------|
| **F1 — Fundação i18n** | Novo módulo `bin/lib/gui_i18n.py`: dicionário `STRINGS = {"pt": {...}, "en": {...}}` com uma chave por texto de UI (títulos, botões, checkboxes, headers, mensagens de console/erro, textos de `messagebox`, título da janela); classe `Lang` (`current: str`, `t(key) -> str`); `load_lang()`/`save_lang()` lendo/gravando um arquivo de preferência em `Path.home() / ".sfk_launcher_lang"` (texto puro, `"pt"` ou `"en"`; falha silenciosa e volta pro padrão `"pt"` se o arquivo não existir/for inválido — preferência de UI, não é log auditável, não entra em `memory/`). | baixo |
| **F2 — Layout compacto** | Em `bin/sfk_gui.py`: reduzir `Theme.SPACE_XL/LG/MD/SM/XS` (32→24, 24→18, 16→12, 8→6, 4→3), `Fonts` (`title` 22→18, `h1` 15→13, `h2` 12→11, `body`/`body_bold` 11→10, `small` 9→8, `mono` 10→9), `ActionCard.RADIUS`/`height` (92→72, texto reposicionado no `_redraw`). Recalcular `App.geometry`/`minsize` para o novo total (estimativa: ~760x560 / minsize ~680x480 — valor final ajustado na validação visual da F4, matemática de pixel do Tkinter varia por fonte/SO). | médio (fonte pequena demais prejudica legibilidade — mitigado pela checagem manual na F4) |
| **F3 — Widget de idioma + retradução in-place** | Widget `LangSwitch` (dois `tk.Label` clicáveis "PT"/"EN", ou toggle equivalente) adicionado direto em `App` (não dentro de `self._container`) e posicionado com `place(relx=1.0, x=-16, y=12, anchor="ne")` + `.lift()` — fica por cima de qualquer view, pois não é substituído no `tkraise()` entre telas. Cada view passa a guardar referência (`self.xxx`) de **todo** widget com texto estático (títulos, labels, checkboxes, botões) em vez de criar alguns inline sem referência como hoje; cada view ganha um método `retranslate()` que atualiza `.configure(text=...)` desses widgets a partir de `Lang.t(key)`. Ao clicar no switch: `Lang.current` muda, `save_lang()` grava a preferência, e `App` chama `retranslate()` em todas as views já instanciadas (estado dos campos — caminho digitado, checkboxes marcados — preservado, nada é destruído/recriado). Mensagens já escritas no `ConsolePanel` (histórico de uma execução passada) **não** são retraduzidas retroativamente — só o texto estático da UI; textos novos de console (próxima execução) já saem no idioma atual. | alto (é o item com mais superfície: ~60 strings espalhadas em 6 views + `Header`/`ResultBanner`/`PathPicker`/título da janela — risco de esquecer alguma; mitigado por checklist item-a-item na F4 antes de fechar) |
| **F4 — Testes & validação** | Rodar `python3 bin/sfk_gui.py` manualmente: (a) confirmar os 5 cards da Home visíveis sem redimensionar, no tamanho padrão da F2; (b) navegar por todas as 6 telas nos dois idiomas, conferindo cada label/botão/checkbox/mensagem de erro/diálogo de confirmação contra a chave esperada (checklist string-a-string); (c) confirmar que a preferência persiste (fechar e reabrir o launcher, ou reler o arquivo de preferência); (d) rodar os fluxos existentes (Checar projeto com dry-run, Skills → listar) para confirmar que nada quebrou no encanamento de `ProcessRunner`/`PathPicker` por causa da refatoração de referências. | baixo (validação, não implementação nova) |
| **F5 — Memória & fechamento** | `memory/MODIFICATION_LOG.md` (mudança sem plano ativo de bug, é o próprio PLAN-0005 — registrar marco START/END); `memory/progress.md` (módulo "SFK Launcher (GUI)" — nota atualizada, ainda `stable`); fechamento do plano com Git Record preenchido. | baixo |

## 4. Resultado esperado (STAR — Result)

- Janela padrão do launcher abre já mostrando os 5 cards da Home, sem corte e sem
  precisar redimensionar manualmente.
- Fontes e espaçamentos visivelmente menores em todas as telas, mantendo legibilidade.
- Alternador PT/EN visível no canto superior direito em qualquer tela; troca o idioma
  de toda a interface (incluindo mensagens de erro e diálogos de confirmação) sem
  apagar o que o usuário já preencheu.
- Escolha de idioma sobrevive a fechar/reabrir o launcher (arquivo em
  `~/.sfk_launcher_lang`).
- Nenhuma regressão nos fluxos existentes (criar projeto, adicionar/atualizar,
  checar projeto, skills).

## 5. Riscos e mitigações

- **Cobertura incompleta da tradução:** maior risco do plano — 6 views + helpers
  compartilhados. Mitigado por checklist string-a-string na F4 antes de marcar DONE.
- **Reconstruir view vs. retraduzir in-place:** cogitei destruir e recriar todas as
  views a cada troca de idioma (mais simples de implementar), mas isso apagaria
  caminho/nome já digitados pelo usuário no meio de uma tarefa — rejeitado. Retradução
  in-place custa mais linhas (toda label estática precisa de referência), mas não perde
  dado do usuário.
- **Fonte pequena demais:** mitigado por validação visual manual na F4 antes de fechar;
  se `body`=10/`small`=8 ficar ilegível em algum SO, ajusto o valor ali mesmo (é
  constante única em `Fonts.load`, sem impacto em cascata).
- **Geometria "no chute":** os números de `App.geometry`/`minsize` na F2 são estimativa;
  valor final é o que passar na checagem visual da F4, não a conta de cabeça.

## 6. Fora de escopo (explícito, anti-scope-drift)

- Não adiciona idiomas além de PT/EN.
- Não detecta idioma do sistema operacional automaticamente — padrão é sempre PT na
  primeira execução (sem arquivo de preferência ainda).
- Não muda nenhuma lógica de negócio/subprocess (`jb_kit_turbo.py`, `sfk_updater.py`,
  `import_skill.py`) — só a camada de apresentação em `bin/sfk_gui.py` + o novo
  `bin/lib/gui_i18n.py`.
- Não introduz dependência externa (PIL, Babel, gettext) — dicionário Python puro,
  mesma filosofia zero-install do arquivo atual.
- Não mexe no ícone (`build_icon_image`) nem no `sfk-launcher.sh`/`.bat`.

## 7. Git Record of Delivery
- Step 1 (Pre-commit review): feito — arquivos: `bin/sfk_gui.py` (M), `bin/lib/gui_i18n.py`
  (novo), `memory/MODIFICATION_LOG.md` (M), `memory/progress.md` (M), este plano (novo);
  `memory/decisions/DECISION-001.md` (novo, entrega de sessão anterior já descrita no
  log, incluída no mesmo commit por consistência — sinalizado ao usuário). Validações
  executadas (F4): `py_compile` limpo; checagem de geometria (5 cards da Home cabem sem
  corte); troca de idioma retraduz todas as views sem perder input digitado;
  persistência round-trip confirmada; fluxo real de dry-run (`CheckProjectView` →
  `sfk_updater.py`) executado de ponta a ponta com sucesso; follow-up do `LangSwitch`
  (chip com borda + re-lift defensivo) revalidado após o feedback do usuário testando
  via atalho do menu do Zorin.
- Step 2 (Commit authorization): usuário autorizou ("faça commit e push").
- Step 3 (Commit confirmation): `f0085d6` — "feat(gui): SFK Launcher compact layout +
  PT/EN language switch" — 6 arquivos, +760/-163.
- Step 4 (Push authorization and result): usuário autorizou junto com o commit —
  `git push origin main` → `57c1f35..f0085d6`.
- Push status: COMPLETED

## 8. Checklist de aprovação — CONCLUÍDO
- [x] Escopo da tradução = tudo (labels, botões, checkboxes, console, diálogos) —
      confirmado.
- [x] Persistência do idioma entre sessões = sim, salvar preferência — confirmado.
- [x] Abordagem de tamanho = encolher fontes/espaçamentos/janela — confirmado.
- [x] Abordagem técnica aprovada: módulo novo `bin/lib/gui_i18n.py` + retradução
      in-place — implementada em F1–F3.
- [x] Localização do arquivo de preferência aprovada: `Path.home() / ".sfk_launcher_lang"`
      — implementada em F1.
- [x] F1–F4 executadas e validadas (ver Git Record acima). Falta apenas a
      autorização de commit/push do usuário para fechar o plano como DONE.

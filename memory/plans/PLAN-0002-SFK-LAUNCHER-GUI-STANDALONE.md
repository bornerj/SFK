# PLAN-0002 — SFK Launcher (GUI standalone, zero-install)

> **Status:** WAITING_APPROVAL (nada será executado até aprovação explícita)
> **Tipo:** COMPLEX CODE · **Categoria de arquivo:** C (tooling do mantenedor → `bin/`)
> **Base funcional:** `USAGE.md` (os 6 cenários de uso já documentados)

---

## 1. Objetivo e contexto

Criar um **aplicativo gráfico único** que executa o SFK por botões, para quem **não
quer saber de comando nem de caminho de pasta na cabeça**. A pessoa só precisa saber:
"quero usar o SFK" e "é um projeto novo ou já existente?". O resto — caminhos, flags,
ordem de passos — o app resolve com **botões de acesso ao disco** e opções
autoexplicativas.

O app é uma **casca fina** sobre as ferramentas já validadas em `bin/lib/` e
`.sfk/kernel/scripts/`. Ele **não reimplementa** lógica: chama o scaffolder, o updater
e o importador de skills, mostrando a saída ao vivo. Assim, a fonte-da-verdade continua
nos scripts Python testados; o GUI só orquestra e traduz para linguagem humana.

## 2. Princípio diretor

> **Zero-install, casca fina, Categoria C.** Nada além do Python (Tkinter é stdlib).
> O GUI mora em `bin/` (tooling do operador do SFK) e **nunca embarca** num projeto
> gerado — coerente com a Lei de Fronteira de Arquivos (RULES §10 / Princípio #10).

## 3. Decisões travadas (confirmadas com o usuário)

| Tema | Decisão | Porquê |
|------|---------|--------|
| Toolkit | **Tkinter** (biblioteca-padrão do Python) | Único GUI "zero-install": não exige `pip install` nada. |
| Distribuição | **Script Python** rodado pelo Python do sistema | O SFK já exige Python; sem passo de build. Launchers de duplo-clique acompanham. |
| Plataformas | **Linux (principal, testado) + Windows (portável)** | Tkinter é multiplataforma; código sem chamadas POSIX-only. macOS deve rodar, mas fora do teste. |
| Empacotar `.exe` (PyInstaller) | **Fora de escopo agora** | Registrado como evolução futura, caso queira entregar binário a não-técnicos. |

> **Ressalva conhecida:** em algumas distros Linux o Tkinter vem separado
> (`python3-tk`). O app detecta a ausência no arranque e mostra uma instrução amigável
> (uma linha para instalar). É o único "install" possível, e é do SO, não do app.

## 4. Desenho da experiência (autoexplicativo e direto)

### Tela inicial — "O que você quer fazer?"
Botões grandes, um por cenário do `USAGE.md`:

```
┌──────────────────────── SFK Launcher ─────────────────────────┐
│                                                               │
│   [ 🌱  Criar um projeto novo ]                                │
│        Começar do zero com o SFK já instalado.                │
│                                                               │
│   [ ➕  Adicionar o SFK a um projeto que já existe ]           │
│        Instalar o SFK sobre um código existente.              │
│                                                               │
│   [ ⬆️  Atualizar o SFK de um projeto ]                        │
│        Trazer a versão mais nova (migra layout antigo).       │
│                                                               │
│   [ 🧩  Skills:  importar nova  ·  atualizar de um projeto ]   │
│                                                               │
│   [ 🔎  Abrir/checar um projeto (pré-visualização) ]           │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Painel de cada ação (padrão comum)
- **Botão "Procurar…"** abre o seletor de pasta do disco (`filedialog.askdirectory`).
  O caminho aparece num campo — a pessoa nunca digita caminho.
- Campos mínimos com **valores-padrão** e **texto de ajuda** embaixo (autoexplicativo).
- **Ações destrutivas/existentes começam por "Pré-visualizar (não altera nada)"**
  (dry-run); "Aplicar" é secundário e pede confirmação.
- **Console ao vivo** (somente leitura) mostrando a saída real do script — transparência.
- Ao terminar: **faixa de resultado** ("✅ Projeto criado em …") + botão **"Abrir pasta"**.

### Mapeamento ação → ferramenta existente
| Ação no app | Chama | Flags que o app injeta |
|-------------|-------|------------------------|
| Criar projeto novo | `bin/lib/jb_kit_turbo.py` | `<pasta>` `--project-name` `--init-git` (padrão on), avançado: `--force`, `--keep-examples` |
| Adicionar SFK / Atualizar | `bin/lib/sfk_updater.py` | `<pasta>` · botão preview = `--dry-run`; aplicar = `--yes`; opção "sem backup" = `--no-backup` |
| Importar skill nova | `.sfk/kernel/scripts/import_skill.py` | `<pasta-da-skill>` `--force` (novo, ver F4) |
| Atualizar skills de um projeto | `bin/lib/sfk_updater.py` | igual ao update (skills fazem parte do engine sincronizado) |
| Checar projeto | `bin/lib/sfk_updater.py --dry-run` | mostra o que mudaria + layout detectado |

## 5. Arquitetura técnica

- **Arquivo:** `bin/sfk_gui.py` (Tkinter, só stdlib). Launchers: `bin/sfk-launcher.sh`,
  `bin/sfk-launcher.bat`, `bin/sfk-launcher.desktop` (duplo-clique → `python sfk_gui.py`).
- **Descoberta da raiz do SFK:** `Path(__file__).resolve().parents[1]` → localiza
  `bin/lib/*.py` e `.sfk/kernel/scripts/import_skill.py`. Usa `sys.executable` como Python.
- **Execução:** `subprocess.Popen(args_list, stdout=PIPE, stderr=STDOUT)` numa **thread**
  de fundo; linhas transmitidas por `queue.Queue` para o widget `Text` via `after()`.
  UI nunca congela; botões desabilitam durante a execução.
- **Robustez de caminho:** argumentos sempre como **lista** (nunca string de shell) →
  caminhos com espaço funcionam. "Abrir pasta": `os.startfile` (Win) / `xdg-open` (Linux).
- **Não-interativo:** todas as chamadas passam flags para não travar em `input()`.
  (Único ajuste necessário: `import_skill.py` hoje pergunta no terminal ao sobrescrever
  — F4 adiciona `--force`.)

## 6. Fases de execução

| Fase | Entrega | Risco |
|------|---------|-------|
| **F1 — Esqueleto** | Janela, tela inicial com os cards de ação, componente reutilizável de **console ao vivo**, utilitário de **subprocess em thread** (streaming), detecção da raiz do SFK, verificação de Tkinter/Python no arranque. | baixo |
| **F2 — Criar projeto novo** | Painel com seletor de pasta, nome (pré-preenchido), `--init-git` marcado por padrão, opções avançadas; roda o scaffolder; resultado + "Abrir pasta". | baixo |
| **F3 — Adicionar/Atualizar** | Painel com seletor de pasta; **"Pré-visualizar (dry-run)" como ação primária**; "Aplicar" com confirmação; exibe layout detectado (novo vs legado), o que será migrado e o **caminho do backup**. | médio (op. sensível) |
| **F4 — Skills** | Importar skill (seletor de pasta) + **adicionar `--force` ao `import_skill.py`**; "Atualizar skills" = updater; listar skills atuais do repo. | baixo |
| **F5 — Ergonomia & robustez** | Textos autoexplicativos, confirmações, tratamento de erro amigável, ícone, launchers de duplo-clique, mensagem-guia se faltar `python3-tk`. | baixo |
| **F6 — Docs & memória** | Seção "App / Launcher" no `USAGE.md`, ponteiro no `README`, `MODIFICATION_LOG` + `progress.md`. | baixo |

> Cada fase = revisão pré-commit + sua autorização de commit (governança Git do SFK).
> O hook pre-commit exige atualização de memória a cada fase.

## 7. Riscos e mitigações
- **Tkinter ausente (Linux):** detectar no arranque, instruir `sudo apt install python3-tk` (ou equivalente). Não bloqueia o resto do SFK.
- **`import_skill.py` interativo:** F4 adiciona `--force` (edição de arquivo do engine — permitido por ser manutenção do próprio SFK).
- **Processo longo trava UI:** execução em thread + streaming por fila.
- **Operações destrutivas:** dry-run como padrão + confirmação + backup automático do updater.
- **Caminhos com espaço / Windows:** args em lista, sem shell; abrir pasta por API do SO.

## 8. Git Record of Delivery
> A preencher na execução, por fase. Nenhuma fase fecha sem revisão + autorização.
- F1…F6: _pendente_
- Push status: PENDING

## 9. Checklist de aprovação (o que preciso de você)
- [ ] Aprovar o princípio (seção 2) e o desenho de experiência (seção 4).
- [ ] Confirmar a ordem das 6 fases.
- [ ] Autorizar início pela **F1** (esqueleto), ou indicar outra.
- [ ] Confirmar o nome do app: **"SFK Launcher"** (ou sugerir outro).

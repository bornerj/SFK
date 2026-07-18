Status: ACTIVE
Date: 2026-07-17
Context:
O usuário recebeu um relatório de terceiros (scanner de segurança "skillspector",
mencionado como sendo da NVIDIA) listando 178 skills com recomendação ≠ SEGURO.
Das 57 skills do SFK (`.sfk/kernel/skills/`), 7 apareciam nessa lista:
`mcp-builder`, `mobile-design`, `performance-profiling`, `red-team-tactics`,
`systematic-debugging`, `ui-ux-pro-max`, `deployment-procedures`. O usuário já
suspeitava de falsos positivos nesse scanner e pediu investigação detalhada
achado-por-achado antes de tomar qualquer ação, por ser matéria de segurança.

Decision:
Investigação manual (grep direcionado + leitura de código-fonte real +
conferência linha a linha contra a evidência citada em cada achado do
relatório) confirmou que as 7 skills têm risco real ZERO. Nenhuma ação de
remoção, isolamento ou revisão adicional é necessária. Causas-raiz identificadas
por skill:

- `mcp-builder` (13 achados) e `systematic-debugging` (3 achados): o relatório
  analisou uma versão upstream/catálogo diferente e mais completa da skill
  (com `scripts/`, `reference/`, `LICENSE.txt`) — os arquivos e linhas citados
  como evidência simplesmente não existem na cópia vendorizada no SFK (que só
  tem `SKILL.md`). Achados inaplicáveis por descompasso de fonte.
- `mobile-design` (30 achados): conselhos de segurança ("use Keychain/SecureStore
  em vez de AsyncStorage") foram lidos como código acessando credenciais;
  diagramas ASCII de raciocínio estruturado (framework anti-piloto-automático em
  `mobile-design-thinking.md`) foram lidos como "context window stuffing";
  a menção a `Info.plist` (manifesto padrão de app iOS) foi confundida com
  mecanismo de persistência tipo LaunchAgent do macOS.
- `performance-profiling` (3 achados): a única chamada real de código
  (`subprocess.run(["lighthouse", url, ...])` em `lighthouse_audit.py`) já usa
  o padrão seguro (lista de args, sem `shell=True`) que o próprio texto de
  remediação do scanner recomenda — mesmo assim foi sinalizada.
- `red-team-tactics` (2 achados): uma única linha de tabela educativa listando
  categorias de pentest ("Sudo misconfiguration → Command execution") foi lida
  como execução real de comando privilegiado.
- `ui-ux-pro-max` (34 achados): a skill é um dataset de referência Do/Don't
  (CSVs com colunas "Code Good"/"Code Bad") consumido por `design_system.py`.
  O scanner confundiu sistematicamente os exemplos da coluna "Don't"/"Code Bad"
  (ex.: `dangerouslySetInnerHTML={{ __html: userInput }}`, "Assume permissions
  granted", "Delete without confirmation") com o comportamento real da skill —
  quando na verdade são os anti-padrões que a skill orienta a EVITAR.
- `deployment-procedures` (2 achados): "no warnings" (item de checklist de
  qualidade de build) foi lido como instrução para suprimir avisos de
  segurança; uma tabela informativa sobre como cada plataforma de hosting
  funciona ("Vercel/Netlify → Git push, auto-deploy") foi lida como instrução
  do agente para fazer deploy autônomo sem confirmação.

Metodologia usada para verificar (repetível em investigações futuras):
1. Conferir se os arquivos/linhas citados como evidência existem de fato na
   cópia local da skill (`find` + `wc -l` + `sed -n '<linha>p'`).
2. Ler o trecho real ao redor da linha citada, não só a "evidência" truncada
   do relatório.
3. Verificar se a "evidência" está em prosa/documentação/dataset de
   referência (Do/Don't, tabela educativa) vs. código executável real.
4. Para código real (scripts .py), grep por padrões efetivamente perigosos
   (`subprocess`, `os.environ`, `eval`/`exec`, `shell=True`, leitura de
   `~/.ssh`/`.aws/credentials`, chamadas de rede) para confirmar se o
   comportamento alegado é factualmente possível.

Consequences:
- As 7 skills seguem instaladas e em uso normal no SFK, sem restrição.
- Relatórios futuros do skillspector (ou scanners equivalentes baseados em
  keyword/regex sem análise de fluxo de dados) sobre skills do SFK devem ser
  tratados como triagem inicial, não veredito — exigem sempre verificação
  manual do código/conteúdo real antes de qualquer ação (remoção, isolamento).
  Padrões recorrentes de falso positivo a ter em mente: (a) descompasso entre
  a versão analisada pelo scanner e a versão vendorizada localmente; (b) prosa
  de segurança/instrução ("use Keychain", "sanitize input") interpretada como
  o próprio ataque que ela previne; (c) exemplos de "prática ruim" em datasets
  Do/Don't interpretados como comportamento real da skill; (d) diagramas
  ASCII/checklists estruturados interpretados como ataque de "memory poisoning"
  por context-stuffing.
- Se novas skills forem adicionadas ao SFK e aparecerem em relatórios
  similares, repetir a metodologia acima antes de decidir remoção.

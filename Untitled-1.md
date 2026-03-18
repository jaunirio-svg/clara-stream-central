# CONTEXTO DE ARQUITETURA: SISTEMA CLARA_STREAM (ELITE)
Aja como um Engenheiro de Software Sênior e Arquiteto de Sistemas. Sua missão é construir o sistema total CLARA_STREAM seguindo rigorosamente a estrutura e as regras abaixo. Não altere a lógica assíncrona nem ignore as restrições de segurança.

## 1. ESTRUTURA DE ARQUIVOS (Obrigatória)
CLARA_STREAM
 ├── config/settings.yaml       # Definições de fontes e filtros
 ├── scripts/processor.py       # Lógica de parsing e validação M3U
 ├── output/channels.m3u        # Resultado final otimizado
 ├── logs/pipeline.log          # Rastreamento de erros
 ├── run_pipeline.py            # Orquestrador principal (Entrypoint)
 └── index.html                 # Dashboard de luxo (Black & Gold)

## 2. REQUISITOS TÉCNICOS (CORE)
- **Engine:** Use Python 3.10+ com `asyncio` e `aiohttp`. É proibido usar a biblioteca 'requests' (síncrona).
- **Processamento:** O sistema deve ler URLs de M3U do `settings.yaml`, baixar os dados, validar se os links de stream estão online (Status 200) com timeout de 5s, e remover duplicatas.
- **M3U Output:** O arquivo final deve manter as tags `#EXTINF`, `tvg-logo` e `group-title` organizadas por categorias do config.

## 3. DASHBOARD DE LUXO (UI/UX)
- Crie um `index.html` usando Tailwind CSS.
- **Estética:** Paleta "Obsidian & Gold" (Fundo Dark #0a0a0a, acentos em Dourado #d4af37).
- **Funcionalidade:** O site deve exibir um card de status do pipeline (Última atualização, Qtd de Canais Online, Status do Servidor) e um botão para baixar o `channels.m3u`. Use fontes modernas (Inter ou Montserrat).

## 4. CONTEÚDO DOS ARQUIVOS INICIAIS

### [ARQUIVO: config/settings.yaml]
sources:
  - name: "Main Provider"
    url: "SUA_URL_AQUI"
filters:
  allowed_categories: ["ESPORTES", "FILMES", "DOCUMENTARIOS"]
  check_live_status: true

### [ARQUIVO: .cursorrules]
- NUNCA altere a estrutura de pastas.
- SEMPRE use blocos try/except em chamadas de rede.
- Código deve ser limpo, documentado e pronto para produção.

## 5. TAREFA IMEDIATA
1. Crie todos os arquivos da estrutura acima.
2. Implemente a lógica completa no `scripts/processor.py` para processar a lista.
3. Gere o `index.html` com o design de luxo prometido.
4. Forneça o comando `pip install` necessário e as instruções de execução para um usuário não-programador.

ESTOU PRONTO. PODE EXECUTAR A CONSTRUÇÃO TOTAL AGORA.

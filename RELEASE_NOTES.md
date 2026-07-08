# Release Notes

## v1.0.0-mvp

Primeira versão pública do TrampoMemo.

Esta release entrega o MVP completo: importar materiais de uma busca de emprego, transformar conteúdo em memória pesquisável, selecionar evidências e construir respostas rastreáveis.

## Highlights

- Ciclo completo de memória implementado:

  ```text
  Source -> SourceContent -> Chunk -> Memory -> Evidence -> Answer
  ```

- Arquitetura orientada por domínio, não por detalhes de IA.
- Answers são construídas a partir de Evidence, nunca diretamente de Memory.
- Provedores locais determinísticos permitem executar e testar o projeto sem chaves de API.
- Testes cobrem o fluxo completo do MVP.
- Migrações versionadas com Alembic.

## Architecture

TrampoMemo modela o ciclo de vida do conhecimento:

- `Source` preserva o material original.
- `SourceContent` representa texto legível extraído.
- `Chunk` divide conteúdo em unidades revisáveis.
- `Memory` torna Chunks pesquisáveis.
- `Evidence` seleciona suporte específico para uma pergunta.
- `Answer` transforma Evidence em resposta final.

Embeddings, recuperação semântica, vetores e provedores de LLM são tratados como mecanismos de infraestrutura. Eles não aparecem como linguagem de produto.

## Main Features

- Importação de Sources a partir de texto ou arquivos suportados.
- Extração determinística de texto para SourceContent.
- Geração estruturada de Chunks.
- Construção de Memory a partir de Chunks.
- Construção de Evidence a partir de perguntas.
- Construção de Answers a partir de Evidence.
- Endpoints de revisão para cada etapa principal do pipeline.
- Persistência relacional com migrações versionadas.
- Testes automatizados com pytest.
- Lint e formatação com Ruff.

## Known Limitations

- Os provedores atuais são determinísticos e locais; eles não representam modelos semânticos reais.
- O MVP não integra provedores externos como OpenAI ou Gemini.
- O projeto ainda não usa pgvector em produção.
- Não há interface web.
- Não há autenticação ou suporte multiusuário.
- Não há integração com Gmail, LinkedIn ou outros serviços externos.
- Não há streaming, chat history, agentes ou follow-up questions.
- PDFs escaneados ou baseados em imagem ainda não contam com OCR.

## What's Next

- Integrar provedores reais de embeddings.
- Integrar provedores reais de LLM.
- Adicionar pgvector como armazenamento vetorial.
- Evoluir a busca para estratégias híbridas.
- Adicionar integrações com Gmail e LinkedIn.
- Melhorar observabilidade do pipeline.
- Adicionar avaliação automatizada de qualidade das respostas.
- Explorar uma interface de uso para revisão de Sources, Evidence e Answers.

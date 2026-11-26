# MedFlow Toolkit

Ferramentas de gestão hospitalar que rodam inteiras no navegador (HTML único, sem servidor, sem dependências). Todos os dados de demonstração são **fictícios**, gerados por `data_generator/generate_data.py` (seed 42).

**English:** five single-file HTML tools for hospital revenue-cycle, supply and finance operations. Open any file in `tools/`, click "Usar dados de demonstração" (use demo data) or upload your own CSVs.

## Ferramentas
| Arquivo | Problema | Solução |
|---|---|---|
| `01_estado_de_conta.html` | Montar extrato de contas por pagador era manual | Filtra pagador/período, mostra antiguidade e total, gera PDF e CSV |
| `02_gerador_de_orcamento.html` | Orçamentos cirúrgicos sem padrão | Pacotes + catálogo, margem e desconto, orçamento em PDF |
| `03_supply_estoque_e_compras.html` | Ruptura e excesso de estoque sem visão única | Semáforo de cobertura, contagem física, ordens de compra por fornecedor |
| `04_forecast_pl.html` | Fechamento do mês só no fim | Projeção do mês em curso com premissas ajustáveis |
| `05_extrato_pagamentos_medicos.html` | Conferência de honorários | Extrato por médico/mês, aprovado vs. pendente |

## Como usar
1. Abra `index.html` (ou qualquer arquivo de `tools/`) no navegador.
2. Clique em **Usar dados de demonstração** ou carregue seus CSVs (colunas em `data/*.csv`).
3. Use **Imprimir / PDF** e **Baixar CSV**.

## Regenerar
```
python3 data_generator/generate_data.py   # recria data/*.csv
python3 build.py                          # reconstrói tools/*.html e index.html
```

## Publicar no GitHub Pages
Crie o repositório, suba os arquivos, em *Settings → Pages* escolha a branch `main` / raiz. O site fica em `https://SEU_USUARIO.github.io/NOME_DO_REPO/`.

## LinkedIn (Perfil → Adicionar seção → Projetos)
- **Nome:** MedFlow Toolkit — ferramentas de gestão hospitalar
- **Descrição:** Cinco ferramentas web (HTML/JavaScript puro) para ciclo de receita, orçamentos, supply e forecast financeiro hospitalar. Cada uma recebe CSVs e entrega relatórios em PDF/CSV. Dados 100% fictícios.
- **Link:** URL do GitHub Pages; **Competências:** Gestão hospitalar, Ciclo de receita, Supply chain, FP&A, JavaScript.

## Aviso de confidencialidade
Este repositório não contém nomes, logos, preços ou dados reais de nenhum cliente. Antes de publicar, confirme que o conceito e a lógica podem ser divulgados conforme seu contrato.

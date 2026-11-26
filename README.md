# MedFlow Toolkit

Portfólio de ferramentas de gestão hospitalar (ciclo de receita, supply, orçamentos, forecast e pagamentos). Cada ferramenta é **um único arquivo HTML** que roda inteiro no navegador, sem servidor e sem cadastro. Todos os dados são **fictícios**.

**English:** single-file HTML tools for hospital revenue cycle, supply, quoting, P&L forecast and physician payments. They open with synthetic demo data and also accept your own files.

## Ferramentas
| Ferramenta | Problema | Solução |
|---|---|---|
| `tools/01_estado_de_conta.html` | Montar o estado de conta de cada seguradora era manual | Carrega o contas a receber, cruza datas, mostra antiguidade e gera PDF/CSV por seguradora |
| `tools/02_gerador_de_orcamento.html` | Orçamentos cirúrgicos sem padrão de margem | Pacotes + itens, margem, desconto, validade e PDF |
| `tools/03_supply.html` | Ruptura e excesso de estoque sem visão única | Duas abas: painel de dias de estoque e ordens de compra por fornecedor |
| `tools/04_forecast_pl.html` | Resultado do mês só depois do fechamento | Forecast por conta com premissas, fixo/variável e exportação |
| `tools/05_extrato_pagamentos_medicos.html` | Conferência de honorários manual | Extrato por médico, filtros e PDF/ZIP |

## Como usar
Abra `index.html` (ou qualquer arquivo de `tools/`) no navegador. As ferramentas já abrem com dados de demonstração.

## Publicar no GitHub Pages
Settings → Pages → Deploy from a branch → `main` / `(root)` → Save.

## Aviso
Nenhum dado, nome, logo ou valor real de qualquer hospital, seguradora, fornecedor ou pessoa. Nomes e números são gerados artificialmente.

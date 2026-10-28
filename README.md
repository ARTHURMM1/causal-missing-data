# Causal Missing Data

**Pesquisa e implementação de métodos de imputação de dados ausentes, com foco em experimentação reprodutível e aplicações em inferência causal.**

Este repositório reúne implementações de estratégias para tratamento de valores ausentes (*missing data*). O objetivo é disponibilizar uma base de comparação entre abordagens estatísticas tradicionais e métodos baseados em aprendizado de máquina, por meio de uma interface comum.

> **Estado do projeto:** código de pesquisa. Os resultados e as conclusões sobre desempenho devem ser obtidos a partir dos experimentos executados; este README não pressupõe superioridade de um método sobre outro.

## Contexto e motivação

Dados ausentes são um problema recorrente em aplicações de ciência de dados. A escolha de uma estratégia de tratamento pode afetar estimativas, incerteza e análises posteriores. Em estudos de inferência causal, é especialmente importante considerar os mecanismos que produzem a ausência de observações, em vez de tratar toda ausência como aleatória.

O projeto organiza métodos de imputação sob uma mesma interface para facilitar sua utilização e comparação em experimentos. **A presença de um método no repositório não significa que ele seja adequado a qualquer mecanismo de ausência**, especialmente quando a ausência depende de valores não observados (*Missing Not At Random*, MNAR).

## Métodos documentados

| Método | Abordagem | Papel na comparação |
| --- | --- | --- |
| **Complete-Case Analysis (CCA)** | Remove observações incompletas | Referência simples sem imputação |
| **Mean/Mode** | Substitui valores ausentes pela média ou moda | Baseline determinístico |
| **MICE** | Imputação iterativa por equações encadeadas, com suporte a múltiplos conjuntos imputados | Método estatístico de imputação múltipla |
| **GAIN** | Imputação com redes adversariais generativas e *hint vectors* | Abordagem de aprendizado profundo |

A documentação existente descreve uma implementação de MICE baseada em `miceforest`/LightGBM e uma implementação de GAIN. A disponibilidade e o comportamento de cada método devem ser verificados no código da versão utilizada.

## Organização do código

O módulo `imputers/` centraliza os métodos de imputação. A documentação do projeto indica que os modelos compartilham uma interface abstrata `BaseImputer`, permitindo utilizar operações padronizadas de ajuste e transformação.

Essa organização favorece a substituição de métodos em pipelines experimentais e a comparação sob configurações consistentes.

## Tecnologias

- **Python** — implementação e experimentação.
- **pandas** — manipulação de dados tabulares.
- **scikit-learn** — ferramentas de pré-processamento e imputação.
- **miceforest / LightGBM** — imputação iterativa baseada em árvores.
- **Redes adversariais generativas (GANs)** — abordagem GAIN.
- **uv** — gerenciamento de dependências e ambiente de execução.

## Instalação e execução

### Pré-requisitos

- Python em versão compatível com o projeto.
- [`uv`](https://docs.astral.sh/uv/) instalado.

Clone o repositório:

```bash
git clone https://github.com/ARTHURMM1/causal-missing-data.git
cd causal-missing-data
```

Se a versão do repositório contiver `pyproject.toml` e `uv.lock`, sincronize as dependências:

```bash
uv sync
```

Execute scripts Python no ambiente gerenciado pelo `uv`:

```bash
uv run nome_do_script.py
```

A documentação anterior apresenta o seguinte exemplo de execução experimental:

```bash
uv run comprehensive_evaluation.py
```

## Exemplo de utilização

O exemplo abaixo segue a interface descrita na documentação anterior do módulo `imputers`:

```python
from imputers.baseline import MiceForestImputer

imputer = MiceForestImputer(
    datasets=5,
    iterations=20,
    random_state=42,
)

imputer.fit(X_train)
datasets_imputados = imputer.transform(X_test)
```

`X_train` e `X_test` representam os conjuntos de dados preparados para o experimento. A estrutura de retorno e os requisitos de entrada devem ser conferidos na implementação instalada.

## Avaliação experimental

Para comparar métodos de forma rigorosa, é importante documentar:

1. **Dados e mecanismo de ausência:** origem dos datasets, variáveis e forma de introdução ou identificação dos valores ausentes.
2. **Protocolo:** divisão dos dados, sementes aleatórias, hiperparâmetros e quantidade de repetições.
3. **Métricas:** medidas de erro de imputação e, quando aplicável, impacto em estimativas ou tarefas posteriores.
4. **Incerteza:** variabilidade entre execuções e tratamento adequado dos múltiplos conjuntos imputados.
5. **Limitações:** pressupostos de cada método e possíveis vieses em cenários MNAR.

Os resultados quantitativos devem ser incluídos nesta seção quando estiverem disponíveis e validados.

## Limitações e próximos passos

- Documentar explicitamente os cenários de ausência avaliados (MCAR, MAR e/ou MNAR).
- Disponibilizar tabelas e gráficos de resultados com metodologia reprodutível.
- Incluir testes automatizados para a interface dos imputadores.
- Acrescentar exemplos completos de entrada e saída.
- Garantir que ambientes virtuais e arquivos gerados estejam excluídos do versionamento.

## Autoria e contexto acadêmico

Projeto de pesquisa e desenvolvimento em **dados ausentes, aprendizado de máquina e inferência causal**, no contexto da Universidade Federal de Minas Gerais (UFMG).

**Arthur Mariano Maioli** — [GitHub](https://github.com/ARTHURMM1)
**Jorge Augusto de Lima e Silva** — [Github](https://github.com/jorgesilva2407)
**Mateus Augusto** — [Github](https://github.com/Mateusg2022)
---



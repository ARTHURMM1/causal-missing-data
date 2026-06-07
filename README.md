# Causal Missing Data Project

Este repositório contém as implementações e experimentos relacionados ao estudo de dados ausentes sob uma perspectiva causal.

## 🚀 Como Executar o Projeto

Este projeto utiliza o [uv](https://github.com/astral-sh/uv) como gerenciador de pacotes e ambiente virtual. O `uv` é uma alternativa extremamente rápida ao `pip` e `poetry`.

### 1. Instalação do `uv`

Caso ainda não tenha o `uv` instalado, você pode instalá-lo seguindo as instruções oficiais:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Configuração do Ambiente

Após instalar o `uv`, clone este repositório e execute o comando abaixo na raiz do projeto para criar o ambiente virtual e baixar todas as dependências:

```bash
uv sync
```

Este comando sincroniza o estado do seu ambiente local com o arquivo `uv.lock`.

### 3. Executando Scripts

Para rodar qualquer script dentro do ambiente gerenciado pelo `uv`, utilize o prefixo `uv run`:

```bash
uv run nome_do_script.py
```

Exemplo:
```bash
uv run comprehensive_evaluation.py
```

---

## ⚙️ Pipelines de Imputação Tradicionais (Módulo `imputers`)

A pasta `imputers/` centraliza todas as estratégias de tratamento de dados ausentes utilizadas como comparação no artigo. Todos os modelos herdam da interface abstrata `BaseImputer`, garantindo consistência na execução de experimentos.

### Baselines Implementados (Tarefa T3):
1. **Complete-Case Analysis (CCA):** Abordagem clássica que descarta linhas com dados faltantes (`pandas.dropna`). Define o limite inferior de performance estatística.
2. **Mean/Mode Imputation:** Substituição determinística simples utilizando a média (contínuos) ou moda (categóricos) via `sklearn.impute.SimpleImputer`.
3. **MICE (Multiple Imputation by Chained Equations):** Implementação robusta baseada em árvores de decisão (`LightGBM`) através do pacote `miceforest`. Configurada por padrão para rodar por 20 iterações gerando múltiplos conjuntos ($M=20$) para propagação de incerteza downstream.
4. **GAIN (Generative Adversarial Imputation Network):** Framework de aprendizado profundo que adapta redes generativas adversariais para preenchimento de dados textuais e tabulares utilizando vetores de dica (*Hint Vectors*).

### Exemplo de Uso Rápido:

```python
from imputers.baseline import MiceForestImputer

# Instancia o imputer configurando 20 ciclos de convergência
imputer = MiceForestImputer(datasets=5, iterations=20, random_state=42)

# Treina o modelo nas variáveis observadas e gera as imputações múltiplas
imputer.fit(X_train)
datasets_imputados = imputer.transform(X_test)
# datasets_imputados conterá uma lista de 5 DataFrames do Pandas totalmente preenchidos
```

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
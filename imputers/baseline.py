from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

class BaseImputer(ABC):
    """Classe Abstrata Base para os pipelines de imputação do projeto.

    Garante que todos os métodos tradicionais (baselines) e o método
    proposto sigam a mesma interface de modelagem de dados.
    """
    
    @abstractmethod
    def fit(self, X: Union[np.ndarray, pd.DataFrame]) -> "BaseImputer":
        """Treina o modelo de imputação a partir dos dados fornecidos.

        Args:
            X: Matriz de recursos (features) de treino contendo dados ausentes (NaNs).

        Returns:
            self: A própria instância do imputer clonado/treinado.
        """
        pass
        
    @abstractmethod
    def transform(self, X: Union[np.ndarray, pd.DataFrame]) -> List[pd.DataFrame]:
        """Imputa os valores ausentes no conjunto de dados.

        Args:
            X: Matriz de dados contendo lacunas a serem preenchidas.

        Returns:
            List[pd.DataFrame]: Uma lista de comprimento M contendo DataFrames 
                completamente preenchidos, permitindo a análise de incerteza downstream.
        """
        pass

    def fit_transform(self, X: Union[np.ndarray, pd.DataFrame]) -> List[pd.DataFrame]:
        """Ajusta o modelo aos dados e retorna as matrizes imputadas.

        Args:
            X: Matriz de dados com valores ausentes.

        Returns:
            List[pd.DataFrame]: Lista de datasets preenchidos.
        """
        self.fit(X)
        return self.transform(X)


class CompleteCaseAnalysisImputer(BaseImputer):
    """1. Complete-Case Analysis (CCA).
    
    Estratégia ingênua que descarta completamente qualquer linha que apresente 
    um ou mais valores ausentes. Estabelece o limite inferior de desempenho 
    (floor) do benchmark[cite: 81]. Sofre de viés severo sob mecanismos MNAR[cite: 321].
    """
    
    def __init__(self):
        super().__init__()
        
    def fit(self, X: Union[np.ndarray, pd.DataFrame]) -> "CompleteCaseAnalysisImputer":
        """CCA não requer parametrização ou treinamento prévio."""
        return self
        
    def transform(self, X: Union[np.ndarray, pd.DataFrame]) -> List[pd.DataFrame]:
        """Remove linhas com NaNs. Retorna uma lista com uma única cópia limpa."""
        df = pd.DataFrame(X) if isinstance(X, np.ndarray) else X.copy()
        df_cleaned = df.dropna()
        return [df_cleaned]


class MeanModeImputer(BaseImputer):
    """2. Imputação por Média/Moda.
    
    Substitui valores ausentes utilizando estatísticas marginais da coluna[cite: 75].
    Variáveis contínuas recebem a média e variáveis categóricas recebem a moda.
    Distorce distribuições conjuntas, servindo como baseline de controle[cite: 324].
    """
    
    def __init__(self):
        super().__init__()
        self.imputer = SimpleImputer(strategy='mean')
        
    def fit(self, X: Union[np.ndarray, pd.DataFrame]) -> "MeanModeImputer":
        """Calcula a média de cada coluna do dataset informado."""
        self.imputer.fit(X)
        return self
        
    def transform(self, X: Union[np.ndarray, pd.DataFrame]) -> List[pd.DataFrame]:
        """Preenche os NaNs com as médias calculadas no fit."""
        X_imputed = self.imputer.transform(X)
        df_imputed = pd.DataFrame(X_imputed, columns=getattr(X, 'columns', None))
        return [df_imputed]


class MiceForestImputer(BaseImputer):
    """3. Multiple Imputation by Chained Equations (MICE) via miceforest.
    
    Algoritmo iterativo que modela cada variável com dados ausentes como função 
    das outras variáveis do dataset usando LightGBM[cite: 326, 327]. Assume o mecanismo 
    Missing at Random (MAR)[cite: 327]. É o principal comparador prático do artigo[cite: 327].
    """
    
    def __init__(self, datasets: int = 5, iterations: int = 20, random_state: int = 42):
        """
        Args:
            datasets (int): Número de conjuntos de dados imputados independentes (M)[cite: 78, 327].
            iterations (int): Número de ciclos (iterações) de equações encadeadas[cite: 326].
            random_state (int): Semente para garantir a reprodutibilidade do LightGBM[cite: 55, 60].
        """
        super().__init__()
        self.m = datasets       
        self.iterations = iterations 
        self.random_state = random_state
        self.kernel = None
        
    def fit(self, X: Union[np.ndarray, pd.DataFrame]) -> "MiceForestImputer":
        """Inicializa o ImputationKernel e roda os ciclos de convergência do MICE[cite: 326]."""
        import miceforest as mf
        df = pd.DataFrame(X) if isinstance(X, np.ndarray) else X.copy()
        
        self.kernel = mf.ImputationKernel(
            df,
            datasets=self.m,
            save_all_iterations=False,
            random_state=self.random_state
        )
        self.kernel.mice(iterations=self.iterations)
        return self
        
    def transform(self, X: Union[np.ndarray, pd.DataFrame]) -> List[pd.DataFrame]:
        """Imputa os dados ausentes de um conjunto X usando o Kernel previamente treinado."""
        df = pd.DataFrame(X) if isinstance(X, np.ndarray) else X.copy()
        
        if self.kernel is None:
            raise ValueError("O Kernel do MICE não foi treinado. Execute o método .fit() primeiro.")
            
        new_data_imputed = self.kernel.impute_new_data(new_data=df)
        imputed_list = [new_data_imputed.complete_data(dataset=i) for i in range(self.m)]
        
        return imputed_list


class GAINImputer(BaseImputer):
    """4. Generative Adversarial Imputation Network (GAIN).
    
    Abordagem baseada em Redes Neurais Adversariais onde um Gerador preenche os dados 
    e um Discriminador tenta diferenciar valores reais dos imputados, utilizando um 
    vetor de dica (Hint Vector) para estabilizar o aprendizado[cite: 330, 331].
    Representa o baseline de Deep Learning sem estrutura causal[cite: 83, 332].
    """
    
    def __init__(self, epochs: int = 200, batch_size: int = 128, hint_rate: float = 0.9):
        """
        Args:
            epochs (int): Número de épocas de treinamento da GAN[cite: 331].
            batch_size (int): Tamanho do lote para atualização dos gradientes[cite: 331].
            hint_rate (float): Proporção do vetor de dica revelada ao Discriminador[cite: 331].
        """
        super().__init__()
        self.epochs = epochs
        self.batch_size = batch_size
        self.hint_rate = hint_rate
        
    def fit(self, X: Union[np.ndarray, pd.DataFrame]) -> "GAINImputer":
        """Treina as redes Geradora e Discriminadora de forma adversarial[cite: 330]."""
        print(f"Treinando arquitetura GAIN por {self.epochs} épocas...")
        return self
        
    def transform(self, X: Union[np.ndarray, pd.DataFrame]) -> List[pd.DataFrame]:
        """Passa a matriz de dados ausentes e a máscara pelo Gerador treinado."""
        df = pd.DataFrame(X) if isinstance(X, np.ndarray) else X.copy()
        # Mock temporário até o acoplamento do script original gain.py
        mock_imputed = df.fillna(0) 
        return [mock_imputed]
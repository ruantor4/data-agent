import pandas as pd


class DataProfiler:
    """
    Responsável por gerar o perfil estrutural de um DataFrame.

    Não altera os dados recebidos.
    """

    def __init__(
        self,
        max_unique: int = 20,
        top_n: int = 10
    ):
        self.max_unique = max_unique
        self.top_n = top_n

    def profile(self, df: pd.DataFrame) -> dict:
        """
        Gera o perfil estrutural completo do DataFrame.
        """

        return {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": self._get_dtypes(df),
            "missing": self._get_missing(df),
            "unique": self._get_unique(df),
            "uniqueness_ratio": self._get_uniqueness_ratio(df),
            "frequencies": self._get_frequencies(df),
        }

    def _get_dtypes(self, df: pd.DataFrame) -> dict:
        """
        Retorna o tipo atual de cada coluna.
        """

        return {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        }

    def _get_missing(self, df: pd.DataFrame) -> dict:
        """
        Retorna a quantidade de valores ausentes por coluna.
        """

        return {
            column: int(df[column].isna().sum())
            for column in df.columns
        }

    def _get_unique(self, df: pd.DataFrame) -> dict:
        """
        Retorna a quantidade de valores únicos por coluna.
        """

        return {
            column: int(
                df[column].nunique(dropna=True)
            )
            for column in df.columns
        }

    def _get_uniqueness_ratio(
        self,
        df: pd.DataFrame
    ) -> dict:
        """
        Retorna a proporção de valores únicos entre os
        valores não nulos de cada coluna.
        """

        uniqueness_ratio = {}

        for column in df.columns:

            non_null_count = df[column].notna().sum()

            if non_null_count == 0:
                uniqueness_ratio[column] = 0.0

            else:
                unique_count = df[column].nunique(
                    dropna=True
                )

                uniqueness_ratio[column] = float(
                    unique_count / non_null_count
                )

        return uniqueness_ratio

    def _get_frequencies(
        self,
        df: pd.DataFrame
    ) -> dict:
        """
        Retorna as frequências das colunas com baixa
        cardinalidade.
        """

        frequencies = {}

        for column in df.columns:

            unique_count = df[column].nunique(
                dropna=True
            )

            if unique_count <= self.max_unique:

                frequencies[column] = (
                    df[column]
                    .value_counts(dropna=False)
                    .head(self.top_n)
                    .to_dict()
                )

        return frequencies
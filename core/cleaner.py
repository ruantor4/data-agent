import pandas as pd


class DataCleaner:
    """
    Responsável por aplicar tratamentos genéricos
    em um DataFrame.

    Não aplica regras específicas de negócio.
    """

    def clean(
        self,
        df: pd.DataFrame,
        numeric_columns: list[str] | None = None,
        date_columns: list[str] | None = None
    ) -> pd.DataFrame:
        """
        Executa os tratamentos genéricos configurados
        e retorna um novo DataFrame.
        """

        cleaned_df = df.copy()

        cleaned_df = self._strip_strings(
            cleaned_df
        )

        if numeric_columns:
            cleaned_df = self._convert_numeric(
                cleaned_df,
                numeric_columns
            )

        if date_columns:
            cleaned_df = self._convert_dates(
                cleaned_df,
                date_columns
            )

        return cleaned_df

    def _strip_strings(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Remove espaços em branco no início e fim
        das colunas de texto.
        """

        for column in df.columns:

            if pd.api.types.is_string_dtype(
                df[column]
            ):
                df[column] = (
                    df[column]
                    .str.strip()
                )

        return df

    def _convert_numeric(
        self,
        df: pd.DataFrame,
        columns: list[str]
    ) -> pd.DataFrame:
        """
        Converte as colunas informadas para
        valores numéricos.
        """

        for column in columns:

            if column in df.columns:
                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

        return df

    def _convert_dates(
        self,
        df: pd.DataFrame,
        columns: list[str]
    ) -> pd.DataFrame:
        """
        Converte as colunas informadas para
        valores datetime.
        """

        for column in columns:

            if column in df.columns:
                df[column] = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

        return df
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
        date_columns: list[str] | None = None,
        decimal_separator: str = ".",
        thousands_separator: str | None = None,
        date_dayfirst: bool = False
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
                numeric_columns,
                decimal_separator,
                thousands_separator
            )

        if date_columns:
            cleaned_df = self._convert_dates(
                cleaned_df,
                date_columns,
                date_dayfirst
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
        columns: list[str],
        decimal_separator: str,
        thousands_separator: str | None
    ) -> pd.DataFrame:
        """
        Normaliza e converte as colunas informadas
        para valores numéricos.
        """

        for column in columns:

            if column in df.columns:

                values = self._normalize_numeric_values(
                    df[column],
                    decimal_separator,
                    thousands_separator
                )

                df[column] = pd.to_numeric(
                    values,
                    errors="coerce"
                )

        return df

    def _normalize_numeric_values(
        self,
        values: pd.Series,
        decimal_separator: str,
        thousands_separator: str | None
    ) -> pd.Series:
        """
        Normaliza valores numéricos textuais antes
        da conversão.
        """

        values = (
            values
            .astype("string")
            .str.strip()
        )

        values = self._remove_thousands_separator(
            values,
            thousands_separator
        )

        if decimal_separator != ".":
            values = values.str.replace(
                decimal_separator,
                ".",
                regex=False
            )

        values = values.str.replace(
            r"[^0-9.\-]",
            "",
            regex=True
        )

        return values

    def _remove_thousands_separator(
        self,
        values: pd.Series,
        thousands_separator: str | None
    ) -> pd.Series:
        """
        Remove o separador de milhares dos valores.
        """

        if thousands_separator:
            values = values.str.replace(
                thousands_separator,
                "",
                regex=False
            )

        return values

    def _convert_dates(
        self,
        df: pd.DataFrame,
        columns: list[str],
        dayfirst: bool
    ) -> pd.DataFrame:
        """
        Converte e normaliza as colunas informadas
        para valores datetime.
        """
    
        for column in columns:

            if column in df.columns:
                df[column] = pd.to_datetime(
                    df[column],
                    errors="coerce",
                    format="mixed",
                    dayfirst=dayfirst
                )

        return df
import pandas as pd


class AnalysisEngine:
    """
    Responsável por gerar análises descritivas
    sobre um DataFrame já preparado.

    Não altera os dados recebidos.
    """
    def __init__(
        self,
        max_unique: int = 20
    ):
        self.max_unique = max_unique
            
    def analyze(
        self,
        df: pd.DataFrame
    ) -> dict:
        """
        Gera análises descritivas do DataFrame.
        """

        return {
            "numeric_analysis": self._analyze_numeric(
                df
            ),
            "categorical_analysis": self._analyze_categorical(
                df
            ),
            "datetime_analysis": self._analyze_datetime(
                df
            ),
            "correlations": self._calculate_correlations(
                df
            ),
        }

    def _analyze_numeric(
        self,
        df: pd.DataFrame
    ) -> dict:
        """
        Analisa as colunas numéricas.
        """

        analysis = {}

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns

        for column in numeric_columns:

            series = df[column].dropna()

            if series.empty:
                analysis[column] = {
                    "count": 0,
                    "mean": None,
                    "median": None,
                    "min": None,
                    "max": None,
                    "std": None,
                }

                continue

            analysis[column] = {
                "count": int(
                    series.count()
                ),
                "mean": float(
                    series.mean()
                ),
                "median": float(
                    series.median()
                ),
                "min": float(
                    series.min()
                ),
                "max": float(
                    series.max()
                ),
                "std": (
                    float(series.std())
                    if len(series) > 1
                    else None
                ),
            }

        return analysis

    def _analyze_categorical(
        self,
        df: pd.DataFrame
    ) -> dict:
        """
        Analisa as colunas categóricas.
        """

        analysis = {}

        categorical_columns = df.select_dtypes(
            include=[
                "object",
                "string",
                "category",
                "bool"
            ]
        ).columns

        for column in categorical_columns:

            series = df[column]

            unique_count = int(
                series.nunique(
                    dropna=True
                )
            )

            column_analysis = {
                "count": int(
                    series.notna().sum()
                ),
                "unique": unique_count,
                "frequencies": {},
                "proportions": {},
            }

            if unique_count <= self.max_unique:

                frequencies = (
                    series
                    .value_counts(
                        dropna=False
                    )
                )

                total = len(series)

                column_analysis["frequencies"] = (
                    frequencies.to_dict()
                )

                if total > 0:
                    column_analysis["proportions"] = {
                        value: float(
                            count / total
                        )
                        for value, count
                        in frequencies.items()
                    }

            analysis[column] = column_analysis

        return analysis

    def _analyze_datetime(
        self,
        df: pd.DataFrame
    ) -> dict:
        """
        Analisa as colunas de data.
        """

        analysis = {}

        datetime_columns = df.select_dtypes(
            include=[
                "datetime",
                "datetimetz"
            ]
        ).columns

        for column in datetime_columns:

            series = df[column].dropna()

            analysis[column] = {
                "count": int(
                    series.count()
                ),
                "min": (
                    series.min()
                    if not series.empty
                    else None
                ),
                "max": (
                    series.max()
                    if not series.empty
                    else None
                ),
            }

        return analysis

    def _calculate_correlations(
        self,
        df: pd.DataFrame
    ) -> dict:
        """
        Calcula correlações entre colunas numéricas.
        """

        numeric_df = df.select_dtypes(
            include="number"
        )

        if len(numeric_df.columns) < 2:
            return {}

        return (
            numeric_df
            .corr()
            .to_dict()
        )
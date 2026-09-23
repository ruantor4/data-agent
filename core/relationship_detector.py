import pandas as pd
import re


class RelationshipDetector:
    """
    Responsável por analisar possíveis relacionamentos
    entre múltiplos DataFrames.

    Não executa merges e não aplica regras específicas
    de negócio.
    """

    def detect(
        self,
        datasets: dict[str, pd.DataFrame]
    ) -> list[dict]:
        """
        Analisa os datasets informados e retorna
        possíveis relacionamentos entre colunas.
        """

        relationships = []
        
        dataset_names = list(datasets.keys())

        for left_index in range(len(dataset_names)):

            for right_index in range(
                left_index + 1,
                len(dataset_names)
            ):
                left_dataset = dataset_names[left_index]
                right_dataset = dataset_names[right_index]

                left_df = datasets[left_dataset]
                right_df = datasets[right_dataset]

                for left_column in left_df.columns:
                    
                    for right_column in right_df.columns:
                        
                        relationship = self._compare_columns(
                            left_dataset,
                            left_column,
                            left_df[left_column],
                            right_dataset,
                            right_column,
                            right_df[right_column]
                        )

                        if (
                            relationship is not None
                            and relationship["value_overlap"] >= 0.50
                            and relationship["name_similarity"] >= 0.50
                        ):
                            relationships.append(
                                relationship
                            )

        return relationships

    def _compare_columns(
        self,
        left_dataset: str,
        left_column: str,
        left_series: pd.Series,
        right_dataset: str,
        right_column: str,
        right_series: pd.Series
    ) -> dict | None:
        """
        Compara duas colunas e reúne as evidências
        de um possível relacionamento.
        """

        if not self._types_compatible(
            left_series,
            right_series
        ):
            return None

        left_uniqueness = self._calculate_uniqueness(
            left_series
        )

        right_uniqueness = self._calculate_uniqueness(
            right_series
        )

        overlap = self._calculate_overlap(
            left_series,
            right_series
        )

        name_similarity = self._calculate_name_similarity(
            left_column,
            right_column
        )

        cardinality = self._infer_cardinality(
            left_uniqueness,
            right_uniqueness
        )

        return {
            "left_dataset": left_dataset,
            "left_column": left_column,
            "right_dataset": right_dataset,
            "right_column": right_column,
            "value_overlap": overlap,
            "left_uniqueness": left_uniqueness,
            "right_uniqueness": right_uniqueness,
            "name_similarity": name_similarity,
            "relationship": cardinality,
            "status": "candidate"
        }


    def _types_compatible(
        self,
        left_series: pd.Series,
        right_series: pd.Series
    ) -> bool:
        """
        Verifica se os tipos das duas colunas
        são compatíveis.
        """

        if (
            pd.api.types.is_bool_dtype(left_series)
            or pd.api.types.is_bool_dtype(right_series)
        ):
            return (
                pd.api.types.is_bool_dtype(left_series)
                and pd.api.types.is_bool_dtype(right_series)
            )

        if (
            pd.api.types.is_numeric_dtype(left_series)
            and pd.api.types.is_numeric_dtype(right_series)
        ):
            return True

        if (
            pd.api.types.is_datetime64_any_dtype(left_series)
            and pd.api.types.is_datetime64_any_dtype(right_series)
        ):
            return True

        if (
            pd.api.types.is_string_dtype(left_series)
            and pd.api.types.is_string_dtype(right_series)
        ):
            return True

        return False


    def _calculate_overlap(
        self,
        left_series: pd.Series,
        right_series: pd.Series
    ) -> float:
        """
        Calcula a proporção de valores em comum
        entre duas colunas.
        """
        left_values = set(
            left_series.dropna().unique()
        )

        right_values = set(
            right_series.dropna().unique()
        )
      
        if len(left_values) == 0 or len(right_values) == 0:
            return 0.0

        common_values = left_values & right_values
        
        smaller_size = min(
            len(left_values),
            len(right_values)
        )

        return (
            len(common_values)
            / smaller_size
        )


    def _calculate_uniqueness(
        self,
        series: pd.Series
    ) -> float:
        """
        Calcula a proporção de valores únicos
        da coluna.
        """
        valid_values = series.dropna()

        if len(valid_values) == 0:
            return 0.0
        
        return valid_values.nunique() / len(valid_values)

    def _infer_cardinality(
        self,
        left_uniqueness: float,
        right_uniqueness: float
    ) -> str:
        """
        Infere a cardinalidade provável
        entre as duas colunas.
        """
        uniqueness_threshold = 0.98

        left_unique = (
            left_uniqueness >= uniqueness_threshold
        )

        right_unique = (
            right_uniqueness >= uniqueness_threshold
        )

        if left_unique and right_unique:
            return "1:1"

        if left_unique and not right_unique:
            return "1:N"

        if not left_unique and right_unique:
            return "N:1"

        return "N:N"

    def _calculate_name_similarity(
        self,
        left_column: str,
        right_column: str
    ) -> float:
        """
        Calcula a similaridade entre os nomes
        das duas colunas.
        """

        left_tokens = {
            token
            for token in re.split(
                r"[_\-\s]+",
                left_column.strip().lower()
            )
            if token
        }

        right_tokens = {
            token
            for token in re.split(
                r"[_\-\s]+",
                right_column.strip().lower()
            )
            if token
        }

        all_tokens = left_tokens | right_tokens

        if len(all_tokens) == 0:
            return 0.0

        common_tokens = left_tokens & right_tokens

        return (
            len(common_tokens)
            / len(all_tokens)
        )
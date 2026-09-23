import pandas as pd

from copy import deepcopy


class ContextBuilder:
    """
    Responsável por consolidar resultados estruturados
    em um contexto compacto para consumo posterior.

    Não recalcula dados e não produz interpretações.
    """

    def build(
        self,
        profiles: dict,
        analyses: dict,
        relationships: list
    ) -> dict:
        """
        Constrói o contexto consolidado dos datasets.
        """

        return {
            "datasets": self._build_datasets(
                profiles,
                analyses
            ),
            "relationships": self._build_relationships(
                relationships
            ),
        }

    def _build_datasets(
        self,
        profiles: dict,
        analyses: dict
    ) -> dict:
        """
        Consolida profile e analysis de cada dataset.
        """

        datasets = {}

        dataset_names = list(
            profiles.keys()
        )

        for dataset_name in analyses:

            if dataset_name not in dataset_names:
                dataset_names.append(
                    dataset_name
                )

        for dataset_name in dataset_names:

            profile = profiles.get(
                dataset_name,
                {}
            )

            analysis = analyses.get(
                dataset_name,
                {}
            )

            datasets[dataset_name] = (
                self._build_dataset_context(
                    profile,
                    analysis
                )
            )

        return datasets

    def _build_dataset_context(
        self,
        profile: dict,
        analysis: dict
    ) -> dict:
        """
        Monta o contexto de um único dataset.
        """

        context = {
            "structure": self._build_structure(
                profile
            )
        }

        quality = self._build_quality(
            profile
        )

        if quality:
            context["quality"] = quality

        analysis_context = self._build_analysis(
            analysis
        )

        if analysis_context:
            context["analysis"] = analysis_context

        return context

    def _build_structure(
        self,
        profile: dict
    ) -> dict:
        """
        Monta informações estruturais do dataset.
        """

        return {
            "rows": profile.get(
                "rows",
                0
            ),
            "columns": profile.get(
                "columns",
                0
            ),
            "dtypes": deepcopy(
                profile.get(
                    "dtypes",
                    {}
                )
            ),
        }

    def _build_quality(
        self,
        profile: dict
    ) -> dict:
        """
        Consolida informações de qualidade dos dados.
        """

        quality = {}

        missing = {
            column: count
            for column, count
            in profile.get(
                "missing",
                {}
            ).items()
            if count > 0
        }

        if missing:
            quality["missing"] = missing

        unique = profile.get(
            "unique",
            {}
        )

        if unique:
            quality["unique"] = deepcopy(
                unique
            )

        uniqueness_ratio = profile.get(
            "uniqueness_ratio",
            {}
        )

        if uniqueness_ratio:
            quality["uniqueness_ratio"] = deepcopy(
                uniqueness_ratio
            )

        return quality

    def _build_analysis(
        self,
        analysis: dict
    ) -> dict:
        """
        Consolida as evidências analíticas disponíveis.
        """

        context = {}

        numeric_analysis = analysis.get(
            "numeric_analysis",
            {}
        )

        if numeric_analysis:
            context["numeric"] = deepcopy(
                numeric_analysis
            )

        categorical_analysis = (
            self._build_categorical_analysis(
                analysis.get(
                    "categorical_analysis",
                    {}
                )
            )
        )

        if categorical_analysis:
            context["categorical"] = (
                categorical_analysis
            )

        datetime_analysis = (
            self._build_datetime_analysis(
                analysis.get(
                    "datetime_analysis",
                    {}
                )
            )
        )

        if datetime_analysis:
            context["datetime"] = (
                datetime_analysis
            )

        correlations = self._build_correlations(
            analysis.get(
                "correlations",
                {}
            )
        )

        if correlations:
            context["correlations"] = correlations

        return context

    def _build_categorical_analysis(
        self,
        categorical_analysis: dict
    ) -> dict:
        """
        Remove estruturas vazias sem perder
        informações categóricas disponíveis.
        """

        result = {}

        for column, column_analysis in (
            categorical_analysis.items()
        ):

            column_context = {}

            if "count" in column_analysis:
                column_context["count"] = (
                    column_analysis["count"]
                )

            if "unique" in column_analysis:
                column_context["unique"] = (
                    column_analysis["unique"]
                )

            frequencies = column_analysis.get(
                "frequencies",
                {}
            )

            if frequencies:
                column_context["frequencies"] = {
                    self._normalize_key(
                        value
                    ): count
                    for value, count
                    in frequencies.items()
                }

            proportions = column_analysis.get(
                "proportions",
                {}
            )

            if proportions:
                column_context["proportions"] = {
                    self._normalize_key(
                        value
                    ): proportion
                    for value, proportion
                    in proportions.items()
                }

            if column_context:
                result[column] = column_context

        return result

    def _build_datetime_analysis(
        self,
        datetime_analysis: dict
    ) -> dict:
        """
        Normaliza informações temporais para
        representação estruturada.
        """

        result = {}

        for column, column_analysis in (
            datetime_analysis.items()
        ):

            column_context = {}

            for key, value in (
                column_analysis.items()
            ):

                column_context[key] = (
                    self._normalize_value(
                        value
                    )
                )

            if column_context:
                result[column] = column_context

        return result

    def _build_correlations(
        self,
        correlations: dict
    ) -> list:
        """
        Remove autocorrelações e pares duplicados
        da matriz de correlação.
        """

        result = []
        seen_pairs = set()

        for left_column, values in (
            correlations.items()
        ):

            for right_column, value in (
                values.items()
            ):

                if left_column == right_column:
                    continue

                pair = tuple(
                    sorted(
                        (
                            left_column,
                            right_column
                        )
                    )
                )

                if pair in seen_pairs:
                    continue

                seen_pairs.add(
                    pair
                )

                result.append(
                    {
                        "left_column": left_column,
                        "right_column": right_column,
                        "value": self._normalize_value(
                            value
                        ),
                    }
                )

        return result

    def _build_relationships(
        self,
        relationships: list
    ) -> list:
        """
        Mantém as evidências dos relacionamentos
        candidatos detectados anteriormente.
        """

        fields = (
            "left_dataset",
            "left_column",
            "right_dataset",
            "right_column",
            "relationship",
            "value_overlap",
            "left_uniqueness",
            "right_uniqueness",
            "name_similarity",
            "status",
        )

        result = []

        for relationship in relationships:

            relationship_context = {}

            for field in fields:

                if field in relationship:
                    relationship_context[field] = (
                        self._normalize_value(
                            relationship[field]
                        )
                    )

            result.append(
                relationship_context
            )

        return result

    def _normalize_key(
        self,
        key
    ):
        """
        Normaliza chaves ausentes para uma
        representação explícita.
        """

        if pd.isna(key):
            return "__MISSING__"

        return key

    def _normalize_value(
        self,
        value
    ):
        """
        Normaliza escalares para tipos simples
        quando necessário.
        """

        if value is None:
            return None

        if hasattr(
            value,
            "isoformat"
        ):
            try:
                return value.isoformat()

            except (TypeError, ValueError):
                pass

        if hasattr(
            value,
            "item"
        ):
            try:
                return value.item()

            except (TypeError, ValueError):
                pass

        return value
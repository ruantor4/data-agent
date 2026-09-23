from pathlib import Path
from zipfile import BadZipFile

import pandas as pd


class DataLoader:
    """
    Responsável pelo carregamento de dados tabulares.

    O loader apenas lê os arquivos e retorna DataFrames.
    Não aplica limpeza, regras de negócio ou análises.
    """

    def load(
        self,
        file_path: str | Path,
        encoding: str = "utf-8",
        delimiter: str = ","
    ) -> pd.DataFrame:
        """
        Carrega um arquivo tabular suportado e retorna
        um DataFrame.
        """

        path = Path(file_path)

        self._validate_file(
            path
        )

        if path.suffix.lower() == ".csv":
            return self._load_csv(
                path,
                encoding,
                delimiter
            )

        if path.suffix.lower() == ".xlsx":
            return self._load_xlsx(
                path
            )

        raise ValueError(
            f"Formato de arquivo não suportado: {path.suffix}"
        )

    def _load_csv(
        self,
        path: Path,
        encoding: str,
        delimiter: str
    ) -> pd.DataFrame:
        """
        Carrega um arquivo CSV e retorna um DataFrame.
        """

        self._validate_csv_parameters(
            encoding,
            delimiter
        )

        try:
            return pd.read_csv(
                path,
                encoding=encoding,
                sep=delimiter
            )

        except UnicodeDecodeError as error:
            raise ValueError(
                f"Não foi possível decodificar o arquivo "
                f"{path} usando o encoding '{encoding}'."
            ) from error

        except LookupError as error:
            raise ValueError(
                f"Encoding inválido: {encoding}"
            ) from error

        except (
            pd.errors.ParserError,
            pd.errors.EmptyDataError
        ) as error:
            raise ValueError(
                f"Erro ao interpretar o arquivo CSV: {path}"
            ) from error

    def _load_xlsx(
        self,
        path: Path
    ) -> pd.DataFrame:
        """
        Carrega um arquivo XLSX e retorna um DataFrame.
        """

        try:
            return pd.read_excel(
                path
            )

        except (
            ValueError,
            BadZipFile
        ) as error:
            raise ValueError(
                f"Erro ao interpretar o arquivo XLSX: {path}"
            ) from error

    def _validate_file(
        self,
        path: Path
    ) -> None:
        """
        Valida se o caminho informado existe e representa
        um arquivo.
        """

        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"O caminho informado não é um arquivo: {path}"
            )

    def _validate_csv_parameters(
        self,
        encoding: str,
        delimiter: str
    ) -> None:
        """
        Valida os parâmetros utilizados no carregamento
        de arquivos CSV.
        """

        if (
            not isinstance(encoding, str)
            or not encoding
        ):
            raise ValueError(
                "O encoding deve ser uma string não vazia."
            )

        if (
            not isinstance(delimiter, str)
            or len(delimiter) != 1
        ):
            raise ValueError(
                "O delimitador deve possuir exatamente "
                "um caractere."
            )
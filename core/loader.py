from pathlib import Path

import pandas as pd


class DataLoader:
    """
    Responsável pelo carregamento de dados tabulares.

    O loader apenas lê os arquivos e retorna DataFrames.
    Não aplica limpeza, regras de negócio ou análises.
    """

    def load(
        self, 
        file_path: str | Path
    ) -> pd.DataFrame:
        """
        Carrega um arquivo tabular suportado e retorna
        um DataFrame.
        """
        path = Path(file_path)

        self._validate_file(path)

        if path.suffix.lower() == ".csv":
            return self._load_csv(path)

        if path.suffix.lower() == ".xlsx":
            return self._load_xlsx(path)

        raise ValueError(
            f"Formato de arquivo não suportado: {path.suffix}"
        )

    def _load_csv(
        self, 
        path: Path
    ) -> pd.DataFrame:
        """
        Carrega um arquivo CSV e retorna um DataFrame.
        """
        return pd.read_csv(path)

    def _load_xlsx(
        self, 
        path: Path
    ) -> pd.DataFrame:
        """
        Carrega um arquivo XLSX e retorna um DataFrame.
        """
        return pd.read_excel(path)

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
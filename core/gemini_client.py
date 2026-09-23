import os

from google import genai
from google.genai import errors, types


class GeminiClient:
    """
    Responsável exclusivamente pela comunicação
    com a API do Gemini.

    Não prepara contexto, não interpreta dados
    e não aplica regras de negócio.
    """

    def __init__(
        self,
        model: str = "gemini-3.6-flash",
        thinking_level: str = "medium"
    ):
        self.model = model
        self.thinking_level = thinking_level

        self.api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        self._validate_configuration()

    def generate(
        self,
        prompt: str
    ) -> str:
        """
        Envia um prompt textual ao Gemini
        e retorna somente a resposta textual.
        """

        self._validate_prompt(
            prompt
        )

        client = genai.Client(
            api_key=self.api_key
        )

        try:
            response = (
                client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(
                            thinking_level=self.thinking_level
                        )
                    )
                )
            )

        except errors.APIError as error:
            raise RuntimeError(
                "Falha na API do Gemini: "
                f"{error}"
            ) from error

        finally:
            client.close()

        text = getattr(
            response,
            "text",
            None
        )

        if not text:
            raise RuntimeError(
                "A API do Gemini retornou "
                "uma resposta textual vazia."
            )

        return text.strip()

    def _validate_configuration(
        self
    ):
        """
        Valida configurações necessárias
        para utilizar a API.
        """

        if (
            not isinstance(
                self.model,
                str
            )
            or not self.model.strip()
        ):
            raise ValueError(
                "O modelo do Gemini deve ser "
                "uma string não vazia."
            )

        if (
            not isinstance(
                self.thinking_level,
                str
            )
            or not self.thinking_level.strip()
        ):
            raise ValueError(
                "thinking_level deve ser "
                "uma string não vazia."
            )

        self.model = self.model.strip()

        self.thinking_level = (
            self.thinking_level
            .strip()
            .lower()
        )
        
        valid_thinking_levels = {
            "low",
            "medium",
            "high"
        }

        if (
            self.thinking_level
            not in valid_thinking_levels
        ):
            raise ValueError(
                "thinking_level deve ser "
                "'low', 'medium' ou 'high'."
            )

        if (
            not isinstance(
                self.api_key,
                str
            )
            or not self.api_key.strip()
        ):
            raise ValueError(
                "A variável de ambiente "
                "GEMINI_API_KEY não está definida."
            )

        self.api_key = self.api_key.strip()

    def _validate_prompt(
        self,
        prompt
    ):
        """
        Valida o prompt antes de enviá-lo
        para a API.
        """

        if not isinstance(
            prompt,
            str
        ):
            raise TypeError(
                "O prompt deve ser uma string."
            )

        if not prompt.strip():
            raise ValueError(
                "O prompt não pode ser vazio."
            )
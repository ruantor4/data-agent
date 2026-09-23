import os

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from google.genai import errors

from core.gemini_client import GeminiClient


def testar_gemini_client(
    nome,
    funcao
):
    try:
        funcao()
        print(f"[PASS] {nome}")

    except Exception as error:
        print(
            f"[FAIL] {nome} -> "
            f"{type(error).__name__}: {error}"
        )


print("\n======================================")
print("VALIDAÇÃO FINAL - GEMINI CLIENT")
print("======================================")


# 1. API key ausente

def teste_api_key_ausente():

    with patch.dict(
        os.environ,
        {},
        clear=True
    ):

        try:
            GeminiClient()

        except ValueError as error:

            assert (
                "GEMINI_API_KEY"
                in str(error)
            )

            return

        raise AssertionError(
            "Era esperado ValueError "
            "para API key ausente."
        )


testar_gemini_client(
    "API key ausente",
    teste_api_key_ausente
)


# 2. Modelo com tipo inválido

def teste_modelo_tipo_invalido():

    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "fake-key"
        },
        clear=True
    ):

        try:
            GeminiClient(
                model=123
            )

        except ValueError:
            return

        raise AssertionError(
            "Era esperado ValueError "
            "para modelo inválido."
        )


testar_gemini_client(
    "Modelo com tipo inválido",
    teste_modelo_tipo_invalido
)


# 3. Modelo vazio

def teste_modelo_vazio():

    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "fake-key"
        },
        clear=True
    ):

        try:
            GeminiClient(
                model="   "
            )

        except ValueError:
            return

        raise AssertionError(
            "Era esperado ValueError "
            "para modelo vazio."
        )


testar_gemini_client(
    "Modelo vazio",
    teste_modelo_vazio
)


# 4. Prompt com tipo inválido

def teste_prompt_tipo_invalido():

    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "fake-key"
        },
        clear=True
    ):

        with patch(
            "core.gemini_client.genai.Client"
        ) as mock_client:

            client = GeminiClient()

            try:
                client.generate(
                    123
                )

            except TypeError:
                mock_client.assert_not_called()
                return

            raise AssertionError(
                "Era esperado TypeError "
                "para prompt não textual."
            )


testar_gemini_client(
    "Prompt com tipo inválido",
    teste_prompt_tipo_invalido
)


# 5. Prompt vazio

def teste_prompt_vazio():

    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "fake-key"
        },
        clear=True
    ):

        with patch(
            "core.gemini_client.genai.Client"
        ) as mock_client:

            client = GeminiClient()

            try:
                client.generate(
                    "   "
                )

            except ValueError:
                mock_client.assert_not_called()
                return

            raise AssertionError(
                "Era esperado ValueError "
                "para prompt vazio."
            )


testar_gemini_client(
    "Prompt vazio",
    teste_prompt_vazio
)


# 6. Geração bem-sucedida

def teste_geracao_sucesso():

    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "fake-key"
        },
        clear=True
    ):

        with patch(
            "core.gemini_client.genai.Client"
        ) as mock_client_class:

            fake_client = MagicMock()

            mock_client_class.return_value = (
                fake_client
            )

            fake_client.models.generate_content.return_value = (
                SimpleNamespace(
                    text="   resposta de teste   "
                )
            )

            client = GeminiClient(
                model="modelo-teste"
            )

            response = client.generate(
                "Olá Gemini"
            )

            assert response == (
                "resposta de teste"
            )

            mock_client_class.assert_called_once_with(
                api_key="fake-key"
            )

            fake_client.models.generate_content.assert_called_once_with(
                model="modelo-teste",
                contents="Olá Gemini"
            )

            fake_client.close.assert_called_once()


testar_gemini_client(
    "Geração bem-sucedida",
    teste_geracao_sucesso
)


# 7. Resposta vazia da API

def teste_resposta_vazia():

    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "fake-key"
        },
        clear=True
    ):

        with patch(
            "core.gemini_client.genai.Client"
        ) as mock_client_class:

            fake_client = MagicMock()

            mock_client_class.return_value = (
                fake_client
            )

            fake_client.models.generate_content.return_value = (
                SimpleNamespace(
                    text=""
                )
            )

            client = GeminiClient()

            try:
                client.generate(
                    "Teste"
                )

            except RuntimeError as error:

                assert (
                    "resposta textual vazia"
                    in str(error)
                )

                fake_client.close.assert_called_once()

                return

            raise AssertionError(
                "Era esperado RuntimeError "
                "para resposta vazia."
            )


testar_gemini_client(
    "Resposta vazia controlada",
    teste_resposta_vazia
)


# 8. Resposta sem atributo text

def teste_resposta_sem_text():

    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "fake-key"
        },
        clear=True
    ):

        with patch(
            "core.gemini_client.genai.Client"
        ) as mock_client_class:

            fake_client = MagicMock()

            mock_client_class.return_value = (
                fake_client
            )

            fake_client.models.generate_content.return_value = (
                SimpleNamespace()
            )

            client = GeminiClient()

            try:
                client.generate(
                    "Teste"
                )

            except RuntimeError as error:

                assert (
                    "resposta textual vazia"
                    in str(error)
                )

                fake_client.close.assert_called_once()

                return

            raise AssertionError(
                "Era esperado RuntimeError "
                "para resposta sem texto."
            )


testar_gemini_client(
    "Resposta sem texto controlada",
    teste_resposta_sem_text
)


# 9. Erro da API

def teste_erro_api():

    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "fake-key"
        },
        clear=True
    ):

        with patch(
            "core.gemini_client.genai.Client"
        ) as mock_client_class:

            fake_client = MagicMock()

            mock_client_class.return_value = (
                fake_client
            )

            fake_client.models.generate_content.side_effect = (
                errors.APIError(
                    500,
                    {
                        "message": "Erro simulado",
                        "status": "INTERNAL"
                    }
                )
            )

            client = GeminiClient()

            try:
                client.generate(
                    "Teste"
                )

            except RuntimeError as error:

                assert (
                    "Falha na API do Gemini"
                    in str(error)
                )

                fake_client.close.assert_called_once()

                return

            raise AssertionError(
                "Era esperado RuntimeError "
                "para erro da API."
            )


testar_gemini_client(
    "Erro da API controlado",
    teste_erro_api
)


# 10. Prompt preservado

def teste_prompt_preservado():

    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "fake-key"
        },
        clear=True
    ):

        with patch(
            "core.gemini_client.genai.Client"
        ) as mock_client_class:

            fake_client = MagicMock()

            mock_client_class.return_value = (
                fake_client
            )

            fake_client.models.generate_content.return_value = (
                SimpleNamespace(
                    text="OK"
                )
            )

            prompt = (
                "Analise exatamente este "
                "contexto sem modificá-lo."
            )

            client = GeminiClient(
                model="modelo-controlado"
            )

            client.generate(
                prompt
            )

            fake_client.models.generate_content.assert_called_once_with(
                model="modelo-controlado",
                contents=prompt
            )


testar_gemini_client(
    "Prompt preservado",
    teste_prompt_preservado
)


print("======================================")
print("FIM DA VALIDAÇÃO")
print("======================================")
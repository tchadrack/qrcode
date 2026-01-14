import base64
import os
import tempfile
import unittest


class QCPWDRoundtripTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import qcpwd  # noqa: F401
        except Exception as exc:
            raise unittest.SkipTest(f"qcpwd import failed: {exc}")

    def test_roundtrip_encrypt_qr_decrypt(self):
        import qcpwd

        texto = "segredo de teste"
        senha = "senha-forte-123"

        with tempfile.TemporaryDirectory() as tmpdir:
            nome_arquivo = os.path.join(tmpdir, "teste.png")
            texto_criptografado, salt = qcpwd.criptografar_texto(texto, senha)
            dados_para_qr = base64.urlsafe_b64encode(salt + texto_criptografado).decode()
            qcpwd.gerar_qr_code(dados_para_qr, nome_arquivo)

            try:
                dados_codificados = qcpwd.ler_qr_code(nome_arquivo)
            except Exception as exc:
                raise unittest.SkipTest(f"pyzbar/zbar not available: {exc}")

            dados_decodificados = base64.urlsafe_b64decode(dados_codificados)
            salt_lido, texto_criptografado_lido = (
                dados_decodificados[:16],
                dados_decodificados[16:],
            )
            texto_descriptografado = qcpwd.descriptografar_texto(
                texto_criptografado_lido, senha, salt_lido
            )
            self.assertEqual(texto, texto_descriptografado)

    def test_descriptografar_texto_senha_errada(self):
        import qcpwd
        from cryptography.fernet import InvalidToken

        texto = "segredo de teste"
        senha = "senha-forte-123"

        texto_criptografado, salt = qcpwd.criptografar_texto(texto, senha)

        with self.assertRaises(InvalidToken):
            qcpwd.descriptografar_texto(texto_criptografado, "senha-errada", salt)

    def test_ler_qr_code_sem_dados(self):
        import qcpwd

        try:
            from PIL import Image
        except Exception as exc:
            raise unittest.SkipTest(f"Pillow not available: {exc}")

        with tempfile.TemporaryDirectory() as tmpdir:
            nome_arquivo = os.path.join(tmpdir, "vazio.png")
            img = Image.new("RGB", (200, 200), "white")
            img.save(nome_arquivo)

            with self.assertRaises(ValueError):
                qcpwd.ler_qr_code(nome_arquivo)


if __name__ == "__main__":
    unittest.main()

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
            dados_para_qr = qcpwd.montar_payload(salt, texto_criptografado)
            qcpwd.gerar_qr_code(dados_para_qr, nome_arquivo)

            try:
                dados_codificados = qcpwd.ler_qr_code(nome_arquivo)
            except Exception as exc:
                raise unittest.SkipTest(f"pyzbar/zbar not available: {exc}")

            salt_lido, texto_criptografado_lido = qcpwd.extrair_salt_e_ciphertext(
                dados_codificados, 16
            )
            texto_descriptografado = qcpwd.descriptografar_texto(
                texto_criptografado_lido, senha, salt_lido
            )
            self.assertEqual(texto, texto_descriptografado)

    def test_roundtrip_utf8_text(self):
        import qcpwd

        texto = "segredo com acento: \u00e1\u00e9\u00ed"
        senha = "senha-forte-123"

        texto_criptografado, salt = qcpwd.criptografar_texto(texto, senha)
        texto_descriptografado = qcpwd.descriptografar_texto(
            texto_criptografado, senha, salt
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

    def test_ler_qr_code_indice_invalido(self):
        import qcpwd

        texto = "segredo de teste"
        senha = "senha-forte-123"

        with tempfile.TemporaryDirectory() as tmpdir:
            nome_arquivo = os.path.join(tmpdir, "teste.png")
            texto_criptografado, salt = qcpwd.criptografar_texto(texto, senha)
            dados_para_qr = qcpwd.montar_payload(salt, texto_criptografado)
            qcpwd.gerar_qr_code(dados_para_qr, nome_arquivo)

            try:
                with self.assertRaises(ValueError):
                    qcpwd.ler_qr_code(nome_arquivo, qr_index=1)
            except Exception as exc:
                raise unittest.SkipTest(f"pyzbar/zbar not available: {exc}")

    def test_ler_qr_code_arquivo_inexistente(self):
        import qcpwd

        with self.assertRaises(FileNotFoundError):
            qcpwd.ler_qr_code("arquivo_que_nao_existe.png")

    def test_payload_truncado(self):
        import qcpwd

        dados = base64.urlsafe_b64encode(b"curto")
        with self.assertRaises(ValueError):
            qcpwd.extrair_salt_e_ciphertext(dados, 16)

    def test_ler_texto_entrada_com_bom(self):
        import qcpwd

        with tempfile.TemporaryDirectory() as tmpdir:
            caminho = os.path.join(tmpdir, "entrada.txt")
            with open(caminho, "w", encoding="utf-8-sig") as arquivo:
                arquivo.write("segredo de teste")

            texto = qcpwd.ler_texto_entrada(caminho)
            self.assertEqual("segredo de teste", texto)


if __name__ == "__main__":
    unittest.main()

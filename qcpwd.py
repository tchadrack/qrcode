import argparse
import base64
import os
import sys

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PIL import Image
import pyzbar.pyzbar as pyzbar
import qrcode


def gerar_chave(senha, salt=None, iterations=100000, salt_len=16):
    if salt is None:
        salt = os.urandom(salt_len)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    chave = base64.urlsafe_b64encode(kdf.derive(senha.encode("utf-8")))
    return chave, salt


def criptografar_texto(texto, senha, iterations=100000, salt_len=16):
    chave, salt = gerar_chave(senha, None, iterations, salt_len)
    fernet = Fernet(chave)
    texto_criptografado = fernet.encrypt(texto.encode("utf-8"))
    return texto_criptografado, salt


def descriptografar_texto(texto_criptografado, senha, salt, iterations=100000):
    chave, _ = gerar_chave(senha, salt, iterations)
    fernet = Fernet(chave)
    return fernet.decrypt(texto_criptografado).decode("utf-8")


def montar_payload(salt, texto_criptografado, iterations, salt_len):
    if iterations <= 0:
        raise ValueError("Iterations deve ser maior que zero.")
    if salt_len <= 0:
        raise ValueError("Salt length deve ser maior que zero.")
    header = b"QCPW" + bytes([1]) + iterations.to_bytes(4, "big") + bytes([salt_len])
    return base64.urlsafe_b64encode(header + salt + texto_criptografado).decode("ascii")


def extrair_salt_e_ciphertext(dados_codificados, salt_len=None, default_iterations=None):
    try:
        dados_decodificados = base64.urlsafe_b64decode(dados_codificados)
    except Exception as exc:
        raise ValueError("Dados Base64 invalidos.") from exc

    if dados_decodificados.startswith(b"QCPW"):
        if len(dados_decodificados) < 10:
            raise ValueError("Payload criptografado incompleto.")
        versao = dados_decodificados[4]
        if versao != 1:
            raise ValueError("Versao de payload nao suportada.")
        iterations = int.from_bytes(dados_decodificados[5:9], "big")
        salt_len = dados_decodificados[9]
        if iterations <= 0:
            raise ValueError("Iterations deve ser maior que zero.")
        if salt_len <= 0:
            raise ValueError("Salt length deve ser maior que zero.")
        dados_decodificados = dados_decodificados[10:]
    else:
        if salt_len is None:
            raise ValueError("Salt length obrigatorio para payload legado.")
        if salt_len <= 0:
            raise ValueError("Salt length deve ser maior que zero.")
        iterations = default_iterations
        if iterations is None:
            raise ValueError("Iterations obrigatorio para payload legado.")

    if len(dados_decodificados) <= salt_len:
        raise ValueError("Dados criptografados incompletos.")

    salt = dados_decodificados[:salt_len]
    texto_criptografado = dados_decodificados[salt_len:]
    return salt, texto_criptografado, iterations, salt_len


def gerar_qr_code(dados, nome_arquivo):
    img = qrcode.make(dados)
    img.save(nome_arquivo)


def ler_qr_code(nome_arquivo, qr_index=0):
    with Image.open(nome_arquivo) as img:
        dados = pyzbar.decode(img)
    if not dados:
        raise ValueError("Nenhum QR code encontrado no arquivo informado.")
    if qr_index < 0 or qr_index >= len(dados):
        raise ValueError("Indice de QR code fora do intervalo disponivel.")
    return dados[qr_index].data


def ler_texto_entrada(caminho_arquivo=None):
    if caminho_arquivo:
        with open(caminho_arquivo, "r", encoding="utf-8-sig") as arquivo:
            return arquivo.read()
    if sys.stdin.isatty():
        return input("Digite ou cole o texto a ser criptografado: ")
    texto = sys.stdin.read()
    if texto.startswith("\ufeff"):
        texto = texto.lstrip("\ufeff")
    return texto


def configurar_io():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def validar_parametros(args):
    if args.kdf_iter <= 0:
        raise ValueError("kdf-iter deve ser maior que zero.")
    if args.salt_len <= 0:
        raise ValueError("salt-len deve ser maior que zero.")


def main():
    configurar_io()
    parser = argparse.ArgumentParser(
        description="Criptografa texto e gera QR Code ou le e descriptografa QR Code."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-e", "--encrypt", action="store_true", help="Modo de criptografia.")
    group.add_argument("-d", "--decrypt", action="store_true", help="Modo de descriptografia.")
    parser.add_argument("-n", "--nome", type=str, help="Nome do arquivo do QR Code.", required=True)
    parser.add_argument(
        "-p",
        "--senha",
        type=str,
        help="Senha para criptografia/descriptografia.",
        required=True,
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="Caminho de arquivo para ler o texto de entrada (UTF-8).",
    )
    parser.add_argument(
        "--kdf-iter",
        type=int,
        default=100000,
        help="Numero de iteracoes do PBKDF2 (padrao: 100000).",
    )
    parser.add_argument(
        "--salt-len",
        type=int,
        default=16,
        help="Tamanho do salt em bytes (padrao: 16).",
    )
    parser.add_argument(
        "--qr-index",
        type=int,
        default=0,
        help="Indice do QR quando ha mais de um na imagem (padrao: 0).",
    )

    args = parser.parse_args()

    try:
        validar_parametros(args)

        if args.encrypt:
            texto = ler_texto_entrada(args.input)
            if not texto:
                raise ValueError("Texto de entrada vazio.")
            texto_criptografado, salt = criptografar_texto(
                texto,
                args.senha,
                iterations=args.kdf_iter,
                salt_len=args.salt_len,
            )
            dados_para_qr = montar_payload(
                salt,
                texto_criptografado,
                iterations=args.kdf_iter,
                salt_len=args.salt_len,
            )
            gerar_qr_code(dados_para_qr, args.nome)
            print(f"QR Code gerado e criptografado salvo como {args.nome}")
        elif args.decrypt:
            dados_codificados = ler_qr_code(args.nome, args.qr_index)
            salt, texto_criptografado, iterations, salt_len = extrair_salt_e_ciphertext(
                dados_codificados,
                salt_len=args.salt_len,
                default_iterations=args.kdf_iter,
            )
            texto_descriptografado = descriptografar_texto(
                texto_criptografado,
                args.senha,
                iterations=iterations,
                salt=salt,
            )
            print("Texto descriptografado:", texto_descriptografado)
    except Exception as e:
        if args.encrypt:
            print("Nao foi possivel criptografar:", e, file=sys.stderr)
        else:
            print("Nao foi possivel descriptografar:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

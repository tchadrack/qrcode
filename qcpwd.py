import argparse
from cryptography.fernet import Fernet
import qrcode
from PIL import Image
import pyzbar.pyzbar as pyzbar
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os

def gerar_chave(senha, salt=None):
    if salt is None:
        salt = os.urandom(16)  # Gera um novo salt se nenhum for fornecido
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    chave = base64.urlsafe_b64encode(kdf.derive(senha.encode()))
    return chave, salt

def criptografar_texto(texto, senha):
    chave, salt = gerar_chave(senha)
    fernet = Fernet(chave)
    texto_criptografado = fernet.encrypt(texto.encode())
    return texto_criptografado, salt

def descriptografar_texto(texto_criptografado, senha, salt):
    chave, _ = gerar_chave(senha, salt)
    fernet = Fernet(chave)
    return fernet.decrypt(texto_criptografado).decode()

def gerar_qr_code(dados, nome_arquivo):
    img = qrcode.make(dados)
    img.save(nome_arquivo)

def ler_qr_code(nome_arquivo):
    img = Image.open(nome_arquivo)
    dados = pyzbar.decode(img)
    return dados[0].data

def main():
    parser = argparse.ArgumentParser(description='Criptografa texto e gera QR Code ou lê e descriptografa QR Code.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', '--encrypt', action='store_true', help='Modo de criptografia.')
    group.add_argument('-d', '--decrypt', action='store_true', help='Modo de descriptografia.')
    parser.add_argument('-n', '--nome', type=str, help='Nome do arquivo do QR Code.', required=True)
    parser.add_argument('-p', '--senha', type=str, help='Senha para criptografia/descriptografia.', required=True)

    args = parser.parse_args()

    if args.encrypt:
        texto = input("Digite ou cole o texto a ser criptografado: ")
        texto_criptografado, salt = criptografar_texto(texto, args.senha)
        # Combina o salt e o texto criptografado para armazenamento
        dados_para_qr = base64.urlsafe_b64encode(salt + texto_criptografado).decode()
        gerar_qr_code(dados_para_qr, args.nome)
        print(f"QR Code gerado e criptografado salvo como {args.nome}")
    elif args.decrypt:
        try:
            dados_codificados = ler_qr_code(args.nome)
            dados_decodificados = base64.urlsafe_b64decode(dados_codificados)
            # Extrai o salt e o texto criptografado
            salt, texto_criptografado = dados_decodificados[:16], dados_decodificados[16:]
            texto_descriptografado = descriptografar_texto(texto_criptografado, args.senha, salt)
            print("Texto descriptografado:", texto_descriptografado)
        except Exception as e:
            print("Não foi possível descriptografar:", e)

if __name__ == '__main__':
    main()


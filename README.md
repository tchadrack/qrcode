#QCPWD.PY 

Documentação do Script de Criptografia e QR Code

# Visão Geral

Este script fornece uma interface de linha de comando para criptografar um texto fornecido pelo usuário e gerar um QR Code 
correspondente, ou ler um QR Code existente e descriptografar o texto contido nele, se a senha correta for fornecida.

Você pode guardar informações sigilosas em um simples qrcode, impresso em papel ou algum outro suporte, seguras pela sua
 senha.


# Requisitos

- Python 3
- Bibliotecas: cryptography, qrcode, Pillow, pyzbar

Você precisará instalar o python, e as bibliotecas acima em seu sistema; 

### Funções

gerar_chave(senha, salt=None)
Gera uma chave segura para criptografia com base em uma senha fornecida.

Parâmetros:

senha: A senha a partir da qual a chave de criptografia será derivada.
salt: O salt a ser usado na derivação da chave. Se não for fornecido, um novo será gerado aleatoriamente.
Retorno:

Retorna uma tupla contendo a chave derivada e o salt utilizado.
criptografar_texto(texto, senha)
Criptografa um texto fornecido usando a senha fornecida.

Parâmetros:

texto: O texto claro a ser criptografado.
senha: A senha usada para gerar a chave de criptografia.
Retorno:

Retorna uma tupla contendo o texto criptografado e o salt usado na criptografia.
descriptografar_texto(texto_criptografado, senha, salt)
Descriptografa um texto criptografado fornecido usando a senha e o salt fornecidos.

Parâmetros:

texto_criptografado: O texto criptografado a ser descriptografado.
senha: A senha usada para descriptografar o texto.
salt: O salt usado para gerar a chave de criptografia.
Retorno:

Retorna o texto descriptografado.
gerar_qr_code(dados, nome_arquivo)
Gera um QR Code contendo os dados fornecidos e salva o QR Code como uma imagem.

Parâmetros:

dados: Os dados a serem incorporados no QR Code.
nome_arquivo: O nome do arquivo de imagem onde o QR Code será salvo.
ler_qr_code(nome_arquivo)
Lê um QR Code de um arquivo de imagem fornecido e extrai os dados contidos.

Parâmetros:

nome_arquivo: O nome do arquivo de imagem contendo o QR Code.
Retorno:



 
# Instalação

A instalação é muito simples, 


# UTILIZACAO - LINHA DE COMANDO

## clone o repositório:

git clone https://github.com/tchadrack/qrcode

## Invoque o script com os parâmetros desejados:

## CRIPTOGRAFANDO: 

#### python qcpwd.py -e -n nome_do_arquivo.png -p senha

Onde nome_do_arquivo.png é o nome do arquivo de imagem que será criado, e senha é a senha usada para criptografar o 
texto.


## DESCRIPTOGRAFANDO: 

#### python qcpwd.py -d -n nome_do_arquivo.png -p senha

Onde nome_do_arquivo.png é o nome do arquivo de imagem que contém o QR Code criptografado, e senha é a senha que, se 
correta, descriptografará o texto contido no QR Code.

Nota: A senha usada para descriptografar deve ser a mesma usada para criptografar o texto originalmente. Se a senha estiver 
incorreta, a descriptografia falhará.

# Segurança

Este script utiliza o algoritmo Fernet para criptografia simétrica, que é construído sobre o AES no modo CBC. O 
PBKDF2HMAC com SHA256 é usado para derivar a chave de criptografia segura a partir da senha e do salt. A segurança do 
script depende da força da senha escolhida e do segredo do salt gerado durante a criptografia.



### DOAÇÃO (DONATION): bc1q67uz4y2qfjyh2dd3dpus0emwplcshyg5n9nyys    (btc)





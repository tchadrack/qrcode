# QCPWD.PY

Script de linha de comando para criptografar um texto com senha, gerar um QR Code com os dados criptografados e,
posteriormente, ler o QR Code e descriptografar o conteudo com a senha correta.

Voce pode guardar informacoes sigilosas em um QR Code, impresso em papel ou outro suporte, protegidas pela sua senha.

## Destaques

- Script simples que roda localmente com Python.
- Codigo aberto para auditoria.
- Criptografia simetrica com senha; evite solucoes online para dados sensiveis.

## Como funciona

1) A senha informada e usada para derivar uma chave com PBKDF2-HMAC (SHA-256) e um salt aleatorio.
2) O texto e criptografado com Fernet usando a chave derivada.
3) O salt e concatenado ao ciphertext e o resultado e codificado em Base64 para caber no QR Code.
4) Na leitura, o QR e decodificado, o salt e separado do ciphertext, e o texto e descriptografado com a mesma senha.

## Requisitos

- Python 3
- Bibliotecas: cryptography, qrcode, Pillow, pyzbar

Instale o Python e as dependencias acima no seu sistema.

## Funcionalidades

- `gerar_chave(senha, salt=None)`: deriva uma chave segura a partir da senha usando PBKDF2HMAC e um salt.
- `criptografar_texto(texto, senha)`: criptografa texto com Fernet e retorna o ciphertext e o salt.
- `descriptografar_texto(texto_criptografado, senha, salt)`: descriptografa o ciphertext usando a senha e o salt.
- `gerar_qr_code(dados, nome_arquivo)`: gera e salva um QR Code com os dados.
- `ler_qr_code(nome_arquivo)`: le um QR Code e retorna os dados contidos.

## Instalacao

Clone o repositorio:

```bash
git clone https://github.com/tchadrack/qrcode
```

Instale as dependencias:

```bash
pip install cryptography qrcode Pillow pyzbar
```

## Utilizacao (linha de comando)

### Criptografando

```bash
python qcpwd.py -e -n nome_do_arquivo.png -p senha
```

O script pede o texto via `stdin`, criptografa e grava o QR Code no arquivo informado.

### Descriptografando

```bash
python qcpwd.py -d -n nome_do_arquivo.png -p senha
```

O script le o QR Code e tenta descriptografar o texto. A senha precisa ser a mesma usada na criptografia.

### Fluxo completo (exemplo)

```bash
echo "segredo de teste" | python qcpwd.py -e -n segredo.png -p senha-forte-123
python qcpwd.py -d -n segredo.png -p senha-forte-123
```

Saida esperada no modo de descriptografia:

```
Texto descriptografado: segredo de teste
```

## Estrutura do QR Code

O QR Code armazena uma string Base64 que contem:

```
[16 bytes de salt][ciphertext do Fernet]
```

Esse formato e gerado automaticamente pelo script e e esperado na leitura.

## Seguranca e limitacoes

- A seguranca depende da forca da senha. Use senhas longas e unicas.
- O salt e armazenado junto do ciphertext no QR Code. Isso e esperado e nao compromete a seguranca.
- Se o QR Code for danificado ou ilegivel, a descriptografia falha.
- A leitura do QR Code depende do `pyzbar` e da biblioteca nativa do ZBar no sistema.
- A criptografia usa Fernet (AES + HMAC) e a chave e derivada com PBKDF2-HMAC (SHA-256).

## Testes

Testes simples de roundtrip (criptografia -> QR -> descriptografia) em `tests/`:

```bash
python -m unittest discover -s tests
```

## Troubleshooting

- Erro ao importar `pyzbar`: instale o ZBar no sistema (no Windows, use um pacote que inclua as DLLs do ZBar).
- `Nenhum QR code encontrado no arquivo informado.`: o arquivo nao e um QR valido ou esta ilegivel.
- `Nao foi possivel descriptografar`: senha incorreta ou QR corrompido.

## Doacao (BTC)

`bc1q67uz4y2qfjyh2dd3dpus0emwplcshyg5n9nyys`

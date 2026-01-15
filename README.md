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
3) O salt, o ciphertext e um cabecalho com metadados (versao, iteracoes e salt-len) sao codificados em Base64 para caber no QR Code.
4) Na leitura, o QR e decodificado, o payload e interpretado e o texto e descriptografado com a mesma senha.

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

## Preparacao do ambiente

### Python (CLI)

Requisitos:
- Python 3.10+
- Bibliotecas: `cryptography`, `qrcode`, `Pillow`, `pyzbar`
- Dependencia nativa: ZBar (necessaria para o `pyzbar`)

Instale as dependencias Python:

```bash
pip install cryptography qrcode Pillow pyzbar
```

No Windows, instale o ZBar (ou um pacote que inclua as DLLs do ZBar) e garanta que
as DLLs estejam no `PATH`.

### Android/Flutter (app)

Este repositorio inclui um Flutter SDK em `tools/flutter` e um Android SDK em
`tools/android-sdk`. Se preferir, use seus SDKs instalados no sistema.

Requisitos:
- Flutter (SDK)
- Android SDK (platform-tools, build-tools)
- JDK 11+ (recomendado 17)

Se usar os SDKs locais do repo, execute:

```bash
tools/flutter/bin/flutter.bat doctor -v
tools/flutter/bin/flutter.bat config --jdk-dir="D:\GIT_REPOSITORIOS\qrcode\tools\jdk-17\jdk-17.0.17+10"
tools/flutter/bin/flutter.bat doctor --android-licenses
```

Opcional: adicione ao `PATH` (para nao precisar do caminho completo):
- `tools/flutter/bin`
- `tools/android-sdk/platform-tools`

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

### Ler texto de arquivo

```bash
python qcpwd.py -e -n nome_do_arquivo.png -p senha -i texto.txt
```

O arquivo de entrada deve estar em UTF-8 (com ou sem BOM).

### Fluxo completo (exemplo)

```bash
echo "segredo de teste" | python qcpwd.py -e -n segredo.png -p senha-forte-123
python qcpwd.py -d -n segredo.png -p senha-forte-123
```

Saida esperada no modo de descriptografia:

```
Texto descriptografado: segredo de teste
```

## Opcoes avancadas

- `--kdf-iter`: numero de iteracoes do PBKDF2 (padrao: 100000).
- `--salt-len`: tamanho do salt em bytes (padrao: 16).
- `--qr-index`: indice do QR quando ha mais de um na imagem (padrao: 0).

## Estrutura do QR Code

O QR Code armazena uma string Base64 que contem:

```
[magic QCPW][versao=1][iteracoes (4 bytes)][salt-len (1 byte)][salt][ciphertext do Fernet]
```

Esse formato e gerado automaticamente pelo script e e esperado na leitura. Payloads legados
sem cabecalho continuam sendo aceitos, mas exigem `--kdf-iter` e `--salt-len` corretos.

## Seguranca e limitacoes

- A seguranca depende da forca da senha. Use senhas longas e unicas.
- O salt e armazenado junto do ciphertext no QR Code. Isso e esperado e nao compromete a seguranca.
- Se o QR Code for danificado ou ilegivel, a descriptografia falha.
- A leitura do QR Code depende do `pyzbar` e da biblioteca nativa do ZBar no sistema.
- A criptografia usa Fernet (AES + HMAC) e a chave e derivada com PBKDF2-HMAC (SHA-256).

## Codigos de saida

- `0`: sucesso
- `1`: erro na leitura/decodificacao/descriptografia

## Testes

Testes simples de roundtrip (criptografia -> QR -> descriptografia) em `tests/`:

```bash
python -m unittest discover -s tests
```

## Android App (Flutter)

### Dependencias

As dependencias do app estao em `android_app/pubspec.yaml`:
- `mobile_scanner` (leitura de QR)
- `pointycastle` (criptografia)
- `cupertino_icons`

### Build debug

```bash
cd android_app
..\tools\flutter\bin\flutter.bat pub get
..\tools\flutter\bin\flutter.bat build apk --debug
```

### Build release (APK)

1) Criar keystore (ou usar um existente):

```bash
keytool -genkeypair -v -keystore android_app\android\app\app-release.jks ^
  -alias app-release -keyalg RSA -keysize 2048 -validity 10000 ^
  -storepass sua_senha -keypass sua_senha ^
  -dname "CN=SeuNome, OU=Dev, O=Empresa, L=Cidade, ST=Estado, C=BR"
```

2) Criar `android_app/android/key.properties` (arquivo ignorado pelo git):

```
storePassword=sua_senha
keyPassword=sua_senha
keyAlias=app-release
storeFile=../app/app-release.jks
```

3) Build:

```bash
cd android_app
..\tools\flutter\bin\flutter.bat build apk --release
```

Saida:
`android_app/build/app/outputs/flutter-apk/app-release.apk`

### APK por ABI (menor)

```bash
cd android_app
..\tools\flutter\bin\flutter.bat build apk --release --split-per-abi
```

### Instalacao via ADB

```bash
tools\android-sdk\platform-tools\adb.exe devices
tools\android-sdk\platform-tools\adb.exe install -r android_app\build\app\outputs\flutter-apk\app-release.apk
```

Se houver erro de assinatura, desinstale o app antigo:

```bash
tools\android-sdk\platform-tools\adb.exe uninstall com.example.android_app
```

## Troubleshooting

- Erro ao importar `pyzbar`: instale o ZBar no sistema (no Windows, use um pacote que inclua as DLLs do ZBar).
- `Nenhum QR code encontrado no arquivo informado.`: o arquivo nao e um QR valido ou esta ilegivel.
- `Indice de QR code fora do intervalo disponivel.`: use `--qr-index` com um valor valido.
- `Dados criptografados incompletos.`: QR truncado/corrompido ou `--salt-len` incorreto.
- `Nao foi possivel descriptografar`: senha incorreta ou QR corrompido.
- Flutter/Gradle falhando com Java 8: use JDK 11+ e configure com `flutter config --jdk-dir=...`.
- `adb` nao encontrado: use `tools/android-sdk/platform-tools/adb.exe` ou adicione ao `PATH`.

## Doacao (BTC)

`bc1q67uz4y2qfjyh2dd3dpus0emwplcshyg5n9nyys`

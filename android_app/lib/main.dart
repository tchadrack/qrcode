import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:pointycastle/api.dart'
    show KeyParameter, ParametersWithIV, PaddedBlockCipherParameters;
import 'package:pointycastle/block/aes.dart';
import 'package:pointycastle/block/modes/cbc.dart';
import 'package:pointycastle/digests/sha256.dart';
import 'package:pointycastle/key_derivators/api.dart';
import 'package:pointycastle/key_derivators/pbkdf2.dart';
import 'package:pointycastle/macs/hmac.dart';
import 'package:pointycastle/padded_block_cipher/padded_block_cipher_impl.dart';
import 'package:pointycastle/paddings/pkcs7.dart';

void main() {
  runApp(const QrDecryptApp());
}

class QrDecryptApp extends StatelessWidget {
  const QrDecryptApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'QR Decrypt',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
        useMaterial3: true,
      ),
      home: const QrDecryptPage(),
    );
  }
}

class QrDecryptPage extends StatefulWidget {
  const QrDecryptPage({super.key});

  @override
  State<QrDecryptPage> createState() => _QrDecryptPageState();
}

class _QrDecryptPageState extends State<QrDecryptPage> {
  final MobileScannerController _scannerController = MobileScannerController();
  final TextEditingController _passwordController = TextEditingController();

  String? _qrData;
  String? _decryptedText;
  String? _errorText;
  bool _busy = false;

  @override
  void dispose() {
    _scannerController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _onDetect(BarcodeCapture capture) {
    if (_qrData != null || _busy) {
      return;
    }
    for (final barcode in capture.barcodes) {
      final raw = barcode.rawValue;
      if (raw != null && raw.isNotEmpty) {
        setState(() {
          _qrData = raw;
          _decryptedText = null;
          _errorText = null;
        });
        _scannerController.stop();
        break;
      }
    }
  }

  Future<void> _decrypt() async {
    final data = _qrData;
    final password = _passwordController.text;
    if (data == null || data.isEmpty) {
      setState(() {
        _errorText = 'Escaneie um QR antes de descriptografar.';
      });
      return;
    }
    if (password.isEmpty) {
      setState(() {
        _errorText = 'Informe a senha.';
      });
      return;
    }
    setState(() {
      _busy = true;
      _errorText = null;
      _decryptedText = null;
    });
    try {
      final plainText = _decryptPayload(data, password);
      setState(() {
        _decryptedText = plainText;
      });
    } catch (error) {
      setState(() {
        _errorText = 'Nao foi possivel descriptografar: $error';
      });
    } finally {
      setState(() {
        _busy = false;
      });
    }
  }

  void _resetScan() {
    setState(() {
      _qrData = null;
      _decryptedText = null;
      _errorText = null;
      _passwordController.clear();
    });
    _scannerController.start();
  }

  @override
  Widget build(BuildContext context) {
    final hasQr = _qrData != null;
    return Scaffold(
      appBar: AppBar(
        title: const Text('QR Criptografado'),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Expanded(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: Stack(
                    children: [
                      MobileScanner(
                        controller: _scannerController,
                        onDetect: _onDetect,
                      ),
                      Positioned(
                        left: 16,
                        right: 16,
                        bottom: 16,
                        child: Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.black.withOpacity(0.6),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            hasQr
                                ? 'QR capturado. Informe a senha.'
                                : 'Aponte a camera para o QR.',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.w600,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _passwordController,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Senha',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _busy ? null : _decrypt,
                      child: _busy
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Descriptografar'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  OutlinedButton(
                    onPressed: _busy ? null : _resetScan,
                    child: const Text('Novo scan'),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              if (_decryptedText != null)
                Expanded(
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Theme.of(context)
                          .colorScheme
                          .secondaryContainer,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: SelectableText(
                      _decryptedText!,
                      style: const TextStyle(fontSize: 16),
                    ),
                  ),
                )
              else if (_errorText != null)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  child: Text(
                    _errorText!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

String _decryptPayload(
  String payload,
  String password, {
  int saltLen = 16,
  int iterations = 100000,
}) {
  final payloadBytes = _base64UrlDecode(payload);
  if (payloadBytes.length <= saltLen) {
    throw StateError('Payload incompleto.');
  }
  final salt = Uint8List.fromList(payloadBytes.sublist(0, saltLen));
  final tokenEncoded =
      ascii.decode(payloadBytes.sublist(saltLen), allowInvalid: false);
  final token = _base64UrlDecode(tokenEncoded);
  final keyBytes = _deriveKey(password, salt, iterations);
  final plainBytes = _fernetDecrypt(token, keyBytes);
  return utf8.decode(plainBytes);
}

Uint8List _deriveKey(String password, Uint8List salt, int iterations) {
  final derivator = PBKDF2KeyDerivator(HMac(SHA256Digest(), 64))
    ..init(Pbkdf2Parameters(salt, iterations, 32));
  return derivator.process(Uint8List.fromList(utf8.encode(password)));
}

Uint8List _fernetDecrypt(Uint8List token, Uint8List keyBytes) {
  if (keyBytes.length != 32) {
    throw StateError('Chave invalida.');
  }
  if (token.length < 1 + 8 + 16 + 32) {
    throw StateError('Token invalido.');
  }
  if (token[0] != 0x80) {
    throw StateError('Versao do token invalida.');
  }
  final signingKey = keyBytes.sublist(0, 16);
  final encryptionKey = keyBytes.sublist(16, 32);
  final signed = token.sublist(0, token.length - 32);
  final signature = token.sublist(token.length - 32);

  final hmac = HMac(SHA256Digest(), 64)..init(KeyParameter(signingKey));
  final expected = hmac.process(Uint8List.fromList(signed));
  if (!_constantTimeEqual(expected, signature)) {
    throw StateError('Assinatura invalida.');
  }

  final ivOffset = 1 + 8;
  final iv = token.sublist(ivOffset, ivOffset + 16);
  final cipherText = token.sublist(ivOffset + 16, token.length - 32);

  final cipher = PaddedBlockCipherImpl(
    PKCS7Padding(),
    CBCBlockCipher(AESEngine()),
  );
  cipher.init(
    false,
    PaddedBlockCipherParameters<ParametersWithIV<KeyParameter>, Null>(
      ParametersWithIV<KeyParameter>(KeyParameter(encryptionKey), iv),
      null,
    ),
  );
  return cipher.process(cipherText);
}

Uint8List _base64UrlDecode(String input) {
  final normalized = base64Url.normalize(input);
  return Uint8List.fromList(base64Url.decode(normalized));
}

bool _constantTimeEqual(Uint8List a, Uint8List b) {
  if (a.length != b.length) {
    return false;
  }
  var diff = 0;
  for (var i = 0; i < a.length; i++) {
    diff |= a[i] ^ b[i];
  }
  return diff == 0;
}

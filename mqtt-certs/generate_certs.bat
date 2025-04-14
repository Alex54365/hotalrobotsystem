@echo off
setlocal

REM === 路徑設定 ===
set OPENSSL_CONF=certs\openssl.cnf
set CERT_DIR=certs

REM === 建立 certs 資料夾 ===
if not exist %CERT_DIR% mkdir %CERT_DIR%

REM === 產生 CA 私鑰與憑證 ===
openssl genrsa -out %CERT_DIR%\ca.key 2048
openssl req -x509 -new -nodes -key %CERT_DIR%\ca.key -sha256 -days 3650 -out %CERT_DIR%\ca.crt -config %CERT_DIR%\openssl.cnf

REM === 產生 Server 私鑰 ===
openssl genrsa -out %CERT_DIR%\server.key 2048

REM === 建立 CSR（簽署請求）===
openssl req -new -key %CERT_DIR%\server.key -out %CERT_DIR%\server.csr -config %CERT_DIR%\openssl.cnf

REM === 用 CA 憑證簽署成 server.crt ===
openssl x509 -req -in %CERT_DIR%\server.csr -CA %CERT_DIR%\ca.crt -CAkey %CERT_DIR%\ca.key -CAcreateserial -out %CERT_DIR%\server.crt -days 3650 -sha256 -extfile %CERT_DIR%\openssl.cnf -extensions v3_ca

del %CERT_DIR%\server.csr
del %CERT_DIR%\ca.srl

echo Done! 憑證已產生於 certs\ 資料夾
pause
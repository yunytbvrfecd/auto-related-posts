import pyotp
import qrcode

secret = pyotp.random_base32()
print("TOTP_SECRET:", secret)

# QRコードを表示
totp = pyotp.TOTP(secret)
uri = totp.provisioning_uri(name="admin@example.com", issuer_name="MyPortfolioApp")
img = qrcode.make(uri)
img.show()

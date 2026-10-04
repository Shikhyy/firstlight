import base64
import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

# Generate private key
private_key = ec.generate_private_key(ec.SECP256R1())

# Get public key
public_key = private_key.public_key()

# Serialize to DER
priv_der = private_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
pub_der = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint,
)

# Convert to urlsafe base64
priv_b64 = base64.urlsafe_b64encode(priv_der).decode("utf-8").rstrip("=")
pub_b64 = base64.urlsafe_b64encode(pub_der).decode("utf-8").rstrip("=")

with open("data/vapid.json", "w") as f:
    json.dump({"private_key": priv_b64, "public_key": pub_b64}, f)

print(f"Public Key: {pub_b64}")

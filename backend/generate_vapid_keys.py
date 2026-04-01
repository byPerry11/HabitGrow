import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

def generate_vapid_keys():
    # 1. Generar la llave privada (curva P-256 / SECP256R1)
    private_key = ec.generate_private_key(ec.SECP256R1())
    
    # 2. Extraer los bytes de la llave privada (32 bytes)
    private_bytes = private_key.private_numbers().private_value.to_bytes(32, byteorder='big')
    
    # 3. Obtener la llave pública y sus coordenadas X, Y
    public_key = private_key.public_key()
    public_numbers = public_key.public_numbers()
    
    # Formato Uncompressed ANSI X9.62 (0x04 + X + Y) - Requerido por Web Push
    public_bytes = b'\x04' + \
                   public_numbers.x.to_bytes(32, byteorder='big') + \
                   public_numbers.y.to_bytes(32, byteorder='big')
    
    # 4. Codificar en Base64 URL Safe sin caracteres de relleno (=)
    def b64url(data):
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')
    
    print("--- VAPID KEYS GENERATED ---")
    print(f"VAPID_PUBLIC_KEY={b64url(public_bytes)}")
    print(f"VAPID_PRIVATE_KEY={b64url(private_bytes)}")
    print("----------------------------")

if __name__ == "__main__":
    generate_vapid_keys()

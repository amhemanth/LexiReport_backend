import secrets

# Generate a secure random key
jwt_secret_key = secrets.token_urlsafe(32)
print("\nGenerated JWT Secret Key:")
print("------------------------")
print(jwt_secret_key)
print("\nCopy this key and replace the JWT_SECRET_KEY value in your .env file") 
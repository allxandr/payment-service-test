import os

os.environ["DB__USER"] = "postgres"
os.environ["DB__PASSWORD"] = "postgres"
os.environ["DB__HOST"] = "localhost"
os.environ["DB__PORT"] = "5432"
os.environ["DB__NAME"] = "payments"
os.environ["RABBIT__USER"] = "guest"
os.environ["RABBIT__PASSWORD"] = "guest"
os.environ["RABBIT__HOST"] = "localhost"
os.environ["RABBIT__PORT"] = "5672"
os.environ["AUTH__API_KEY"] = "test-key"
os.environ["API__PORT"] = "8000"
os.environ["ID_GENERATOR__NODE_ID"] = "1"

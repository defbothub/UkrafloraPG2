from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Session

DATABASE_URL = 'postgresql://rxnotqepljlmpp:e8205400e6f8d44b9b5799c1850f3aa996feb260bd16120a0088e3e2ea969772@ec2-63-35-80-199.eu-west-1.compute.amazonaws.com:5432/d5jh23sj9fkhpv'

engine = create_engine(DATABASE_URL)
engine.connect()
db_session = Session(bind=engine)

Base = declarative_base()

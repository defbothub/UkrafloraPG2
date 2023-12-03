from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Session

DATABASE_URL = 'postgresql://tlsonjxxxrjutf:fa7a42d08c48a7c979c96535a3277244dde9acf0039da9ac143cc098901ed3cd@ec2-176-34-212-157.eu-west-1.compute.amazonaws.com:5432/d5dp934vr7psm7'

engine = create_engine(DATABASE_URL)
engine.connect()
db_session = Session(bind=engine)

Base = declarative_base()
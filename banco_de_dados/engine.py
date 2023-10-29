from sqlalchemy import create_engine


URL_DB = 'postgresql://postgres:postgres@loccalhost:5432/desafio_dio_db'
engine = create_engine(URL_DB, echo=True)

from sqlmodel import SQLModel

class User(SQLModel, table=True):
  pass

class Image(SQLModel, table=True):
  pass

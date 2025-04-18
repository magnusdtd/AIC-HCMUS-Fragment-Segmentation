from sqlmodel import SQLModel, Session

class User(SQLModel, table=True):
  pass

class Image(SQLModel, table=True):
  pass
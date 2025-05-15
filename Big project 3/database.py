from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.future import select
from sqlalchemy import Table, Column ,create_engine , String, ForeignKey,Text,update
from typing import List, Optional
from sqlalchemy.orm import DeclarativeBase , sessionmaker, Mapped, mapped_column, relationship

DATABASE_URL = "mysql+aiomysql://root:8292@localhost/Artist_club"



engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False,unique=True)
    password = Column(String(255), nullable=False)

class Artist(Base):
    __tablename__ = "artist"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255),unique=True)
    password = Column(String(255), nullable=False)
    description = Column(String(300), nullable=False)
    experience = Column(String(255), nullable=False)


class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    topic= Column(String(255), nullable=False)
    material = Column(String(255))
    price = Column(Integer, nullable=False)
    artist_id :Mapped[int] = mapped_column(ForeignKey('artist.id',ondelete='CASCADE'))

class Product_foto(Base):
    __tablename__ = "product_foto"
    id = Column(Integer, primary_key=True, index=True)
    foto_name = Column(String(255), nullable=False)
    product_id:Mapped[int] = mapped_column(ForeignKey('product.id',ondelete='CASCADE'))

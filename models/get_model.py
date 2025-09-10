from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

Base =declarative_base()


class Items(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("login.user_id"))

    # Relationship to access user info directly
    user = relationship("Login", back_populates="items")
    def __str__(self):
        return f"{self.title} : {self.description}"
    

class Login(Base):
    __tablename__ = "login"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    items = relationship("Items", back_populates="user")
    def __str__(self):
        return f"{self.user_name} : {self.password}"

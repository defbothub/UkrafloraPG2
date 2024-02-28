from sqlalchemy import Column, String, Integer, LargeBinary, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .db_loader import Base, engine


class Products(Base):
    __tablename__ = 'products'
    id = Column('id', Integer, primary_key=True, unique=True,
                nullable=False, autoincrement=True)
    categori_id = Column(ForeignKey(
        "categories.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    photo = Column(LargeBinary, nullable=False)
    price = Column(Integer, nullable=False)
    category = relationship("Сategories", back_populates="products")
    ordered_product = relationship(
        "Ordered_products", back_populates="product", cascade="all, delete")


class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, nullable=False,
                unique=True, autoincrement=True)
    usr_name = Column(String)
    usr_address = Column(String)
    tg_uid = Column(Integer, nullable=False)
    is_orderd = Column(Boolean, default=False)
    ordered_products = relationship(
        "Ordered_products", back_populates="order", cascade="all, delete", overlaps="orders,product")


class Ordered_products(Base):
    __tablename__ = 'ordered_products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(ForeignKey(
        "products.id", ondelete="CASCADE"), nullable=False)
    order_id = Column(ForeignKey("orders.id", ondelete="CASCADE"))
    quantity = Column(Integer, nullable=False)
    product = relationship("Products", back_populates="ordered_product")
    order = relationship(
        "Orders", back_populates="ordered_products", overlaps="orders")


class Сategories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    products = relationship(
        "Products", back_populates="category", cascade="all, delete")

class Promotion(Base):
    __tablename__ = 'promotions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    photo = Column(LargeBinary, nullable=False)
    caption = Column(String, nullable=False)

class User(Base):
    __tablename__ = 'users_ukrflr'

    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Integer, nullable=False, default=1)

def create_tables():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_tables()

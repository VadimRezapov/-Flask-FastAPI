"""
Необходимо создать базу данных для интернет-магазина. База данных должна
состоять из трех таблиц: товары, заказы и пользователи. Таблица товары должна
содержать информацию о доступных товарах, их описаниях и ценах. Таблица
пользователи должна содержать информацию о зарегистрированных
пользователях магазина. Таблица заказы должна содержать информацию о
заказах, сделанных пользователями.
    ○ Таблица пользователей должна содержать следующие поля: id (PRIMARY KEY),
    имя, фамилия, адрес электронной почты и пароль.
    ○ Таблица товаров должна содержать следующие поля: id (PRIMARY KEY),
    название, описание и цена.
    ○ Таблица заказов должна содержать следующие поля: id (PRIMARY KEY), id
    пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус
    заказа.
------------------------------------------------------------------------------
    Создайте модели pydantic для получения новых данных и
возврата существующих в БД для каждой из трёх таблиц
(итого шесть моделей).
    Реализуйте CRUD операции для каждой из таблиц через
создание маршрутов, REST API.
    ○ Чтение всех
    ○ Чтение одного
    ○ Запись
    ○ Изменение
    ○ Удаление
"""
from datetime import datetime, timedelta, date
import random
from typing import List
from fastapi import FastAPI, Path
from pydantic import BaseModel, Field
import uvicorn
import sqlalchemy
import databases

DATABASE_URL = "sqlite:///dz6.db"
database = databases.Database(DATABASE_URL)
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata = sqlalchemy.MetaData()


users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(50)),
    sqlalchemy.Column("surname", sqlalchemy.String(50)),
    sqlalchemy.Column("email", sqlalchemy.String(50)),
    sqlalchemy.Column("password", sqlalchemy.String(120)),
)

goods = sqlalchemy.Table(
    "goods",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(50)),
    sqlalchemy.Column("description", sqlalchemy.String(200)),
    sqlalchemy.Column("price", sqlalchemy.Float)
)

orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
    sqlalchemy.Column("goods_id", sqlalchemy.ForeignKey("goods.id"), nullable=False),
    sqlalchemy.Column("order_date", sqlalchemy.DATE),
    sqlalchemy.Column('status', sqlalchemy.String(20))
)

metadata.create_all(engine)


class User(BaseModel):
    id: int = Field(default=None)
    name: str = Field(min_length=2, max_length=50)
    surname: str = Field(min_length=2, max_length=50)
    email: str = Field(min_length=4, max_length=50)
    password: str = Field(min_length=5, max_length=120)


class UserIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    surname: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=5, max_length=120)


class Goods(BaseModel):
    id: int = Field(default=None)
    name: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=2, max_length=200)
    price: float = Field(..., ge=0.1, le=100000)


class GoodsIn(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=2, max_length=200)
    price: float = Field(..., ge=0.1, le=100000)


class Order(BaseModel):
    id: int = Field(default=None)
    order_date: date = Field(default=datetime.now())
    status: str = Field(default='in_progress')
    user_id: int
    goods_id: int


class OrderIn(BaseModel):
    order_date: date = Field(default=datetime.now())
    status: str = Field(default='in_progress')
    user_id: int
    goods_id: int


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/')
async def root():
    return {"message": "Интернет магазин"}


# создание тестовых пользователей - count количество создаваемых пользователей
@app.get('/users/fake/{count}')
async def create_fake_users(count: int):
    for i in range(count):
        query = users.insert().values(name=f'user{i+1}',
                                      surname=f'user{i+1}',
                                      email=f'email{i+1}@mail.ru',
                                      password=f'qwerty{i+1}')
        await database.execute(query)
    return {'message': f'{count} тестовых пользователя добавлено в базу данных'}


# создание тестовых товаров - count количество создаваемых товаров
@app.get('/goods/fake/{count}')
async def create_fake_goods(count: int):
    for i in range(count):
        query = goods.insert().values(
            name=f'Goods_name {i+1}',
            description='Some description',
            price=f'{random.randint(1, 100000):.2f}'
        )
        await database.execute(query)
    return {'message': f'{count} тестовых товаров добавлено в базу данных '}


# создание тестовых покупок - count количество создаваемых покупок
@app.get('/orders/fake/{count}')
async def create_fake_orders(count: int):
    for i in range(count):
        query = orders.insert().values(
            order_date=datetime.strptime("2000-01-24", "%Y-%m-%d").date() + timedelta(days=i ** 2),
            status=random.choice(['in_progress', 'done', 'cancelled']),
            user_id=random.randint(1, 10),
            goods_id=random.randint(1, 10)
        )
        await database.execute(query)
    return {'message': f'{count} тестовых покупок добавлено в базу данных'}


# просмотр всех пользователей
@app.get('/users/', response_model=List[User])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)


# просмотр одного пользователя - указать user_id пользователя
@app.get('/users/{user_id}', response_model=User)
async def read_user(user_id: int = Path(..., ge=1)):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


# создание пользователя
@app.post('/users/create/', response_model=User)
async def create_user(user: UserIn):
    query = users.insert().values(
        name=user.name,
        surname=user.surname,
        email=user.email,
        password=user.password
        )
    actual_id = await database.execute(query)
    return {**user.dict(), 'id': actual_id}


# добавление пользователя
@app.put('/users/update/{user_id}', response_model=User)
async def update_user(new_user: UserIn, user_id: int = Path(..., ge=1)):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), 'id': user_id}


# удаление пользователя
@app.delete('/users/delete/{user_id}')
async def delete_user(user_id: int = Path(..., ge=1)):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {'message': f'Пользователь с ID {user_id} удалён'}


# просмотр товаров
@app.get('/goods/', response_model=List[Goods])
async def get_all_goods():
    query = goods.select()
    return await database.fetch_all(query)


# просмотр одного товара - укажите его product_id
@app.get('/goods/{goods_id}', response_model=Goods)
async def get_goods(product_id: int = Path(..., ge=1)):
    query = goods.select().where(goods.c.id == product_id)
    return await database.fetch_one(query)


# создание товара
@app.post('/goods/create/', response_model=Goods)
async def create_goods(product: GoodsIn):
    query = goods.insert().values(
        name=product.name,
        description=product.description,
        price=product.price
        )
    actual_id = await database.execute(query)
    return {**product.dict(), 'id': actual_id}


# измекнение товара  - укажите его product_id
@app.put('/goods/update/{product_id}', response_model=Goods)
async def update_goods(new_product: GoodsIn, product_id: int = Path(..., ge=1)):
    query = goods.update().where(goods.c.id == product_id).values(**new_product.dict())
    await database.execute(query)
    return {**new_product.dict(), 'id': product_id}


# удаление товара  - укажите его product_id
@app.delete('/goods/delete/{product_id}')
async def delete_goods(product_id: int = Path(..., ge=1)):
    query = goods.delete().where(goods.c.id == product_id)
    await database.execute(query)
    return {'message': f'Товар с id {product_id} удалён'}


# просмотр всех покупок
@app.get('/orders/', response_model=List[Order])
async def get_orders():
    query = orders.select()
    return await database.fetch_all(query)


# просмотр одной покупоки - укажите её order_id
@app.get('/orders/{order_id}', response_model=Order)
async def get_order(order_id: int = Path(..., ge=1)):
    query = orders.select().where(orders.c.id == order_id)
    return await database.fetch_one(query)


# создание покупки
@app.post('/orders/create/', response_model=Order)
async def create_order(order: OrderIn):
    query = orders.insert().values(
        order_date=order.order_date,
        status=order.status,
        user_id=order.user_id,
        goods_id=order.goods_id
        )
    actual_id = await database.execute(query)
    return {**order.dict(), 'id': actual_id}


# изменение покупки
@app.put('/orders/update/{order_id}', response_model=Order)
async def update_order(new_order: OrderIn, order_id: int = Path(..., ge=1)):
    query = orders.update().where(orders.c.id == order_id).values(**new_order.dict())
    await database.execute(query)
    return {**new_order.dict(), 'id': order_id}


# удаление покупки - укажите её order_id
@app.delete('/orders/delete/{order_id}')
async def delete_order(order_id: int = Path(..., ge=1)):
    query = orders.delete().where(orders.c.id == order_id)
    await database.execute(query)
    return {'message': f'Покупка с id {order_id} удалена'}


if __name__ == '__main__':
    uvicorn.run('dz6:app',
                host='127.0.0.1',
                port=8000,
                reload=True)
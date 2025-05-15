from fastapi import (FastAPI,status,HTTPException,Depends,Request,
                     Form,File,UploadFile,Query,BackgroundTasks,WebSocket,
                     WebSocketDisconnect)
from typing import List, Optional, Union, Any
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from fastapi.responses import JSONResponse,FileResponse
import pytz
from database import *
from basemodel import *
import os
import shutil

app = FastAPI()
oauth2_sheme = OAuth2PasswordBearer(tokenUrl='token')
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
UPLOAD_DIRECTORY = 'Upload'
ALLOWED_FILE_TYPES = ["image/png","image/jpeg","image/jpg"]
active_websockets: List[WebSocket] = []
payload= {'user':'alx333'}
token_secret = jwt.encode(payload,'SECRET_KEY', 'HS256')

class ArtistRegister_update(BaseModel):
   artist_id: int = Field(..., name='id',
                            description='artist_id')
   description:str = Field(..., name='information',
                          description='something about you')
   experience:str= Field(..., name='age',
                          description='age of your experience')




class Product_model_update(BaseModel):
    product_id: int = Field(..., name='id',
                            description='product_id')
    description: str = Field(..., name='description',
                             description='product description')
    price: int = Field(..., name='price',
                       description='product price')
    topic: str = Field(..., name='topic',
                       description='product topic')
    material: str = Field(..., name='material',
                          description='product material')


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

def create_token(data:dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


@app.post('/token')
async def token(form_data: OAuth2PasswordRequestForm = Depends(),session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.name == form_data.username))
    user = result.scalars().first()
    result = await session.execute(select(Artist).where(Artist.name == form_data.username))
    artist= result.scalars().first()
    if artist and form_data.password == artist.password:
        current_user = artist
    elif user and form_data.password == user.password:
        current_user = user
    else:
        raise HTTPException(401, 'not right login or password')
    # if not artist or form_data.password != artist.password:
    #     raise HTTPException(401, 'not right login or password')
    # if not user or form_data.password != user.password:
    #     raise HTTPException(401, 'not right login or password')
    access_token = create_token({'username':current_user.name,'password':current_user.password })
    return {'access_token':access_token, 'token_type':'bearer'}

async def get_current_user(token:str = Depends(oauth2_sheme),session: AsyncSession = Depends(get_session)):
    try:
        user = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        result = await session.execute(select(User).where(User.name == user['username'] ))
        user_db = result.scalars().first()
        result = await session.execute(select(Artist).where(Artist.name == user['username'] ))
        artist = result.scalars().first()
        print(artist)
        print(user_db)
        print(user)
        if not user_db and not artist:
            raise HTTPException(401, 'not right token')
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException ( 401, 'Token time was finished')



@app.post("/register_user",tags=['for user'])
async def register_user(form_data:UserRegister,session: AsyncSession = Depends(get_session)):
    if form_data.username and form_data.password:
        new_user = User(name=form_data.username, password=form_data.password)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    else:
        raise HTTPException(status_code=400, detail="Користувач вже існує")

@app.post("/register_artist",tags=['for artist'])
async def register_artist(form_data:ArtistRegister,session: AsyncSession = Depends(get_session)):
    if form_data.name and form_data.password:
        new_artist = Artist(name=form_data.name, password=form_data.password,
                            description=form_data.description,experience=form_data.experience)
        session.add(new_artist)
        await session.commit()
        await session.refresh(new_artist)
        return new_artist
    else:
        raise HTTPException(status_code=400, detail="Користувач вже існує")

@app.post("/update_art",tags=['for artist'])
async def update_art(user_name:str ,product_name:str,
                     user:str = Depends(get_current_user),
                     session: AsyncSession = Depends(get_session)):
    global art_global
    result = await session.execute(select(Artist).where(Artist.name == user_name))
    artist = result.scalar_one()
    result_1 = await session.execute(select(Product).where(Product.name == product_name))
    art = result_1.scalars().first()
    result_2 = await session.execute(select(Product).where(Product.name == product_name, Product.artist_id == artist.id))
    art_global = result_2.scalars().first()
    if art_global is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found")

    return {'art_global': art_global}

@app.post("/update_art_1",tags=['for artist'])
async def update_1_art(product_model:Product_model_update,user:str = Depends(get_current_user),
                     session: AsyncSession = Depends(get_session)):
    result = await session.execute(update(Product).where(Product.id==product_model.product_id).
                                   values(description=product_model.description,
                                          topic=product_model.topic,material=product_model.material,
                                          price=product_model.price))
    await session.commit()
    return {'result':'update successful'}

@app.post("/update_artist",tags=['for artist'])
async def update_artist(user_name:str ,
                     user:str = Depends(get_current_user),
                     session: AsyncSession = Depends(get_session)):
    global art_global_1
    result = await session.execute(select(Artist).where(Artist.name == user_name))
    art_global_1 = result.scalar_one()
    if art_global_1 is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found")

    return {'art_global': art_global_1}

@app.post("/update_artist_1",tags=['for artist'])
async def update_1_artist(artistRegister_update:ArtistRegister_update,user:str = Depends(get_current_user),
                     session: AsyncSession = Depends(get_session)):
    result = await session.execute(update(Artist).where(Artist.id==artistRegister_update.artist_id).
                                   values(description=artistRegister_update.description,
                                          experience=artistRegister_update.experience))
    await session.commit()
    return {'result':'update successful'}


@app.delete("/delete_art",tags=['for artist'])
async def delete_art(user_name:str ,product_name:str,
                     user:str = Depends(get_current_user),
                     session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Artist).where(Artist.name == user_name))
    artist = result.scalar_one()
    # artist_info = await session.get(Artist, artist.id)
    result_1 = await session.execute(select(Product).where(Product.name == product_name))
    art = result_1.scalars().first()
    result_2 = await session.execute(select(Product).where(Product.name == product_name,Product.artist_id==artist.id))
    art_1 = result_2.scalars().first()
    if art_1 is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found")
    await session.delete(art_1)
    await session.commit()

    return {"message": f"Product '{product_name}' successfully deleted"}



@app.post('/add_img3',tags=['for artist'])
async def add_img3(user_name:str = Form(...),product_name:str = Form(...),description:str = Form(...),price:int = Form(...),topic:str = Form(...), material:str = Form(...),files:List[UploadFile] = File(...),user:str = Depends(get_current_user),
                   session: AsyncSession = Depends(get_session)):
    form= Product_model(user_name=user_name,product_name=product_name,description=description,
                   price=price,topic=topic,material=material)
    if not form:
        raise HTTPException(status_code=400, detail="Неправельні данні")
    result = await session.execute(select(Artist).where(Artist.name == user_name))
    user = result.scalar_one()
    if user:
        if user_name and product_name and description and price and topic and material:
            new_product = Product(name=product_name, description=description,
                                   price=price, topic=topic,
                                  material=material, artist_id = user.id)
            session.add(new_product)
            await session.commit()
            await session.refresh(new_product)
        os.makedirs(os.path.join(f'{UPLOAD_DIRECTORY}/{product_name}'), exist_ok=True)
        image_names = []
        counter= 1
        for file in files:
            if file.content_type not in ALLOWED_FILE_TYPES:
                raise HTTPException(status_code=400, detail="Неприпустимий формат файлу")
            ext = os.path.splitext(file.filename)[-1]
            with open(f'{UPLOAD_DIRECTORY}/{product_name}/{counter}{ext}', 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)
            image_names.append(f'{counter}{ext}')
            new_foto = Product_foto(foto_name=f'{counter}{ext}', product_id=new_product.id)
            session.add(new_foto)
            await session.commit()
            await session.refresh(new_foto)
            counter += 1
        return {'message': 'files added!', 'title': product_name, 'files': image_names}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='Невірні дані', headers={'WWW-Authenticate': 'Bearer'})

@app.get('/search_art',tags=['for user'])
async def search(topic:str= Query(...,name='topic',description='art topic')
           ,user:str = Depends(get_current_user),session: AsyncSession = Depends(get_session)):
    art = await session.execute(select(Product).where(Product.topic.ilike(f'%{topic}%') ))
    art_db = art.scalars().all()
    result = []
    for art_one in art_db:
        product_id_db=await session.execute(select(Product_foto).where(Product.id==art_one.id))
        product_info = product_id_db.scalars().first()
        artist_info = await session.get(Artist, art_one.artist_id)
        result.append({'picture': product_info.foto_name,
                       'artist_name':artist_info.name,
                       'artist_experience':artist_info.experience,
                       'product_name':art_one.name,
                       'product_description':art_one.description,
                       'product_topic':art_one.topic,
                       'product_material':art_one.material,
                       'product_price':art_one.price})
        # file_path = os.path.join(UPLOAD_DIRECTORY)
    return result

@app.get('/search_art_foto',tags=['for user'])
async def search_foto(product_name:str,foto_name:str,user:str = Depends(get_current_user)):
    return FileResponse(f'{UPLOAD_DIRECTORY}/{product_name}/{foto_name}')

@app.get('/search_all_art',tags=['for user'])
async def search_all(user:str = Depends(get_current_user),session: AsyncSession = Depends(get_session)):
    art = await session.execute(select(Product))
    art_db = art.scalars().all()
    result = []
    for art_one in art_db:
        product_id_db=await session.execute(select(Product_foto).where(Product.id==art_one.id))
        product_info = product_id_db.scalars().first()
        artist_info = await session.get(Artist, art_one.artist_id)
        result.append({'picture': product_info.foto_name,
                       'artist_name':artist_info.name,
                       'artist_experience':artist_info.experience,
                       'product_name':art_one.name,
                       'product_description':art_one.description,
                       'product_topic':art_one.topic,
                       'product_material':art_one.material,
                       'product_price':art_one.price})
        # file_path = os.path.join(UPLOAD_DIRECTORY)
    return result

@app.get('/search_all_art_foto',tags=['for user'])
async def search_foto(product_name:str,foto_name:str,user:str = Depends(get_current_user)):
    return FileResponse(f'{UPLOAD_DIRECTORY}/{product_name}/{foto_name}')



def verify_jwt(token:str= Depends(oauth2_sheme)):
    try:
        user = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        return user
    except jwt.PyJWTError:
       return

@app.websocket('/')
async def ws_endpoint(websocket:WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        token = websocket.headers.get('Authorization')
        if not verify_jwt(token):
            await websocket.close(code=4000, reason='Unauthorized')
            return
        while True:
            data = await websocket.receive_text()
            for ws in active_websockets:
                if ws != websocket:
                # if "зв'язатися з менеджером" in data.lower():
                #     await ws.send_text('Опишіть свою проблему')
                # else:
                    await ws.send_text(data)
    except WebSocketDisconnect:
        # await websocket.send_text('Всім папа')
        print(f'Клієнт {websocket.client} відключився')
        active_websockets.remove(websocket)
    except Exception as e:
        print(e)
    finally:
        if websocket.client_state== 'CONNECTED':
            await websocket.close()



async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await init_db()


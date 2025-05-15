from pydantic import (BaseModel, field_validator, ValidationError,
                      EmailStr,constr,HttpUrl,Field)



class UserRegister(BaseModel):
   username: str = Field(..., name='name',
                     description='your name')
   password: str = Field(..., name='password',
                         description='your password')

   @field_validator('password')
   def validator_password(cls, v):
      if len(v) <= 7:
         raise ValueError('Password must be longer')
      return v

class ArtistRegister(BaseModel):
   name: str = Field(..., name='name',
                          description='your name')
   password: str = Field(..., name='password',
                          description='your password')
   description:str = Field(..., name='information',
                          description='something about you')
   experience:str= Field(..., name='age',
                          description='age of your experience')

   @field_validator('password')
   def validator_password(cls, v):
      if len(v) <= 7:
         raise ValueError('Password must be longer')
      return v

   @field_validator('description')
   def validator_description(cls, v):
      if len(v) <= 10:
         raise ValueError('Description must be longer')
      return v

class Product_model(BaseModel):
   user_name: str = Field(..., name='name',
                          description='your name')
   product_name: str = Field(..., name='name',
                             description='product name')
   description: str = Field(..., name='description',
                            description='product description')
   price: int = Field(..., name='price',
                      description='product price')
   topic: str = Field(..., name='topic',
                      description='product topic')
   material: str = Field(..., name='material',
                      description='product material')


   @field_validator('product_name')
   def validator_name(cls, v):
      if len(v) <= 2:
         raise ValueError('name must be longer')
      return v

   @field_validator('description')
   def validator_description(cls, v):
      if len(v) <= 10:
         raise ValueError('description must be longer')
      return v

   @field_validator('price')
   def validator_price(cls, v):
      if v == 0:
         raise ValueError('price can\'t be 0')
      return v

   @field_validator('topic')
   def validator_topic(cls, v):
      if len(v) <= 2:
         raise ValueError('topic must be longer')
      return v

   @field_validator('material')
   def validator_material(cls, v):
      if len(v) <= 2:
         raise ValueError('material must be longer')
      return v



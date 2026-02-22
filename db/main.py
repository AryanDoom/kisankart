#TODO: Use GeoJson instead of Location class
import uuid
import datetime
import asyncio
import os

from dotenv import load_dotenv
load_dotenv()

from PIL import Image
from pymongo import MongoClient

uri = f'mongodb+srv://{os.getenv("MONGO_DB_USERNAME")}:{os.getenv("MONGO_DB_PASSWORD")}@test.ueiwc3g.mongodb.net/?appName=test'
DB_CLIENT = MongoClient(uri, uuidRepresentation="standard")

try:
    DB_CLIENT.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = DB_CLIENT["dev"]
FARMERS_DB = db['farmers']
PRODUCT_DB = db['product']
USER_CREDS_DB = db['user_creds']

class Location:
    def __init__(self,latitude:float,longitude:float):
        self.latitude = latitude
        self.longitude = longitude

class Farmer:
    def __init__(self,name:str,phone_num:int,location:Location,profile_pic:Image,bio:str):
        """
            Farmer object.
            Stores the details of the farmer which will be put in the database as is. 
        """
        self.name = name
        self.phone_number = phone_num
        self.location = location
        self.bio = bio
        self.profile_picture = profile_pic
        self.id = str(uuid.uuid4())

    @property
    def __dict__(self):
        return {"_id":self.id,"name":self.name, "phone_number":self.phone_number, "location":self.location.__dict__,"bio":self.bio,"profile_picture":self.profile_picture.tobytes()}

    def __str__(self):
        return str(self.__dict__)
     
    def __repr(self):
        return self.__dict__
        

class Product:
    def __init__(self,farmer_id:uuid.UUID,name:str,location:Location,price_per_kg:float,stock_in_kg:int,product_image:Image,exp_date:int):
        self.id = str(uuid.uuid4())
        self.farmer_id = farmer_id
        self.name = name
        self.location = location
        self.price_per_kg = price_per_kg
        self.stock_in_kg = stock_in_kg
        self.image = product_image
        self.exp_date = exp_date 

    @staticmethod
    def from_dict(d):
        import io
        img_bytes = io.BytesIO(d['image'])
        # TODO: Fix images
        o = Product(d['farmer_id'],d['name'],Location(**d['location']),d['price_per_kg'],d['stock_in_kg'],Image.new("RGB",(10,10)),d['exp_date'])
        return o

    @property
    def __dict__(self):
        return {"_id":self.id,"farmer_id":self.farmer_id,"name":self.name, "location":self.location.__dict__,"price_per_kg":self.price_per_kg,"image":self.image.tobytes(),"price_per_kg":self.price_per_kg,"stock_in_kg":self.stock_in_kg,"exp_date":self.exp_date}

    def __str__(self):
        return str(self.__dict__)
     
    def __repr(self):
        return self.__dict__

class DuplicateEntry(Exception):
    def __init__(self, message, trying,existing): 
        super().__init__(message)
            
        self.trying = trying
        self.existing = existing

class OrderItem:
    def __init__(self,product_id:uuid.UUID,qty:int):
        self.product_id = product_id
        self.qty = qty

class Customer:
    def __init__(self,name:str,phone_num:int,loc:Location,current_bucket:[OrderItem]):
        self.name = name
        self.id = uuid.uuid4()
        self.phone_number = phone_num
        self.location = loc
        self.current_bucket = current_bucket

    def __dict__(self):
        return {"_id":self.id,"name":self.name,"phone_number":self.phone_number,"location":self.location}

    def from_dict(d):
        c = Customer(d['name'],d['phone_number'],d['location'])
        c.id = d['_id']
        return c

async def try_add_customer_to_db(customer:Customer):
    if c:=CUSTOMERS_DB.find_one({"_id":customer.id}):
        raise DuplicateEntry(f"Customer with id {customer.id} already exists.",customer,c)
    CUSTOMERS_DB.insert_one(customer.__dict__)

def try_add_farmer_to_db(farmer:Farmer):
    """
    JUST ADDS TO THE DB WITHOUT CHECKING FOR AUTHENTICATION
    Returns an exception if the farmer couldn't be added to the database
    """
    if f:= FARMERS_DB.find_one({"_id":farmer.id}):
        raise DuplicateEntry(f"Farmer with id {farmer.id} already exists.",farmer,f)

    FARMERS_DB.insert_one(farmer.__dict__)

async def get_products_from_farmer(farmer:Farmer,get_expired:bool=True):
    fid = farmer.id
    filter_ = {"_id":fid}
    if not get_expired:
        filter_["exp_date"] = {"$gt":datetime.datetime.now().timestamp()}
    print(filter_)
    res = PRODUCT_DB.find(filter_)
    out = []
    for p in res:
        print(p)
        out.append(Product.from_dict(p))
    
    return out

async def add_product(p:Product):
    # TODO: check if farmer exists
    if f:= PRODUCT_DB.find_one({"_id":p.id}):
        raise DuplicateEntry(f"product with id {p.id} already exists.",None,None)
    PRODUCT_DB.insert_one(p.__dict__)

async def doshidd():
    """c
    farmer.id = "1"
    await try_add_farmer_to_db(farmer)
    """
    p = Product(uuid.uuid4(),"balls",Location(1,1),12.0,12.0,Image.new('RGB',(10,10)),int(datetime.datetime.now().timestamp()))
    p.farmer_id = '1'
    farer = Farmer("balls",123456789,Location(12.0,12.0),Image.new('RGB',(10,10)),"yoo whaddup")
    farer.id = '1'
    print(str((await get_products_from_farmer(farer))[0]))

asyncio.run(doshidd())

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
BUCKETS_DB = db['buckets']
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

class ProductNotFound(Exception):
    def __init__(self, message, trying,existing): 
        super().__init__(message)
            
        self.trying = trying
        self.existing = existing

class OrderItem:
    def __init__(self,product_id:uuid.UUID,qty:int):
        self.product_id = product_id
        self.qty = qty
        self.order_item_id = uuid.uuid4()

    def __dict__(self):
        return {"product_id":self.product_id,"qty":self.qty,"_id":self.order_item_id}

    @staticmethod
    def from_dict(d):
        a = OrderItem(d["product_id"],d["qty"])
        a.order_item_id = d['_id']
        return a


class Order:
    def __iter__(self,customer_id:uuid.UUID,orders:[OrderItem]=[]):
        self.customer_id = customer_id
        self.items = orders
        self.order_id  = uuid.uuid4()

    def add_item(self,order_item:OrderItem):
        for item in self.items:
            if item.product_id == order_item.product_id:
                item.qty += order_item.qty
                return
        self.items.append(order_item)

    def __dict__(self):
        return {"customer_id":self.customer_id,"items":[x.__dict__ for x in self.items],"_id":self.order_id}

    @staticmethod
    def from_dict(d):
        a = OrderItem(d["customer_id"])
        a.order_id = d["_id"]
        for x in d.items:
            a.items.append(OrderItem.from_dict(x))
        return a

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

def try_add_customer_to_db(customer:Customer):
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

def get_products_from_farmer(farmer:Farmer,get_expired:bool=True):
    fid = farmer.id
    filter_ = {"farmer_id":fid}
    print(filter_)
    if not get_expired:
        filter_["exp_date"] = {"$gt":datetime.datetime.now().timestamp()}

    res = PRODUCT_DB.find(filter_)
    out = []
    for p in res:
        print(p)
        out.append(Product.from_dict(p))
    
    return out

def add_product(p:Product):
    # TODO: check if farmer exists
    if f:= PRODUCT_DB.find_one({"_id":p.id}):
        raise DuplicateEntry(f"product with id {p.id} already exists.",None,None)
    PRODUCT_DB.insert_one(p.__dict__)

def get_bucket(customer_id:uuid.UUID):
    if f:=BUCKETS_DB.find_one({"_id":p.id}):
        return Order.from_dict(f)
    return None

def add_to_bucket(customer_id:uuid.UUID,item:OrderItem):
    b = get_bucket(customer_id)
    if not b:
        b = Order(customer_id)
    b.add_item(item)
    BUCKETS_DB.insert_one(b.__dict__)

def doshidd():
    """Test adding a farmer and a product to the database"""

    # Create test objects
    test_location = Location(1.2345, 6.7890)  # Random coordinates for location
    test_farmer = Farmer(
        name="John Doe",
        phone_num=1234567890,
        location=test_location,
        profile_pic=Image.new("RGB", (100, 100)),  # Placeholder image
        bio="A passionate farmer!"
    )

    # Try adding the farmer to the database
    try:
        try_add_farmer_to_db(test_farmer)
        print(f"Farmer {test_farmer.name} added successfully!")
    except DuplicateEntry as e:
        print(f"Error adding farmer: {e.message}")

    # Create a product for the farmer
    test_product = Product(
        farmer_id=test_farmer.id,
        name="Fresh Tomatoes",
        location=test_location,
        price_per_kg=5.0,
        stock_in_kg=100,
        product_image=Image.new("RGB", (10, 10)),  # Placeholder image
        exp_date=int(datetime.datetime.now().timestamp()) + 3600  # 1 hour from now
    )

    # Try adding the product to the database
    try:
        add_product(test_product)
        print(f"Product {test_product.name} added successfully!")
    except DuplicateEntry as e:
        print(f"Error adding product: {e.message}")

    # Optionally, you could also test fetching products from the farmer
    products = get_products_from_farmer(test_farmer)
    print(test_farmer.id,products)
    for product in products:
        print(f"Product found: {product}")

doshidd()

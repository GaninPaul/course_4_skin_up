import random
import jwt
import datetime
from models import User_Pydantic, Users, PhotosCollection, PhotoParams, PhotoAnalysis
from tortoise import Tortoise


async def create_users(count=4):
    for _ in range(count):
        token = jwt.encode({"time": str(datetime.datetime.now())},
                           "secret", algorithm="HS256")
        await Users.create(token=token)


async def create_photos_сollections():
    await PhotosCollection.create(photo1="examples/f1/top.png", photo2="examples/f1/bottom.png", photo3="examples/f1/left.png", photo4="examples/f1/right.png")
    await PhotosCollection.create(photo1="examples/f2/top.png", photo2="examples/f2/bottom.png", photo3="examples/f2/left.png", photo4="examples/f2/right.png")
    await PhotosCollection.create(photo1="examples/f3/top.png", photo2="examples/f3/bottom.png", photo3="examples/f3/left.png", photo4="examples/f3/right.png")


async def create_photos_params(count=3):
    for _ in range(count*4):
        await PhotoParams.create(reflection=str(random.randint(0, 9)), points=str(random.randint(0, 99)), wrinkles=str(random.randint(0, 99)))


async def create_photos_analysis(count=3):
    print("todo")
    # for PhotosCollection_id in range(PhotosCollection.all().count()):
    # for PhotoParams_id in range(PhotoParams.all().count()):
    # await PhotoAnalysis.create(photos_collection=PhotosCollection_id, photo1_params=PhotoParams_id), wrinkles=str(random()*100))


async def run():
    await Tortoise.init(
        db_url="postgres://root:1234@localhost:5432/vkr",
        modules={"models": ["models"]},
    )
    await create_users()
    await create_photos_сollections()
    # await create_photos_params()

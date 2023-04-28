import asyncio
from fixtures import run
from typing import List
import os
import uuid
import json

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from typing_extensions import Annotated
from models import Resurch_Pydantic, Resurchs, PhotosCollection, Users, Recommendations
from fastapi.responses import RedirectResponse

from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise

from utils.crop_face import crop_face
from utils.points.detect_acne import detect_acne
from utils.reflection import detect_reflection
from utils.wrinkles import face_wrinkles


app = FastAPI()


def formatPath(path):
    return path.replace(' ', '').replace('\t', '').replace('\n', '')


async def async_crop_face(path):
    crop_face(path)


async def calc_in_bg(resurch_id, path, files):
    class Result():
        def __init__(self, filename, acne, withoutAcne, reflection_count, wrinkles_count):
            self.filename = filename
            self.acne = acne
            self.withoutAcne = withoutAcne
            self.reflection_count = reflection_count
            self.wrinkles_count = wrinkles_count

    face_wrinkles_res = face_wrinkles(path, files)
    face_acnes_res = detect_acne(path, files)
    face_reflections_res = detect_reflection(path, files)
    # face_wrinkles_json=json.dumps([obj.__dict__ for obj in face_wrinkles_res])
    # face_acnes_json=json.dumps([obj.__dict__ for obj in face_acnes_res])
    # face_reflections_json=json.dumps([obj.__dict__ for obj in face_reflections_res])
    resultList = []
    for item in face_wrinkles_res:
        print("-----------"+item.filename)
        reflection = next(
            ref for ref in face_reflections_res if ref.filename == item.filename)
        acne2 = next(
            ac for ac in face_acnes_res if ac.filename == item.filename)
        res = Result(filename=str(item.filename), wrinkles_count=str(item.wrinkles_count),
                     reflection_count=str(reflection.reflection_count), acne=str(acne2.acne), withoutAcne=str(acne2.withoutAcne))
        resultList.append(res)
    print("-----------")
    # print("face_wrinkles_res: "+str(len(face_wrinkles_res)))
    # print("face_acnes_res: "+str(len(face_acnes_res)))
    res_json = json.dumps([obj.__dict__ for obj in resultList])
    print(res_json)

    # async def async_function():
    resurch = await Resurchs.get(id=resurch_id)
    await Recommendations.create(resurch=resurch, recommendation=res_json)
    # asyncio.run(async_function())


@app.get("/uploadfiles/")
async def redirect():
    return RedirectResponse("/")


@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile],  background_tasks: BackgroundTasks):
    users = await Users.all()
    if len(users) <= 0:
        raise HTTPException(
            status_code=404, detail=f"Users not found")
    user = users[0]
    resurch_id = uuid.uuid4()
    os.mkdir("examples/"+str(resurch_id))

    for file in files:
        with open("examples/"+str(resurch_id)+"/" + str(user.id)+formatPath(file.filename), 'wb') as out_file:
            content = await file.read()
            out_file.write(content)
    if len(files) >= 4:
        photos_collection = await PhotosCollection.create(
            photo1="examples/"+str(resurch_id)+"/" +
            str(user.id)+formatPath(files[0].filename),
            photo2="examples/"+str(resurch_id)+"/" +
            str(user.id)+formatPath(files[1].filename),
            photo3="examples/"+str(resurch_id)+"/" +
            str(user.id)+formatPath(files[2].filename),
            photo4="examples/"+str(resurch_id)+"/" +
            str(user.id)+formatPath(files[3].filename),)
        resurch = await Resurchs.create(id=resurch_id, user=user, photos_collection=photos_collection)

        os.mkdir("examples/"+str(resurch_id)+"/cropped")

        to_croped_files = [str(user.id)+formatPath(files[0].filename),
                           str(user.id)+formatPath(files[1].filename),
                           str(user.id)+formatPath(files[2].filename),
                           str(user.id)+formatPath(files[3].filename)]

        croped_files = [str(user.id)+formatPath(files[0].filename)+"_face.png",
                        str(user.id)+formatPath(files[1].filename)+"_face.png",
                        str(user.id)+formatPath(files[2].filename)+"_face.png",
                        str(user.id)+formatPath(files[3].filename)+"_face.png"]

        crop_face("examples/"+str(resurch_id)+"/", to_croped_files)
        # face_wrinkles_res = face_wrinkles(
        #     "examples/"+str(resurch_id)+"/cropped/", croped_files)
        # face_acnes_res = detect_acne(
        #     "examples/"+str(resurch_id)+"/cropped/", croped_files)
        # background_tasks.add_task(
        #     calc_in_bg, resurch_id=resurch_id, path="/Users/pganin/Documents/vkr/src/examples/"+str(resurch_id)+"/cropped/", files=croped_files)
        asyncio.create_task(calc_in_bg(
            resurch_id=resurch_id, path="/Users/pganin/Documents/vkr/src/examples/"+str(resurch_id)+"/cropped/", files=croped_files))
        return {
            "filenames": [file.filename for file in files],
            "photos_collection": photos_collection.id,
            "user": user.id,
            "resurch": resurch.id}
    else:
        return {"error": "files.count() < 4"}


@app.get("/status/{process_id}")
async def get_process_status(process_id: str):
    resurch = await Resurchs.get(id=process_id)
    if not resurch:
        return {"error": "resurch not found"}
    recommendation = await Recommendations.get(resurch=resurch.id)
    return {"recomendation": recommendation.recommendation}


# @app.get(
#     "/user/{user_id}", response_model=User_Pydantic, responses={404: {"model": HTTPNotFoundError}}
# )
# async def get_user(user_id: int):
#     # if not deleted_count:
#     #     raise HTTPException(
#     #         status_code=404, detail=f"User {user_id} not found")
#     return await User_Pydantic.from_queryset_single(Users.get(id=user_id))


@app.get("/")
async def main():
    content = """
<body>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)

register_tortoise(
    app,
    db_url="postgres://root:1234@localhost:5432/vkr",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

if __name__ == "__main__":
    asyncio.run(run())

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class RecommendedProducts(models.Model):
    id = fields.UUIDField(pk=True)
    recommendation = fields.ForeignKeyField(
        'models.Recommendations', related_name='products')
    product_link = fields.TextField(max_length=1024, null=True)


RecommendedProducts_Pydantic = pydantic_model_creator(
    RecommendedProducts, name="RecommendedProducts")
RecommendedProductsIn_Pydantic = pydantic_model_creator(
    RecommendedProducts, name="RecommendedProductsIn", exclude_readonly=True)


class Recommendations(models.Model):
    id = fields.UUIDField(pk=True)
    resurch = fields.ForeignKeyField(
        'models.Resurchs', related_name='recommendations')
    recommendation = fields.JSONField(null=True)


Recommendations_Pydantic = pydantic_model_creator(
    Recommendations, name="Recommendations")
RecommendationsIn_Pydantic = pydantic_model_creator(
    Recommendations, name="RecommendationsIn", exclude_readonly=True)


class UserProblems(models.Model):
    id = fields.UUIDField(pk=True)
    problem = fields.ForeignKeyField(
        'models.Problems', related_name='problems')
    resurch = fields.ForeignKeyField(
        'models.Resurchs', related_name='problems')


Problems_Pydantic = pydantic_model_creator(UserProblems, name="UserProblems")
ProblemsIn_Pydantic = pydantic_model_creator(
    UserProblems, name="UserProblemsIn", exclude_readonly=True)


class PhotoParams(models.Model):
    id = fields.UUIDField(pk=True)
    reflection = fields.TextField(max_length=1024, null=True)
    points = fields.TextField(max_length=1024, null=True)
    wrinkles = fields.TextField(max_length=1024, null=True)


PhotoParams_Pydantic = pydantic_model_creator(PhotoParams, name="PhotoParams")
PhotoParamsIn_Pydantic = pydantic_model_creator(
    PhotoParams, name="PhotoParamsIn", exclude_readonly=True)


class PhotosCollection(models.Model):
    id = fields.UUIDField(pk=True)
    photo1 = fields.TextField(max_length=1024, null=True)
    photo2 = fields.TextField(max_length=1024, null=True)
    photo3 = fields.TextField(max_length=1024, null=True)
    photo4 = fields.TextField(max_length=1024, null=True)


PhotoCollection_Pydantic = pydantic_model_creator(
    PhotosCollection, name="PhotoCollection")
PhotoCollectionIn_Pydantic = pydantic_model_creator(
    PhotosCollection, name="PhotoCollectionIn", exclude_readonly=True)


class PhotoAnalysis(models.Model):
    id = fields.UUIDField(pk=True)
    photos_collection = fields.ForeignKeyField(
        "models.PhotosCollection", related_name="analytics"
    )
    photo1_params = fields.ForeignKeyField(
        'models.PhotoParams', related_name='analytics1')
    photo2_params = fields.ForeignKeyField(
        'models.PhotoParams', related_name='analytics2')
    photo3_params = fields.ForeignKeyField(
        'models.PhotoParams', related_name='analytics3')
    photo4_params = fields.ForeignKeyField(
        'models.PhotoParams', related_name='analytics4')


PhotoAnalysis_Pydantic = pydantic_model_creator(
    PhotoAnalysis, name="PhotoAnalysis")
PhotoAnalysisIn_Pydantic = pydantic_model_creator(
    PhotoAnalysis, name="PhotoAnalysisIn", exclude_readonly=True)


class Problems(models.Model):
    id = fields.UUIDField(pk=True)
    photo_params = fields.ForeignKeyField(
        'models.PhotoParams', related_name='problems')
    conclusion = fields.TextField(max_length=128, null=True)
    is_example = fields.BooleanField(null=False)


Problems_Pydantic = pydantic_model_creator(Problems, name="Problems")
ProblemsIn_Pydantic = pydantic_model_creator(
    Problems, name="ProblemsIn", exclude_readonly=True)


#
class Users(models.Model):
    id = fields.UUIDField(pk=True)
    token = fields.TextField(max_length=1024)


User_Pydantic = pydantic_model_creator(Users, name="Users")
UserIn_Pydantic = pydantic_model_creator(
    Users, name="UsersIn", exclude_readonly=True)


class Resurchs(models.Model):
    id = fields.UUIDField(pk=True)
    user: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        "models.Users", related_name="resurches"
    )
    photos_collection: fields.ForeignKeyRelation["PhotosCollection"] = fields.ForeignKeyField(
        "models.PhotosCollection", related_name="resurches", null=True
    )


Resurch_Pydantic = pydantic_model_creator(Resurchs, name="Resurchs")
ResurchIn_Pydantic = pydantic_model_creator(
    Resurchs, name="ResurchsIn", exclude_readonly=True)

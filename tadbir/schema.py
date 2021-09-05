import graphene
from graphene_django import DjangoObjectType

from basic.schema import BasicQuery, DeletePazireshMutation, UserNode, UploadTest, CreatePazireshMutation, \
    EditPazireshMutation, ChangePasswordMutation
import graphql_jwt


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserNode)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)


class Mutation(graphene.ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    create_paziresh_mutation = CreatePazireshMutation.Field()
    edit_paziresh_mutation = EditPazireshMutation.Field()
    change_password_mutation = ChangePasswordMutation.Field()
    upload_test_mutation = UploadTest.Field()
    delete_paziresh_mutation = DeletePazireshMutation.Field()


class Query(BasicQuery, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)

from datetime import datetime

import django_filters
import graphene
from graphene import relay, ObjectType, List
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload
from graphql_relay import from_global_id
from .models import *


class ExtendedConnection(graphene.relay.Connection):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, node=None, name=None, **options):
        result = super().__init_subclass_with_meta__(node=node, name=name, **options)
        cls._meta.fields["total_count"] = graphene.Field(
            type=graphene.Int,
            name="totalCount",
            description="Number of items in the queryset.",
            required=True,
            resolver=cls.resolve_total_count,
        )
        return result

    def resolve_total_count(self, *_) -> int:
        return self.iterable.count()


class RoleNode(DjangoObjectType):
    class Meta:
        model = Role
        filter_fields = ['id']
        interfaces = (relay.Node,)


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {'id', 'username', 'roles__name'}

    @property
    def qs(self):
        if self.request.user:
            print(self.request.user.id)
            roles = self.request.user.roles.all()
            for role in roles:
                if role.name == 'bimegozar':
                    print(self.request.user.bimegozar)
                    return super(UserFilter, self).qs.filter(
                        bimeshavanadegharardad__gharardad__bimegozar=self.request.user.bimegozar)
        return super(UserFilter, self).qs


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filterset_class = UserFilter
        interfaces = (relay.Node,)


class BimeGozarNode(DjangoObjectType):
    class Meta:
        model = BimeGozar
        filter_fields = ['id', 'name', 'code']
        interfaces = (relay.Node,)


class BimeGarNode(DjangoObjectType):
    class Meta:
        model = BimeGar
        filter_fields = ['id', 'name', 'code']
        interfaces = (relay.Node,)


class HazineCategoryNode(DjangoObjectType):
    class Meta:
        model = HazineCategory
        filter_fields = ['id', 'name', 'code']
        interfaces = (relay.Node,)


class HazineNode(DjangoObjectType):
    class Meta:
        model = Hazine
        filter_fields = ['id', 'name', 'code']
        interfaces = (relay.Node,)


class GharardadNode(DjangoObjectType):
    class Meta:
        model = Gharardad
        filter_fields = ['id', 'name', 'code', 'expire_date']
        interfaces = (relay.Node,)

    def resolve_file(self, info):
        """Resolve product image absolute path"""
        if self.file:
            self.file = info.context.build_absolute_uri(self.file.url)
        return self.file


class HazineGharardadNode(DjangoObjectType):
    class Meta:
        model = HazineGharardad
        filter_fields = ['id']
        interfaces = (relay.Node,)


class BimeShavanadeGharardadNode(DjangoObjectType):
    class Meta:
        model = BimeShavanadeGharardad
        filter_fields = ['id']
        interfaces = (relay.Node,)


class BimeShavandeGharardadHazineNode(DjangoObjectType):
    class Meta:
        model = BimeShavandeGharardadHazine
        filter_fields = ['id']
        interfaces = (relay.Node,)


class PazireshFilter(django_filters.FilterSet):
    class Meta:
        model = Paziresh
        fields = {'id': ['exact'], 'date': [
            'exact'], 'status': ['exact', 'in']}

    @property
    def qs(self):
        if self.request.user:
            roles = self.request.user.roles.all()
            for role in roles:
                if role.name == 'bimegozar':
                    return super(PazireshFilter, self).qs.filter(
                        bimeshavande_gharardad_hazine__bimeshavande_gharardad__gharardad__bimegozar=self.request.user.bimegozar)
        return super(PazireshFilter, self).qs


class PazireshNode(DjangoObjectType):
    class Meta:
        model = Paziresh
        filterset_class = PazireshFilter
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_file(self, info):
        """Resolve product image absolute path"""
        if self.file:
            self.file = info.context.build_absolute_uri(self.file.url)
        return self.file


class PazireshFileNode(DjangoObjectType):
    class Meta:
        model = PazireshFile
        filter_fields = ['id']
        interfaces = (relay.Node,)

    def resolve_file(self, info):
        """Resolve product image absolute path"""
        if self.file:
            self.file = info.context.build_absolute_uri(self.file.url)
        return self.file


class BasicQuery(graphene.ObjectType):
    bimegozar = relay.Node.Field(BimeGozarNode)
    all_bimegozars = DjangoFilterConnectionField(BimeGozarNode)

    bimegar = relay.Node.Field(BimeGarNode)
    all_bimegars = DjangoFilterConnectionField(BimeGarNode)

    hazinecategory = relay.Node.Field(HazineCategoryNode)
    all_hazinecategories = DjangoFilterConnectionField(HazineCategoryNode)

    hazine = relay.Node.Field(HazineNode)
    all_hazines = DjangoFilterConnectionField(HazineNode)

    gharardad = relay.Node.Field(GharardadNode)
    all_gharardads = DjangoFilterConnectionField(GharardadNode)

    hazinegharardad = relay.Node.Field(HazineGharardadNode)
    all_hazinegharardads = DjangoFilterConnectionField(HazineGharardadNode)

    bimeshavanadegharardad = relay.Node.Field(BimeShavanadeGharardadNode)
    all_bimeshavandegharardads = DjangoFilterConnectionField(
        BimeShavanadeGharardadNode)

    bimeshavandegharardadhazine = relay.Node.Field(
        BimeShavandeGharardadHazineNode)
    all_bimeshavandegharardadhazines = DjangoFilterConnectionField(
        BimeShavandeGharardadHazineNode)

    paziresh = relay.Node.Field(PazireshNode)
    all_pazireshes = DjangoFilterConnectionField(PazireshNode)

    pazireshfile = relay.Node.Field(PazireshFileNode)
    all_pazireshfiles = DjangoFilterConnectionField(PazireshFileNode)

    user = relay.Node.Field(UserNode)
    all_users = DjangoFilterConnectionField(UserNode)

    role = relay.Node.Field(RoleNode)
    all_roles = DjangoFilterConnectionField(RoleNode)


# MUTATIONS
class CreatePazireshMutation(graphene.Mutation):
    class Arguments:
        files = Upload()
        bime_shavande = graphene.ID()
        hazine = graphene.ID()
        gharardad = graphene.ID()
        date = graphene.String()
        hazine_darkhasti = graphene.Int()
        shomare_nezam_pezeshki = graphene.String()
        markaz_darmani = graphene.String()

    success = graphene.Boolean()
    paziresh = graphene.Field(PazireshNode)
    error = graphene.String()

    @classmethod
    def mutate(cls, root, info, files, bime_shavande, hazine, gharardad, date, hazine_darkhasti,
               shomare_nezam_pezeshki='',
               markaz_darmani='', **kwargs):
        bime_shavande_object = User.objects.get(
            pk=from_global_id(bime_shavande)[1])
        gharardad_object = Gharardad.objects.get(
            pk=from_global_id(gharardad)[1])
        hazine_object = Hazine.objects.get(pk=from_global_id(hazine)[1])
        bime_shavande_gharardad = BimeShavandeGharardadHazine.objects.filter(
            bimeshavande_gharardad__bimeshavande=bime_shavande_object,
            bimeshavande_gharardad__gharardad=gharardad_object, hazine=hazine_object).first()
        # try to create a paziresh and catch errors in a message
        try:
            paziresh = Paziresh.objects.create(
                bimeshavande_gharardad_hazine=bime_shavande_gharardad,
                date=date,
                hazine_darkhasti=hazine_darkhasti,
                shomare_nezam_pezeshki=shomare_nezam_pezeshki,
                markaz_darmani=markaz_darmani)
            # if there is a file, save it
            if files:
                for file in files:
                    PazireshFile.objects.create(
                        paziresh=paziresh, file=file)
            success = True
            error = ''
        except Exception as e:
            success = False
            paziresh = None
            error = str(e)
        paziresh.create_file()
        return CreatePazireshMutation(success=success, paziresh=paziresh, error=error)


class EditPazireshMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        hazine_darkhasti = graphene.Int()
        hazine = graphene.ID()
        hazine_taeidi = graphene.Int()
        bime_paye = graphene.Boolean()
        arzyab_message = graphene.String()
        profile_type = graphene.String()
        profile_id = graphene.ID()
        status = graphene.Boolean()
        eslah = graphene.Boolean()

    success = graphene.Boolean()
    paziresh = graphene.Field(PazireshNode)

    @classmethod
    def mutate(cls, root, info, status, id, hazine_darkhasti, hazine, hazine_taeidi, bime_paye, arzyab_message,
               profile_type, profile_id, eslah, **kwargs):
        paziresh = Paziresh.objects.get(pk=from_global_id(id)[1])
        if not paziresh.bimeshavande_gharardad_hazine.hazine.id == from_global_id(hazine)[1]:
            paziresh.bimeshavande_gharardad_hazine.hazine.id = from_global_id(hazine)[
                1]
        if status:
            paziresh.hazine_darkhasti = hazine_darkhasti
            paziresh.hazine_taeidi = hazine_taeidi
            paziresh.bime_paye = bime_paye
            paziresh.arzyab_message = arzyab_message
            if profile_type == "karshenas":
                paziresh.status = "waitforarzyab"
                paziresh.karshenas = User.objects.get(
                    pk=from_global_id(profile_id)[1])
            else:
                last_status = paziresh.status
                paziresh.status = "accepted"
                paziresh.arzyab = User.objects.get(
                    pk=from_global_id(profile_id)[1])
                if last_status != "accepted" and paziresh.bimeshavande_gharardad_hazine.personal_saghf > -1:
                    paziresh.bimeshavande_gharardad_hazine.personal_saghf = paziresh.bimeshavande_gharardad_hazine.personal_saghf - hazine_taeidi
                    paziresh.bimeshavande_gharardad_hazine.save()
        else:
            last_status = paziresh.status
            paziresh.status = 'rejected'
            if last_status == 'accepted' and paziresh.bimeshavande_gharardad_hazine.personal_saghf > -1:
                paziresh.bimeshavande_gharardad_hazine.personal_saghf = paziresh.bimeshavande_gharardad_hazine.personal_saghf + hazine_taeidi
                paziresh.bimeshavande_gharardad_hazine.save()
            paziresh.arzyab_message = arzyab_message
            if profile_type == "karshenas":
                paziresh.karshenas = User.objects.get(
                    pk=from_global_id(profile_id)[1])
            else:
                paziresh.arzyab = User.objects.get(
                    pk=from_global_id(profile_id)[1])
        paziresh.save()
        if eslah:
            paziresh.status = 'waitforkarshenas'
            paziresh.save()
        return EditPazireshMutation(success=True, paziresh=paziresh)


class DeletePazireshMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        paziresh = Paziresh.objects.get(pk=from_global_id(id)[1])
        paziresh.delete()
        return DeletePazireshMutation(success=True)


class ChangePasswordMutation(graphene.Mutation):
    class Arguments:
        current_password = graphene.String()
        new_password = graphene.String()

    status = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, current_password, new_password):
        user = info.context.user
        status = user.check_password(current_password)
        if status:
            user.set_password(new_password)
            user.save()
        return ChangePasswordMutation(status=status)


class UploadTest(graphene.Mutation):
    class Arguments:
        files = Upload()

    status = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, files):
        for file in files:
            PazireshFile.objects.create(file=file, paziresh_id=1)
        return UploadTest(status=True)

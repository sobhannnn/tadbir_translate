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
                if role.name == 'policyholder':
                    print(self.request.user.policy_holder)
                    return super(UserFilter, self).qs.filter(
                        insuredcontract__contract__policyholder=self.request.user.policy_holder)
        return super(UserFilter, self).qs


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filterset_class = UserFilter
        interfaces = (relay.Node,)


class PolicyHolderNode(DjangoObjectType):
    class Meta:
        model = PolicyHolder
        filter_fields = ['id', 'name', 'code']
        interfaces = (relay.Node,)


class InsurerNode(DjangoObjectType):
    class Meta:
        model = Insurer
        filter_fields = ['id', 'name', 'code']
        interfaces = (relay.Node,)


class CostCategoryNode(DjangoObjectType):
    class Meta:
        model = CostCategory
        filter_fields = ['id', 'name', 'code']
        interfaces = (relay.Node,)


class CostNode(DjangoObjectType):
    class Meta:
        model = Cost
        filter_fields = ['id', 'name', 'code']
        interfaces = (relay.Node,)


class ContractNode(DjangoObjectType):
    class Meta:
        model = Contract
        filter_fields = ['id', 'name', 'code', 'expire_date']
        interfaces = (relay.Node,)

    def resolve_file(self, info):
        """Resolve product image absolute path"""
        if self.file:
            self.file = info.context.build_absolute_uri(self.file.url)
        return self.file


class ContractCostNode(DjangoObjectType):
    class Meta:
        model = ContractCost
        filter_fields = ['id']
        interfaces = (relay.Node,)


class InsuredContractNode(DjangoObjectType):
    class Meta:
        model = InsuredContract
        filter_fields = ['id']
        interfaces = (relay.Node,)


class TheCostOfInsuredContractNode(DjangoObjectType):
    class Meta:
        model = TheCostOfInsuredContract
        filter_fields = ['id']
        interfaces = (relay.Node,)


class ReceptionFilter(django_filters.FilterSet):
    class Meta:
        model = Reception
        fields = {'id': ['exact'], 'date': [
            'exact'], 'status': ['exact', 'in']}

    @property
    def qs(self):
        if self.request.user:
            roles = self.request.user.roles.all()
            for role in roles:
                if role.name == 'policyholder':
                    return super(ReceptionFilter, self).qs.filter(
                        TheCostOfInsuredContract__insured_contract__contract__policy_holder=self.request.user.policy_holder)
        return super(ReceptionFilter, self).qs


class ReceptionNode(DjangoObjectType):
    class Meta:
        model = Reception
        filterset_class = ReceptionFilter
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_file(self, info):
        """Resolve product image absolute path"""
        if self.file:
            self.file = info.context.build_absolute_uri(self.file.url)
        return self.file


class ReceptionFileNode(DjangoObjectType):
    class Meta:
        model = ReceptionFile
        filter_fields = ['id']
        interfaces = (relay.Node,)

    def resolve_file(self, info):
        """Resolve product image absolute path"""
        if self.file:
            self.file = info.context.build_absolute_uri(self.file.url)
        return self.file


class BasicQuery(graphene.ObjectType):
    policy_holder = relay.Node.Field(PolicyHolderNode)
    all_policy_holders = DjangoFilterConnectionField(PolicyHolderNode)

    insurer = relay.Node.Field(InsurerNode)
    all_insurers = DjangoFilterConnectionField(InsurerNode)

    cost_category = relay.Node.Field(CostCategoryNode)
    all_cost_categories = DjangoFilterConnectionField(CostCategoryNode)

    cost = relay.Node.Field(CostNode)
    all_costs = DjangoFilterConnectionField(CostNode)

    contract = relay.Node.Field(ContractNode)
    all_contracts = DjangoFilterConnectionField(ContractNode)

    contract_cost = relay.Node.Field(ContractCostNode)
    all_contracts_costs = DjangoFilterConnectionField(ContractCostNode)

    insured_contract = relay.Node.Field(InsuredContractNode)
    all_insured_contracts = DjangoFilterConnectionField(
        InsuredContractNode)

    the_cost_of_insured_contract = relay.Node.Field(
        TheCostOfInsuredContractNode)
    all_the_cost_of_insured_contracts = DjangoFilterConnectionField(
        TheCostOfInsuredContractNode)

    reception = relay.Node.Field(ReceptionNode)
    all_receptions = DjangoFilterConnectionField(ReceptionNode)

    reception_file = relay.Node.Field(ReceptionFileNode)
    all_receprion_files = DjangoFilterConnectionField(ReceptionFileNode)

    user = relay.Node.Field(UserNode)
    all_users = DjangoFilterConnectionField(UserNode)

    role = relay.Node.Field(RoleNode)
    all_roles = DjangoFilterConnectionField(RoleNode)


# MUTATIONS
class CreateReceptionMutation(graphene.Mutation):
    class Arguments:
        files = Upload()
        insured = graphene.ID()  # bime shavande
        cost = graphene.ID()   # hazine
        contract = graphene.ID()   # gharardad
        date = graphene.String()
        requested_cost = graphene.Int()   # hazine darkhasty
        shomare_nezam_pezeshki = graphene.String()
        markaz_darmani = graphene.String()

    success = graphene.Boolean()
    reception = graphene.Field(ReceptionNode)
    error = graphene.String()

    @classmethod
    def mutate(cls, root, info, files, insured, cost, contract, date, requested_cost,
               shomare_nezam_pezeshki='',
               markaz_darmani='', **kwargs):
        insured_object = User.objects.get(
            pk=from_global_id(insured)[1])
        contract_object = Contract.objects.get(
            pk=from_global_id(contract)[1])
        cost_object = Cost.objects.get(pk=from_global_id(cost)[1])
        insured_contract = TheCostOfInsuredContract.objects.filter(
            insured_contract__insured=insured_object,
            insured_contract__contract=contract_object, cost=cost_object).first()
        # try to create a paziresh and catch errors in a message
        try:
            reception = Reception.objects.create(
                the_cost_of_insured_contract=insured_contract,
                date=date,
                requested_cost=requested_cost,
                shomare_nezam_pezeshki=shomare_nezam_pezeshki,
                markaz_darmani=markaz_darmani)
            # if there is a file, save it
            if files:
                for file in files:
                    ReceptionFile.objects.create(
                        reception=reception, file=file)
            success = True
            error = ''
        except Exception as e:
            success = False
            reception = None
            error = str(e)
        reception.create_file()
        return CreateReceptionMutation(success=success, reception=reception, error=error)


class EditReceptionMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        requested_cost = graphene.Int()
        cost = graphene.ID()
        verification_cost = graphene.Int()
        basic_insurance = graphene.Boolean()
        valuator_message = graphene.String()
        profile_type = graphene.String()
        profile_id = graphene.ID()
        status = graphene.Boolean()
        edit = graphene.Boolean() # eslah

    success = graphene.Boolean()
    reception = graphene.Field(ReceptionNode)

    @classmethod
    def mutate(cls, root, info, status, id, requested_cost, cost, verification_cost, basic_insurance, valuator_message,
               profile_type, profile_id, edit, **kwargs):
        reception = Reception.objects.get(pk=from_global_id(id)[1])
        if not reception.the_cost_of_insured_contract.cost.id == from_global_id(cost)[1]:
            reception.the_cost_of_insured_contract.cost.id = from_global_id(cost)[
                1]
        if status:
            reception.requested_cost = requested_cost
            reception.verification_cost = verification_cost
            reception.basic_insurance = basic_insurance
            reception.valuator_message = valuator_message
            if profile_type == "expert":
                reception.status = "awaiting valuator approval"
                reception.expert = User.objects.get(
                    pk=from_global_id(profile_id)[1])
            else:
                last_status = reception.status
                reception.status = "accepted"
                reception.valuator = User.objects.get(
                    pk=from_global_id(profile_id)[1])
                if last_status != "accepted" and reception.the_cost_of_insured_contract.personal_contractـceiling > -1:
                    reception.the_cost_of_insured_contract.personal_contractـceiling = reception.the_cost_of_insured_contract.personal_contractـceiling - verification_cost
                    reception.the_cost_of_insured_contract.save()
        else:
            last_status = reception.status
            reception.status = 'rejected'
            if last_status == 'accepted' and reception.the_cost_of_insured_contract.personal_contractـceiling > -1:
                reception.the_cost_of_insured_contract.personal_contractـceiling = reception.the_cost_of_insured_contract.personal_contractـceiling + verification_cost
                reception.the_cost_of_insured_contract.save()
            reception.valuator_message = valuator_message
            if profile_type == "expert":
                reception.expert = User.objects.get(
                    pk=from_global_id(profile_id)[1])
            else:
                reception.valuator = User.objects.get(
                    pk=from_global_id(profile_id)[1])
        reception.save()
        if edit:
            reception.status = 'awaiting expert approval'
            reception.save()
        return EditReceptionMutation(success=True, reception=reception)


class DeleteReceptionMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        reception = Reception.objects.get(pk=from_global_id(id)[1])
        reception.delete()
        return DeleteReceptionMutation(success=True)


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
            ReceptionFile.objects.create(file=file, reception_id=1)
        return UploadTest(status=True)

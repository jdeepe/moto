"""Handles incoming route53resolver requests/responses."""
import json

from moto.core.exceptions import InvalidToken
from moto.core.responses import BaseResponse
from moto.route53resolver.exceptions import InvalidNextTokenException
from moto.route53resolver.models import route53resolver_backends
from moto.route53resolver.validations import validate_args


class Route53ResolverResponse(BaseResponse):
    """Handler for Route53Resolver requests and responses."""

    @property
    def route53resolver_backend(self):
        """Return backend instance specific for this region."""
        return route53resolver_backends[self.region]

    def associate_resolver_rule(self):
        """Associate a Resolver rule with a VPC."""
        resolver_rule_id = self._get_param("ResolverRuleId")
        name = self._get_param("Name")
        vpc_id = self._get_param("VPCId")
        resolver_rule_association = self.route53resolver_backend.associate_resolver_rule(
            region=self.region,
            resolver_rule_id=resolver_rule_id,
            name=name,
            vpc_id=vpc_id,
        )
        return json.dumps(
            {"ResolverRuleAssociation": resolver_rule_association.description()}
        )

    def create_resolver_endpoint(self):
        """Create an inbound or outbound Resolver endpoint."""
        creator_request_id = self._get_param("CreatorRequestId")
        name = self._get_param("Name")
        security_group_ids = self._get_param("SecurityGroupIds")
        direction = self._get_param("Direction")
        ip_addresses = self._get_param("IpAddresses")
        tags = self._get_param("Tags", [])
        resolver_endpoint = self.route53resolver_backend.create_resolver_endpoint(
            region=self.region,
            creator_request_id=creator_request_id,
            name=name,
            security_group_ids=security_group_ids,
            direction=direction,
            ip_addresses=ip_addresses,
            tags=tags,
        )
        return json.dumps({"ResolverEndpoint": resolver_endpoint.description()})

    def create_resolver_rule(self):
        """Specify which Resolver enpoint the queries will pass through."""
        creator_request_id = self._get_param("CreatorRequestId")
        name = self._get_param("Name")
        rule_type = self._get_param("RuleType")
        domain_name = self._get_param("DomainName")
        target_ips = self._get_param("TargetIps", [])
        resolver_endpoint_id = self._get_param("ResolverEndpointId")
        tags = self._get_param("Tags", [])
        resolver_rule = self.route53resolver_backend.create_resolver_rule(
            region=self.region,
            creator_request_id=creator_request_id,
            name=name,
            rule_type=rule_type,
            domain_name=domain_name,
            target_ips=target_ips,
            resolver_endpoint_id=resolver_endpoint_id,
            tags=tags,
        )
        return json.dumps({"ResolverRule": resolver_rule.description()})

    def delete_resolver_endpoint(self):
        """Delete a Resolver endpoint."""
        resolver_endpoint_id = self._get_param("ResolverEndpointId")
        resolver_endpoint = self.route53resolver_backend.delete_resolver_endpoint(
            resolver_endpoint_id=resolver_endpoint_id,
        )
        return json.dumps({"ResolverEndpoint": resolver_endpoint.description()})

    def delete_resolver_rule(self):
        """Delete a Resolver rule."""
        resolver_rule_id = self._get_param("ResolverRuleId")
        resolver_rule = self.route53resolver_backend.delete_resolver_rule(
            resolver_rule_id=resolver_rule_id,
        )
        return json.dumps({"ResolverRule": resolver_rule.description()})

    def disassociate_resolver_rule(self):
        """Remove the association between a Resolver rule and a VPC."""
        vpc_id = self._get_param("VPCId")
        resolver_rule_id = self._get_param("ResolverRuleId")
        resolver_rule_association = self.route53resolver_backend.disassociate_resolver_rule(
            vpc_id=vpc_id, resolver_rule_id=resolver_rule_id,
        )
        return json.dumps(
            {"ResolverRuleAssociation": resolver_rule_association.description()}
        )

    def get_resolver_endpoint(self):
        """Return info about a specific Resolver endpoint."""
        resolver_endpoint_id = self._get_param("ResolverEndpointId")
        resolver_endpoint = self.route53resolver_backend.get_resolver_endpoint(
            resolver_endpoint_id=resolver_endpoint_id,
        )
        return json.dumps({"ResolverEndpoint": resolver_endpoint.description()})

    def get_resolver_rule(self):
        """Return info about a specific Resolver rule."""
        resolver_rule_id = self._get_param("ResolverRuleId")
        resolver_rule = self.route53resolver_backend.get_resolver_rule(
            resolver_rule_id=resolver_rule_id,
        )
        return json.dumps({"ResolverRule": resolver_rule.description()})

    def get_resolver_rule_association(self):
        """Return info about association between a Resolver rule and a VPC."""
        resolver_rule_association_id = self._get_param("ResolverRuleAssociationId")
        resolver_rule_association = self.route53resolver_backend.get_resolver_rule_association(
            resolver_rule_association_id=resolver_rule_association_id
        )
        return json.dumps(
            {"ResolverRuleAssociation": resolver_rule_association.description()}
        )

    def list_resolver_endpoint_ip_addresses(self):
        """Returns list of IP addresses for specified Resolver endpoint."""
        resolver_endpoint_id = self._get_param("ResolverEndpointId")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults", 10)
        validate_args([("maxResults", max_results)])
        try:
            (
                ip_addresses,
                next_token,
            ) = self.route53resolver_backend.list_resolver_endpoint_ip_addresses(
                resolver_endpoint_id=resolver_endpoint_id,
                next_token=next_token,
                max_results=max_results,
            )
        except InvalidToken as exc:
            raise InvalidNextTokenException() from exc

        response = {
            "IpAddresses": ip_addresses,
            "MaxResults": max_results,
        }
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def list_resolver_endpoints(self):
        """Returns list of all Resolver endpoints, filtered if specified."""
        filters = self._get_param("Filters")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults", 10)
        validate_args([("maxResults", max_results)])
        try:
            (
                endpoints,
                next_token,
            ) = self.route53resolver_backend.list_resolver_endpoints(
                filters, next_token=next_token, max_results=max_results
            )
        except InvalidToken as exc:
            raise InvalidNextTokenException() from exc

        response = {
            "ResolverEndpoints": [x.description() for x in endpoints],
            "MaxResults": max_results,
        }
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def list_resolver_rules(self):
        """Returns list of all Resolver rules, filtered if specified."""
        filters = self._get_param("Filters")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults", 10)
        validate_args([("maxResults", max_results)])
        try:
            (rules, next_token) = self.route53resolver_backend.list_resolver_rules(
                filters, next_token=next_token, max_results=max_results
            )
        except InvalidToken as exc:
            raise InvalidNextTokenException() from exc

        response = {
            "ResolverRules": [x.description() for x in rules],
            "MaxResults": max_results,
        }
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def list_resolver_rule_associations(self):
        """Returns list of all Resolver associations, filtered if specified."""
        filters = self._get_param("Filters")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults", 10)
        validate_args([("maxResults", max_results)])
        try:
            (
                associations,
                next_token,
            ) = self.route53resolver_backend.list_resolver_rule_associations(
                filters, next_token=next_token, max_results=max_results
            )
        except InvalidToken as exc:
            raise InvalidNextTokenException() from exc

        response = {
            "ResolverRuleAssociations": [x.description() for x in associations],
            "MaxResults": max_results,
        }
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def list_tags_for_resource(self):
        """Lists all tags for the given resource."""
        resource_arn = self._get_param("ResourceArn")
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        try:
            (tags, next_token) = self.route53resolver_backend.list_tags_for_resource(
                resource_arn=resource_arn,
                next_token=next_token,
                max_results=max_results,
            )
        except InvalidToken as exc:
            raise InvalidNextTokenException() from exc

        response = {"Tags": tags}
        if next_token:
            response["NextToken"] = next_token
        return json.dumps(response)

    def tag_resource(self):
        """Add one or more tags to a specified resource."""
        resource_arn = self._get_param("ResourceArn")
        tags = self._get_param("Tags")
        self.route53resolver_backend.tag_resource(resource_arn=resource_arn, tags=tags)
        return ""

    def untag_resource(self):
        """Removes one or more tags from the specified resource."""
        resource_arn = self._get_param("ResourceArn")
        tag_keys = self._get_param("TagKeys")
        self.route53resolver_backend.untag_resource(
            resource_arn=resource_arn, tag_keys=tag_keys
        )
        return ""

    def update_resolver_endpoint(self):
        """Update name of Resolver endpoint."""
        resolver_endpoint_id = self._get_param("ResolverEndpointId")
        name = self._get_param("Name")
        resolver_endpoint = self.route53resolver_backend.update_resolver_endpoint(
            resolver_endpoint_id=resolver_endpoint_id, name=name,
        )
        return json.dumps({"ResolverEndpoint": resolver_endpoint.description()})

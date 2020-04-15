import ipaddress
from typing import List

from pydantic import BaseModel, Field, validator


def ip_validator(ip):
    """Validate that a value is a valid IP"""
    ipaddress.ip_address(ip)
    return ip


def unique_validator(collection):
    """Validate that a collection contains only unique elements"""
    if isinstance(collection[0], BaseModel):
        # Items should be hashable -> use json string representation
        coll = [i.json() for i in collection]
    else:
        coll = collection

    assert len(list(coll)) == len(set(coll)), "List items must be unique"
    return collection


class IPRange(BaseModel):
    """A range of allowed IPs"""

    min: str = Field(..., description="The minimum IP in the range", example="8.8.8.4")
    max: str = Field(..., description="The maximum IP in the range", example="8.8.8.8")

    _ip_validator = validator("min", "max", pre=True, allow_reuse=True)(ip_validator)

    @validator("min")
    def le_max(cls, v, values):
        if "max" in values:
            assert ipaddress.ip_address(v) <= ipaddress.ip_address(values["max"])
        return v

    @validator("max")
    def ge_min(cls, v, values):
        if "min" in values:
            assert ipaddress.ip_address(v) >= ipaddress.ip_address(values["min"])
        return v


class BotEntry(BaseModel):
    """
    A bot verification entry.

    Should have at least one of fcrdns_hosts, ip_list, ip_ranges, or
    cidr_list specified. If more than one of these is specified, the bot
    must meet ALL the requirements to be considered verified.

    All IPs may be either IPv4 or IPv6.
    """

    name: str = Field(
        ...,
        description=(
            "A unique name for the bot in question. Should match"
            "user_agent.family from the ua-parser project."
        ),
        example="Googlebot",
        min_length=1,
    )
    fcrdns_hosts: List[str] = Field(
        None,
        description=(
            "A list of hosts that the bot's IP may match in a "
            "Forward confirmed reverse DNS (FCrDNS) query. If this key"
            "is present but the list is empty, any host will be "
            "allowed, but FCrDNS verification will still be performed."
            "Items must be unique."
        ),
        example=["google.com", "googlebot.com"],
        min_length=0,
    )
    ip_list: List[str] = Field(
        None,
        description="A whitelist of IPs that the bot may use. Items must be unique.",
        example=["8.8.8.8", "8.8.4.4"],
        min_length=1,
    )
    ip_ranges: List[IPRange] = Field(
        None,
        description="A list of IP ranges that the bot may use. Items must be unique.",
    )
    cidr_list: List[str] = Field(
        None,
        description=(
            "A list of CIDR IP blocks that the bot may use. Items must be unique."
        ),
        example=["8.8.8.0/24"],
        min_length=1,
    )

    _ip_validator = validator("ip_list", each_item=True, allow_reuse=True)(ip_validator)

    _unique_validator = validator(
        "fcrdns_hosts", "ip_list", "ip_ranges", "cidr_list", allow_reuse=True
    )(unique_validator)

    @validator("cidr_list", each_item=True)
    def cidr_validator(cls, v):
        ipaddress.ip_network(v, strict=False)
        return v


class Bottica(BaseModel):
    """The list of all bot verification requirements."""

    bots: List[BotEntry]

    _unique_validator = validator("bots", allow_reuse=True)(unique_validator)

    @validator("bots")
    def unique_names(cls, v):
        """Validate that each bot has a unique name"""
        names = [entry.name for entry in v]
        unique_validator(names)
        return v


class UAParser(BaseModel):
    regex: str
    family_replacement: str = None


class UAPExtras(BaseModel):
    user_agent_parsers: List[UAParser]

from pathlib import Path
from typing import Union, List, Any

import yaml
from ua_parser import user_agent_parser

from bottica.verifiers import fcrdns_hosts, ip_list, ip_ranges, cidr_list


def _load_uap_extras(yaml_path=Path(__file__).parent / "uap_extras.yaml"):
    """
    Load the UAP extras yaml and add the extra parsers to ua_parser

    We do this globally since ua_parser also uses a global list of
    parsers.
    """
    with open(yaml_path, "r") as h:
        uap_extras = yaml.load(h, Loader=yaml.SafeLoader)

    for entry in uap_extras["user_agent_parsers"]:
        user_agent_parser.USER_AGENT_PARSERS.insert(
            0,
            user_agent_parser.UserAgentParser(
                pattern=entry["regex"],
                family_replacement=entry.get("family_replacement"),
            ),
        )


_load_uap_extras()


class Bottica:
    def __init__(
        self,
        yaml_path: Union[Path, str] = Path(__file__).parent / "bottica.yaml",
        max_tries: int = 3,
    ):
        """
        Verify that bots are really who they say they are.

        Provides several methods for verifying bots that are known in
        bottica-core. To add your own verifiers, you can `.load()` an
        additional custom `bottica.yaml`, or simply add new bots to
        self.verifiers. To use only your own verifiers (and not load
        any of the included ones from bottica-core), you can pass
        `yaml_path=None`.

        self.verifiers is a mapping from bot name (case sensitive) to
        one or more verifiers as described in the bottica-core
        specification.

        Example:
        >>> b = Bottica()
        >>> b.verifiers["my_bot"] = {"fcrdns_hosts":["my_website.com"]}

        If the exact name of the bot isn't known, Bottica
        can utilize the `ua-parser` project to try to id a bot from
        its User-Agent string. In order to verify a bot parsed
        from the User-Agent, the parsed `user_agent.family` must be a
        bot name from `self.verifiers`. See `self.parse_ua` for more
        information.

        :param Union[Path, str] yaml_path: The path to `bottica.yaml`
        :param int max_tries: The maximum number of retries for network-
            dependent verification attempts.
        """
        self.verifiers = dict()
        if yaml_path:
            self.load(yaml_path)
        self.max_tries = max_tries

    def load(self, yaml_path: Union[Path, str]) -> None:
        """
        Load a(nother) `bottica.yaml`.

        If one has already been loaded, `self.verifiers` will be updated
        with the new values, adding any missing values and overwriting
        any existing ones.

        :param Union[Path, str] yaml_path: The path to bottica.yaml
        """
        with open(yaml_path) as h:
            self.yaml = yaml.load(h, Loader=yaml.SafeLoader)

        bot_dict = {bot.pop("name"): bot for bot in self.yaml["bots"]}
        self.verifiers.update(bot_dict)

    # TODO: Add LRU cache with adjustable size
    def verify_bot(self, ip: str, botname: str) -> bool:
        """
        Verify a bot by name.

        The bot's name must be present as a key in `self.verifiers`.

        :param str ip: The IP (v4 or v6) to verify
        :param str botname: The name of the bot to verify
        :return: Whether the bot's IP was successfully verified
        """
        bot_verifiers = self.verifiers[botname]

        return all(
            (
                self.verify(ip, verifier, values)
                for verifier, values in bot_verifiers.items()
            )
        )

    @staticmethod
    def parse_ua(user_agent: str) -> str:
        """
        Parse a bot name from a User-Agent string.

        Relies on `ua_parser.user_agent_parser`. To add additional
        bots to be parsed, insert them into the global regex list
        as follows:

        >>> from ua_parser import user_agent_parser
        >>> my_parser = user_agent_parser.UserAgentParser("my_ua_regex", "my_botname")
        >>> user_agent_parser.USER_AGENT_PARSERS.insert(0, my_parser)

        Other settings for ua_parser can be adjusted similarly (see
        https://github.com/ua-parser/uap-python):
        >>> user_agent_parser.MAX_CACHE_SIZE = 2**16

        Parsed botnames must have at least one verifier set in
        `self.verifiers`.

        :param str user_agent: User-Agent string to parse.
        :return: The parsed bot name
        """
        return user_agent_parser.ParseUserAgent(user_agent)["family"]

    def verify_ua(self, ip: str, user_agent: str) -> bool:
        """
        Verify a bot by User-Agent string.

        See `self.parse_ua()` for parsing details.

        :param str ip: The IP (v4 or v6) to verify
        :param str user_agent: The User-Agent of the bot
        :return: Whether the bot's IP was successfully verified
        """
        botname = self.parse_ua(user_agent)
        return self.verify_bot(ip, botname)

    def verify(self, ip: str, verifier: str, values: List[Any]) -> bool:
        """
        Perform an IP verification.

        :param str ip: the IP (v4 or v6) to verify
        :param str verifier: The verifier to use. Must be one of
            "fcrdns_hosts", "ip_list", "ip_ranges", or "cidr_list".
        :param List values: The values for the verifier, as specified
            in the `bottica` schema.

        :examples:
        >>> b = Bottica()
        >>> b.verify("8.8.4.4", "fcrdns_hosts", ["dns.google"])
        True
        >>> b.verify("8.8.8.8", "ip_list", ["8.8.8.8","8.8.4.4"])
        True
        >>> b.verify("8.8.8.8", "ip_ranges", [{"min": "8.8.8.0", "max":"8.8.8.4"}])
        False
        >>> b.verify("8.8.8.8", "cidr_list", ["8.8.8.0/24"])
        True

        :return: Whether the IP successfully verified
        """
        if verifier == "fcrdns_hosts":
            return fcrdns_hosts(ip, allowed_hosts=values, max_tries=self.max_tries)
        elif verifier == "ip_list":
            return ip_list(ip, allowed_ips=values)
        elif verifier == "ip_ranges":
            return ip_ranges(
                ip, allowed_ranges=((rng["min"], rng["max"]) for rng in values)
            )
        elif verifier == "cidr_list":
            return cidr_list(ip, allowed_cidrs=values)
        else:
            raise ValueError("Unknown verifier")

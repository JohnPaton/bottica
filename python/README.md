# Bottica 🤖 ❤️ 🐍 Python

The Python implementation of Bottica.

```pycon
>>> from bottica import Bottica
>>> btca = Bottica()
```

`Bottica` provides the methods to verify an IP according to one of the
[verifiers](../core#-verifiers) provided in [Bottica Core](../core). You can verify a bot:

* 🏷 [By name](#-verify-a-bot-by-name) (e.g. `Googlebot`)
* 📰 [By User-Agent](#-verify-a-bot-by-user-agent) (e.g. `Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)`)

You can also [add your own verifiers](#-add-your-own-verifiers) for bots that
aren't (yet) listed in Bottica Core, and
[perform the verification methods directly](#-verify-an-ip-directly) on IPs.
Bottica supports both IPv4 and IPv6 everywhere.

When you instantiate `Bottica()`, by default it loads the bot list from
Bottica Core. They are available in the `verifiers` dictionary, which is a map
from bot name to one or more verifiers.

```pycon
>>> btca.verifiers["Googlebot"]
{'fcrdns_hosts': ['google.com', 'googlebot.com']}
```

If multiple verifiers are present, the IP must pass all the verification checks
to be considered verified.


## 🏷 Verify a bot by name

In Bottica, bots are identified by name. The names are the `name` property of
each entry in the [Bottica Core list](../core/bottica.yaml). To verify that
traffic from a particular IP belongs to a particular bot, use the `verify_bot()`
method:

```pycon
>>> btca.verify_bot(ip="1.2.3.4", botname="Googlebot")
False
```

`verify_bot()` relies on the bot name being present in the `verifiers` map, so
it will only work for bots from Bottica Core, or any additional bots that you
have [added yourself](#-add-your-own-verifiers).

## 📰 Verify a bot by User-Agent

Usually you suspect traffic to be coming from a particular bot because of its
User-Agent. Bottica tries to align with the [ua-parser](https://github.com/ua-parser/uap-core) project such that User-Agent families
(`user_agent.family`) parsed by ua-parser will correspond to bot names in
Bottica. If that is the case, you can use the `verify_ua` method to verify an
IP against a particular User-Agent directly.

```pycon
>>> ua = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
>>> btca.parse_ua(ua)
'Googlebot'
>>> btca.verify_ua(ip="1.2.3.4", user_agent=ua)
False
```

If you have a User-Agent that ua-parser can't parse by default, you can add
your own parsers to ua-parser:

```pycon
>>> from ua_parser import user_agent_parser
>>> my_parser = user_agent_parser.UserAgentParser(pattern="MyBotRegex", family_replacement="MyBotName")
>>> user_agent_parser.USER_AGENT_PARSERS.insert(0, my_parser)
```

You should set the `family_replacement` for your parser to be the same
as the bot's name in Bottica. If you're adding a new bot that isn't in Bottica
Core, you should also add your own verifier for it.

## ➕ Add your own verifiers

By default, Bottica Core supports the biggest bots that provide verification
([except Facebook](../CONTRIBUTING.md#-whoisasn-verifier)). However, the list
can never be exhaustive. If you want to add custom bots to verify, you can do
so in two ways:

* Add a verifier directly to `Bottica.verifiers`
* Load a custom `bottica.yaml`

**Do you have a verifiable bot popping up in your logs that isn't included
in Bottica Core? [Submit a PR!](../CONTRIBUTING.md)**

### Adding a verifier directly

To add a verifier directly, simply insert it in the `verifiers` dictionary
using your bot's name as the key. The value should be a dict specifying one or
more of the [verification methods](../core#-verifiers) from Bottica Core.

```pycon
>>> btca.verifiers["MyBotName"] = {"ip_list": ["1.2.3.4", "2.3.4.5"]}
```

### Loading a custom `bottica.yaml`

If you want to maintain your custom bots in a more structured way, you can
also load your own `bottica.yaml` file, as long as it follows the
[specification](../core) from Bottica Core.

```yaml
# my_bottica.yaml
bots:
- name: MyBotName
  ip_list:
    - 1.2.3.4
    - 2.3.4.5
```

```pycon
>>> btca.load("path/to/my_bottica.yaml")
>>> btca.verifiers["MyBotName"]
{"ip_list": ["1.2.3.4", "2.3.4.5"]}
```

Either way (modifying `verifiers` directly or loading a custom `bottica.yaml`), the end result is the same.

## 📍 Verify an IP directly

If you don't need the Bottica Core list of verifiers and just want to
to do checks on IPs, you can use the `bottica` verification functions
directly.

```pycon
>>> from bottica import verification
```

The `verification` module offers verification functions that match the names
and behavior of the corresponding verification methods from Bottica Core:
* `verification.fcrdns_hosts(ip, allowed_hosts, max_tries)`
* `verification.ip_list(ip, allowed_ips)`
* `verification.ip_ranges(ip, allowed_ranges)`
* `verification.cidr_list(ip, allowed_cidrs)`

# 🤖 Bottica

An open source bot & crawler traffic verification tool.

Bots & crawlers generate huge amounts of traffic to most websites. Much of
this traffic is good, in the sense that it creates value (e.g. traffic from
Googlebot is how you keep yourself in search results). Good bots generally
identify themselves with their
[User-Agent string](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent)
so that you don't block them, and respect your `robots.txt`.

However, plenty of bad bots just copy good bots' User-Agents to try to slip
under the radar. That's why the biggest good bots offer verification methods
beyond just the User-Agent, so you can be sure that a request from them is
really legit.

## 🛒🛍 A one-stop shop for bot traffic verification

Maintainers of good bots publish the details of their
[verification methods](#-verifying-good-requests)
on their websites. However, finding these and keeping track of them can
be a hassle, especially if you want to verify traffic from several bots.

[Bottica Core](./core) aims to be a one-stop shop for tracking verification
methods, providing a unified, language-agnostic specification for bot
verification. This approach was inspired by the
[ua-parser](https://github.com/ua-parser/uap-core) project, which is a
similarly-implemented list of regular expressions for parsing User-Agent
strings. Bottica [attempts](../core#-uap-extras) to align its bot names with
the matching name from ua-parser, so that that project can be used to parse
UAs, and the extracted information can be used directly to verify the request
using Bottica.

Bottica can be implemented in any language that is capable of performing DNS
lookups. Currently, only a [Python implementation](./python) is provided, but
PRs adding implementations in other language would be
[more than welcome](./CONTRIBUTING.md)!

## ✅ Verifying good requests

Broadly speaking, good bots provide verification in one of two ways:
* 🔄 Forward-confirmed reverse DNS (FCrDNS)
* 📃 Publishing white lists of IPs that they use in some form

### 🔄 FCrDNS

A forward-confirmed reverse DNS verification is a two step process:

1. A reverse DNS query is performed on an IP to check its reported hostname
2. A forward DNS query is performed on the hostname to get its reported list
   of IPs. The original IP should appear in the hosts list of IPs if the
   reported host name hasn't been spoofed.

As an additional check, bot owners will generally also provide a set of host
names IPs of their bots must resolve to. Bottica Core supports FCrDNS both
[with and without](../core#-fcrdns-hosts) additional host name verification.

### 📃 IP whitelists

Publishing an IP whitelist is a very simple verification method employed by
many bot owners. It can also be combined with FCrDNS to provide a double
layer of verification.

Bottica Core supports IP whitelists as list of
[individual IPs](../core#-ip-list), [IP ranges](../core/#-ip-ranges), and
[CIDR blocks](../core/#-cidr-list).

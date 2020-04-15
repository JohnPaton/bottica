# Bottica Core

The `bottica` specification and list of verifiers: [`bottica.yaml`](./bottica.yaml).

The `bottica` object contains a single entry, `bots`. Its value is a list
of bots, which have a `name` and one or more verifiers. A json-schema of
`bottica` is available at [`schema.yaml`](./schema.yaml).

We aim for bot names to be in with sync their User-Agent family as parsed
by the [ua-parser project](https://github.com/ua-parser/uap-core) (UAP)
to maximize interoperability.

## Verifiers
* [`fcrdns_hosts`](#fcrdns-hosts): Forward-confirmed reverse DNS.
* [`ip_list`](#ip-list): Simple IP whitelist
* [`ip_ranges`](#ip-ranges): Whitelisting of ranges of IPs
* [`cidr_list`](#cidr-list): Whitelisting of CIDR blocks

Each entry in `bottica` can have one or more verifiers. For example,
`Pinterestbot` traffic should be both verified by FCrDNS, _and_ it should
come from a specific IP range:

```yaml
- name: Pinterestbot
  ip_ranges:
    - min: 54.236.1.1
      max: 54.236.1.255
  fcrdns_hosts:
    - pinterest.com
```

### FCrDNS hosts

`fcrdns_hosts` should contain a list of hosts that are allowed to
participate in a [FCrDNS lookup](https://en.wikipedia.org/wiki/Forward-confirmed_reverse_DNS).
If the list is empty, then an FCrDNS check will still be performed, but
all host names will be accepted as long as the IP matches the host's
reported IP address list.

**Example**
```yaml
- name: Googlebot
  fcrdns_hosts:
    - google.com
    - googlebot.com
```

### IP list

A simple whitelist of allowed IP addresses.

**Example**
```yaml
- name: DuckDuckBot
  ip_list:
    - 23.21.227.69
    - 50.16.241.113
    - 50.16.241.114
    - 50.16.241.117
    - 50.16.247.234
    - 52.204.97.54
    - 52.5.190.19
    - 54.197.234.188
    - 54.208.100.253
    - 54.208.102.37
    - 107.21.1.8
```


### IP ranges

A list of IP ranges, one of which must contain the bot's IP. A range is
specified with the `min` IP and the `max` IP, with both boundaries
being inclusive.

**Example**

```yaml
- name: Pinterestbot
  ip_ranges:
    - min: 54.236.1.1
      max: 54.236.1.255
```

### CIDR list

A list of CIDR blocks, one of which must contain the bot's IP address.


## UAP Extras

Since `ua-parser` is an external dependency, it is sometimes necessary
to make some additions or tweaks to their parsing, e.g. in cases where
a major bot is missing, or when their parsed family is too specific
(think of one bot going under many different names, which would all
require separate entries in `bottica`).
[`uap_extras.yaml`](./uap_extras.yaml) provides overrides and additions
to the User-Agent parsing from
[uap-core](https://github.com/ua-parser/uap-core). These should only
contain a regex to match, and possibly a `family_name` override for
setting the bot's name. If provided, `family_name` must match one of
the bot names in `bottica`. If not provided, the first matching group
of the `regex` must always match one of the bot names in `bottica`.

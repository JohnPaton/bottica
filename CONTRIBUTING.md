# Contributing to Bottica

Bottica would love some help! Here are some contributions that would be
especially welcome:

* More bots
* WHOIS/ASN verifier
* Language implementations
* Documentation improvements

## More bots

Have you encountered a friendly bot that offers verification? Add it to
[bottica-core](./core). New entries in Bottica should match the
[bottica spec](./core/README.md), and should have a comment with a link
to the bot's verification webpage so that it's easier to keep track of
any changes.

## WHOIS/ASN verifier

[Facebook](https://developers.facebook.com/docs/sharing/webmasters/crawler/)
provide a dynamic list of CIDRs that their bot traffic could come from.
It would be great to have an additional verifier that performs this
check, and then pipes the whitelisted CIDRs into a `cidr_list`
verification.

## Language implementations

Currently Bottica is only available as a Python package, but
in principle any language that can do DNS lookups and read YAML should
be able to support a Bottica verifier.

Some interesting options would include:

* golang/C/C++/Rust: gotta go fast
* Node.js/Ruby/Java for server-side validation
* A dockerized verification server for verifying IP/User-Agent pairs
* A CLI for piping logs into verification lists

## Documentation improvements

Docs can _always_ be improved.

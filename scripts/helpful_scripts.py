from brownie import (
    network,
    config,
    accounts,
)

FORKED_LOCALE_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCALE_BLOCKCHAIN_ENVIRONTMENTS = ["development", "ganache-locale"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCALE_BLOCKCHAIN_ENVIRONTMENTS
        or network.show_active() in FORKED_LOCALE_ENVIRONMENTS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])

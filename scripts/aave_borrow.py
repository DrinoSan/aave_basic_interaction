from brownie import accounts, network, config, interface
from scripts.get_weth import get_weth
from scripts.helpful_scripts import get_account
from web3 import Web3

amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()

    # Depositing ETH ( WETH ) into aave
    # ABI
    # ADDRESS
    lending_pool = get_lending_pool()

    # Approve sending out ERC20 token
    approve_erc20(amount, lending_pool.address, erc20_address, account)

    print("Depositing...")
    tx = lending_pool.deposit(erc20_address, amount, account, 0, {"from": account})
    tx.wait(1)
    print("Deposited!")
    # ... how much to borrow?
    borrowable_eth, total_dept = get_borrowable_data(lending_pool, account)
    print("Let's borrow")
    # DAI in terms of ETH
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    # borrowable_eth -> borrowable_dai * 0.95 ( the 0.95 are for a better health factor)
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")
    # Now we will borrow
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("We borrows some DAI")
    get_borrowable_data(lending_pool, account)

    # repay_all(amount, lending_pool, account)
    print("You just deposited, borrowed and repayed with Aave, Brownie and Chainlink")


def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repaid!")


def get_asset_price(price_feed_address):
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"The latest DAI/ETH price is: {converted_latest_price}")
    return float(converted_latest_price)
    # 0.000230213930000000


def get_borrowable_data(lending_pool, account):
    (
        totalCollateralETH,
        totalDebtETH,
        availableBorrowsETH,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = lending_pool.getUserAccountData(account.address)
    availableBorrowsETH = Web3.fromWei(availableBorrowsETH, "ether")
    totalDebtETH = Web3.fromWei(totalDebtETH, "ether")
    totalCollateralETH = Web3.fromWei(totalCollateralETH, "ether")
    print(f"You have {totalCollateralETH} worth of ETH deposited")
    print(f"You have {totalDebtETH} worth of ETH borrowd")
    print(f"You can borrow {availableBorrowsETH} worth of ETH")
    return (float(availableBorrowsETH), float(totalDebtETH))


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving erc20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved")
    return tx


def get_lending_pool():
    lending_pool_services_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_services_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool

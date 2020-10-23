import smartpy as sp

# Import FA2 template
FA2 = sp.import_script_from_url("https://smartpy.io/dev/templates/FA2.py")


class Cyber_Token(FA2.FA2):
    pass


@sp.add_test(name="Fungible Token")
def test():
    scenario = sp.test_scenario()

    admin = sp.test_account("Decentralized Dictator")
    mark = sp.test_account("Mark")
    elon = sp.test_account("tesla")

    # Initialize Cyber_Token as cyber_token with single_asset = True
    cyber_token = Cyber_Token(FA2.FA2_config(single_asset=True), admin.address)
    scenario += cyber_token
    # mint 5 tokens to mark
    scenario += cyber_token.mint(address=mark.address,
                                 amount=5,
                                 symbol='CBT',
                                 token_id=0
                                 ).run(sender=admin)
    # mint 10 tokens to elon
    scenario += cyber_token.mint(address=elon.address,
                                 amount=10,
                                 symbol='CBT',
                                 token_id=0
                                 ).run(sender=admin)

    # transfer 2 tokens from elon to mark.
    scenario += cyber_token.transfer([
        cyber_token.batch_transfer.item(from_=elon.address,
                                        txs=[
                                            sp.record(amount=2,
                                                      to_=mark.address,
                                                      token_id=0)
                                        ])
    ]).run(sender=elon)

    # create the FA2.View_consumer and add it to the scenario.
    consumer = FA2.View_consumer(cyber_token)
    scenario += consumer

    def arguments_for_balance_of(receiver, reqs):
        return (sp.record(
            callback=sp.contract(
                FA2.Balance_of.response_type(),
                sp.contract_address(receiver),
                entry_point="receive_balances").open_some(),
            requests=reqs))

    # call the entry point balance_of to check elon's balance.
    scenario += cyber_token.balance_of(arguments_for_balance_of(consumer, [
        sp.record(owner=elon.address, token_id=0)
    ]))

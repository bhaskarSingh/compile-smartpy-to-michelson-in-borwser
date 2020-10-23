import smartpy as sp


class Cryptobot(sp.Contract):

    def __init__(self, manager_address, life_state, initial_mutez, market_address):

        self.init(
            bot_manager=manager_address,
            name="terminator",
            is_alive=life_state,
            plasma_bullet_count=5,

            record_alien_kills={
                "simple_alien": sp.nat(0),
                "boss_alien": sp.nat(0),
            },
            mutez_points=sp.mutez(initial_mutez),
            market_address=market_address,
            active_powerup=sp.record(power='', duration=0)
        )

    @sp.entry_point
    def shoot_alien(self, alien_type):

        sp.verify(
            self.data.bot_manager == sp.sender,
            message="Error: non manager call"
        )

        sp.if self.data.plasma_bullet_count >= 1:
            self.data.plasma_bullet_count -= 1
            self.data.record_alien_kills[alien_type] += 1
        sp.else:
            sp.failwith("Error: you ran out of bullets! Please buy more!")

    @sp.entry_point
    def buy_powerup(self, powerup):

        # modify data_type to also hold another variable called cryptobot_address.
        data_type = sp.TRecord(powerup=sp.TString, cryptobot_contract=sp.TContract(
            sp.TRecord(power=sp.TString, duration=sp.TNat)))

        market_contract = sp.contract(
            data_type, self.data.market_address).open_some()
        self.data.mutez_points -= sp.mutez(3000)

        # define self_contract -
        # 1. Accepts a record with two variables - power(string), duration(nat)
        # 2. Points to the Cryptobot( use sp.to_address() )
        # 3. Specifies receive_powerup entry point
        self_contract = sp.contract(sp.TRecord(power=sp.TString, duration=sp.TNat), sp.to_address(
            sp.self), "receive_powerup").open_some()

        # modify data_to_be_sent to also hold cryptobot_contract which is assigned self_contract
        data_to_be_sent = sp.record(
            powerup=powerup, cryptobot_contract=self_contract)
        sp.transfer(data_to_be_sent, sp.mutez(0), market_contract)

    @sp.entry_point
    def receive_powerup(self, powerup):
        # set active_powerup as the powerup being accepted as a parameter
        self.data.active_powerup.power = powerup.power
        self.data.active_powerup.duration = powerup.duration


class Market(sp.Contract):
    def __init__(self):
        self.init(

            powerups=[
                sp.record(power="time_freeze", duration=3),
                sp.record(power="one_shot_kill", duration=4)
            ]
        )

    @sp.sub_entry_point
    def find_powerup(self, powerup):
        powerup_to_send = sp.local(
            'powerup_to_send', sp.record(power='', duration=sp.nat(0)))

        sp.for p in self.data.powerups:

            sp.if p.power == powerup:

                powerup_to_send.value.power = p.power
                powerup_to_send.value.duration = p.duration

        sp.result(powerup_to_send.value)

    @sp.entry_point
    def send_powerup(self, params):
        # remember to pass find_powerup the powerup sent in params.
        powerup_to_send = self.find_powerup(params.powerup)

        # transfer powerup_to_sent with 0 mutez to the cryptobot_contract sent through the params.
        sp.transfer(powerup_to_send, sp.mutez(0), params.cryptobot_contract)


@sp.add_test(name="inter-contract")
def test():
    scenario = sp.test_scenario()

    # Class Invokation
    my_account = sp.test_account("Cryptobot Owner")
    market = Market()
    scenario += market

    test_bot = Cryptobot(manager_address=my_account.address, life_state=True,
                         initial_mutez=5000, market_address=market.address)
    scenario += test_bot

    # test our code over here.
    scenario += test_bot.buy_powerup('time_freeze')
    scenario.verify(test_bot.data.mutez_points == sp.mutez(2000))
    scenario.verify(test_bot.data.active_powerup.power == 'time_freeze')

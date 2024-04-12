from time import sleep
from pprint import pprint

import algotrade_api
from algotrade_api import AlgotradeApi, PowerPlant, Resource


# Change this at the start of the competition
url = "https://algotrade-server.xfer.hr" # Change this
team_secret = "gogi" # Change this


api = AlgotradeApi(url, team_secret)


def run_with_inputs():
    # Get all games avaliable
    games = api.get_games().json()
    pprint(games)
    i = int(input("Enter index of the game you want to play > "))
    game = games[i]

    api.set_game_id(game["game_id"])

    # Get players you created in this game
    players = api.get_players().json()
    pprint(players)
    i = int(input("Enter index of the player you want to play with, -1 to create new > "))

    if i == -1:
        player_name = input("Name of your player >")
        response = api.create_player(player_name)
        pprint(response.json())
        player_id = response.json()["player_id"]
    else:
        player_id = players[i]["player_id"]
    api.set_player_id(player_id)

    input("Start loop (press enter to continue) >")
    run_with_params()


def run_with_params(game_id: str = None, player_id: str = None):
    # If you want to run the game directly from main, set these parameters
    if game_id is not None:
        api.set_game_id(game_id)
    if player_id is not None:
        api.set_player_id(player_id)

    print("Buying solar power plant")
    r = api.buy_plant(PowerPlant.SOLAR.value)
    assert r.status_code == 200, r.text

    print("Turning the power plant on")
    r = api.turn_on(PowerPlant.SOLAR.value, 1)
    assert r.status_code == 200, r.text

    print("Set the energy price to 300")
    r = api.set_energy_price(300)
    assert r.status_code == 200, r.text

    # Print player stats
    r = api.get_player()
    assert r.status_code == 200, r.text
    pprint(r.json())

    while True:
        tick()
        sleep(0.9)


def tick():
    # Get current player stats
    r = api.get_player()
    assert r.status_code == 200, r.text
    player = r.json()
    print(f"{player['player_id']} Money: {player['money']}")


    # List best market orders
    r = api.get_orders(restriction="best")
    assert r.status_code == 200, r.text
    rjson = r.json()

    # Buy all resources while you can (not a good bot)
    for resource in Resource:
        if (resource.value == Resource.URANIUM.value or 
            resource.value == Resource.ENERGY.value):
            continue
        try:
            orders = rjson[resource.value]
            best_order = orders["sell"][0]
            best_price = best_order['price']
            best_size = best_order["size"]
        except:
            continue

        print(f"{player['player_id']} Buying {resource.value} price: {best_price}, size: {best_size}")

        # Create order to buy coal that will expire in 10 ticks
        r = api.create_order(
            resource=resource.value,
            price=best_price + 100,
            size=5,
            side="buy",
            expiration_length=10)
        assert r.status_code == 200, r.text


if __name__ == "__main__":
    run_with_inputs()

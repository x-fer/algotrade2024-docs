
# Algotrade hackathon

Algotrade hackathon game rules and technical details.

In case of any questions, feel free to ping organizers in Discord or in person!

## Table of contents
1. [Task description](#task)
    1. [Resource market](#resource_market)
    1. [Power plants](#resource_market)
    1. [Electricity market](#electricity_market)
1. [Ticks](#ticks)
1. [Rounds and scoring](#games)
1. [Appendix](#extra)
    1. [Order matching example](#order_matching)
    1. [Bot orders mechanics](#bot_orders)

## Task description <a name="task"></a>

There is a simulated stock exchange for resources and energy.
At the beginning of a game, you are given a sum of money. 
You can buy and sell your resources on *the resource market*.
Resources can be stored in your storage.

You can also process resources you own and produce electricity using *power plants*. This electricity can be sold on *the electricity market*, but cannot be stored.

The player with the biggest [net worth](#scoring) at the end of the game wins!

<img src="./trzista.drawio.svg" style="width:450px;height:300px;">



## Resource market <a name="resource_market"></a>

There are 5 types of resources in this game. These are **coal, uranium, biomass, gas, and oil**. They all have different power outputs and different prices for respective power plants.
Users can buy and sell resources using *orders*.

The game is split into [ticks](#ticks). During ticks, you place your orders which will be put in the order-matching engine at the end of the tick.

Order is defined by:
- order side: BUY / SELL
- resource: resource you want to buy or sell
- order size: number of resources you are trading
- order price: price per unit of resource you are selling (not the total price of the order)
- expiration tick: tick in the game when this order expires (see API docs on the game server for details)

### Matching engine <a name="matching_engine"></a>

will place the orders by the time of arrival - as if they were evaluated in real-time. They are evaluated at the end of the tick for performance reasons. 

- If the order is a BUY order: the engine will look for the SELL order with the lowest price that is already in the engine and if the price is lower than the price of the BUY order, they will match with trade price set as the price of the SELL order (it arrived first).
- If the order is a SELL order: the engine will look for the BUY order with the highest price that is already in the engine and if the price is higher than the price of the SELL order, they will match with trade price set as the price of the BUY order (it arrived first).

If during this process there are two orders with the same price, the engine will look for the first one. If no matching order is found, the placed order will be saved by the engine for later matching, until it expires.

When orders match, the engine checks if the selling player has enough resources and if the buying player has enough money. If not, the respective order is canceled.
Otherwise, both order sizes are updated, since players have now traded resources. If one of the orders remains unfilled (with unsold resources), then it is matched again. See [matching example](#matching_example).

<img src="./match.drawio.svg" style="width:390px;height:250px;">

### Bot orders

Every 5 ticks, our bots create new resource orders (both buy and sell). Price is determined by dataset and [pricing mechanic](#bot_orders). Volume is set to keep players' total resources constant. For example, if players collectively have a lot of resources, our bots will have bigger buy volume, but smaller sell volume.

## Power plants <a name="power_plants"></a>

There are two types of power plants: renewable and nonrenewable.

Every power plant you buy of one type makes the next one more expensive. You can also sell them at 70% of their original price.

The exact formula for the price of the power plant is:

$$
Base price \times (1 + 0.1 x + 0.03 x^2)
$$

Where x is the number of power plants of this type you already own.

### Nonrenewable

Nonrenewable power plants corespond to resources in the game. These are: **coal, uranium, biomass, gas, and oil**.

Nonrenewables require resources to run but produce a lot of stable electricity. You can set how many resources of each type you want to burn per tick. But you cannot burn more resources per tick than power plants of that type that you have. 

- 1 resource burned per tick = 1 power plant is on.

Power plants are evaluated at the end of the tick, after resource order matching, but before electricity matching. If you don't have required resources, some power plants will automatically shut off.

### Renewable

Renewable power plants are **geothermal, wind, solar and hydro**. They don't have coresponding resources, but only power plants.

Renewables always produce electricity following the dataset. However, renewables produce less electricity and do it less reliably. You can use modeling to predict how much they will produce since every tick is one hour in the dataset, which means that one day is 24 ticks.
For example, solar plants will produce more electricity during the daytime.

You can see an example of electricity production from one solar plant below.

<img src="./solar.svg" style="width:480px;height:350px;">

## Energy market <a name="energy_market"></a>

The energy market is simpler than the resource market. You will set the price for your electricity. Our market will have a certain volume of electricity each tick (electricity demand) and the maximum price at which it will buy electricity. It will look for the cheapest electricity from players and buy as much as it can. If it is not filled, it will look for more. If two players set the same price, we will sell it proportionally to the electricity they have produced.

## Ticks <a name="ticks"></a>

In one tick players can create new orders and do other requests.

At the end of the tick following things happen in this order:

1) Resource orders are added to match the engine in time order, and 
then matched on the price-time priority

1) Power plants consume a set amount of resources and then
produces electricity

1) Energy agent buys players energy on price priority
    - If you have energy that is not sold to an energy agent, it is destroyed!
So make sure you produce the right amount of energy

<img src="./tick.drawio.svg" style="width:450px;height:200px;">


## Rounds and scoring <a name="games"></a>

There will be multiple games during the hackathon.

- One game will be open all night long for testing your bots, this game will have the annotation `is_contest=False`.

- There will be **three competition** rounds lasting for 30 minutes. These 
rounds will be scored and they have annotation `is_contest=True`.

- Around one hour before each competition round, we will start a **test round** that will simulate a contest. They will also last 30 minutes, and have the same limitations, but will not be scored. We encourage you to use your best bots here to promote good competition, however don't have to since these rounds aren't scored. These rounds will also have the annotation `is_contest=True`.

You will be able to differentiate between competition and test rounds by names, or ask organizers.

<a name="is_contest"></a>
Normal round `is_contest=False` lasts all night long and may be reset a few times. You may have 10 bots in one game and can reset their money balance. Ticks in these games are longer so you can see more easily what is happening.

When `is_contest=True` (including both test and competition rounds), ticks last one second, and your team is limited to one bot. You can not reset the balance of this bot! So make sure everything goes as planned and that you don't waste your resources and money.

All games will use different datasets.

### Team secrets and creating players <a name="team_secret"></a>

Each team will get a unique `team_secret`. Make sure to send it as a query parameter in all requests you send! Do not share this secret with other teams. It is sent as query parameter for simplicity reasons. Spying the web for team secrets of other teams is strictly forbidden!

Each game has a unique `game_id`. In games, you will be able to create multiple players for testing purposes (so that each team member can create their bots for example). This is of course restricted in contest rounds.

Note: if you created a player in one game, it is not created in all games!

See API docs on the game server for more details.

### Scoring <a name="scoring"></a>

You are scored by your player's net worth. This is calculated as the sum of the sell prices of every power plant you own plus the money you have plus the value of resources you own in current market prices.

Value of the power plants you own are evaluated automatically, you do not have to sell them at the end of the game, since it will give you the same amount of money.

Value of resources is taken directly from our dataset. It is very similar to the price at which our game bot puts their resources on the market - around 5\%. You do not need to sell your resources, except if you predict that the dataset price will be lower at the end of the game.

## Appendix

### Order matching example <a name="matching_example"></a>

The table below shows already placed orders for coal resources.

| Order id| Side |Price | Size |
|-| -----|-----|-----|
|1| BUY | \$250 | 400 |
|2| SELL | \$260 | 300 |
|3| SELL | \$290 | 300 |

Note: the table is sorted by price column, so after every match, the buy orders will still be above the sell orders.

Now three new orders arrive in this order:
[
(4, BUY, \$270, 400),
(5, BUY, \$280, 100),
(6, SELL, \$220, 100)
]
During the tick, they are saved to the queue. At the end of the tick, orders are matched:

The first order in the queue (order 4) is matched with order 2. The trade price is set to \$260 and size to 300. Order 2 is filled, and the player who placed order 4 will pay 300 x \$260 = \$78,000. However, order 4 is still not filled. Now it matches again, but all orders are too high, so it is saved by the engine. The table now looks like this:

| Order id| Side |Price | Size |
|-| -----|-----|-----|
|1| BUY | \$250 | 400 |
|4| BUY | \$270 | 100 |
|3| SELL | \$290 | 300 |

Order 5 is now matched, but all SELL orders are too expensive. It is also saved by the engine.


| Order id| Side |Price | Size |
|-| -----|-----|-----|
|1| BUY | \$250 | 400 |
|4| BUY | \$270 | 100 |
|5| BUY | \$280 | 100 |
|3| SELL | \$290 | 300 |

Order 6 is matched with order 5 with a price of \$280 and size 100. Both orders 5 and 6 are filled. The player who placed order 5 pays \$280 x 100 = \$28,000, and player 6 pays 100 oil resources. In the end, the table looks like this:

| Order id| Side |Price | Size |
|-| -----|-----|-----|
|1| BUY | \$250 | 400 |
|4| BUY | \$270 | 100 |
|3| SELL | \$290 | 300 |

### Bot orders mechanics <a name="bot_orders"></a>

**Constants in this explanation may be changed**

This mechanism is done for each resource separately.

Bot total volume is set between 100 and 400. If players have 10000 resources, then both the sell and buy volume will be 200. If players have more total resources than 10000, buy volume will be reduced linearly, and sell will be increased linearly. The same is done otherwise.

Price is taken directly from the dataset for the tick (about 1000-3000 per resource), but some bot coefficient is added. This coefficient is between -100 and 100. It is different for buy and sell, so it is possible that buy and sell prices from bots are much apart.
The buy coefficient is bigger if the last bot buy orders (those from the previous 5 ticks) were sold well - if they were more filled. If previous buy orders weren't traded at all, it means that the bot price is too high and that it should lower it.
It is done the same for sell orders but in a different direction.
These two coefficients are averaged and taken as the final coefficient of price.

Once the price and volume are determined, the bot *disperses* the orders. It creates many smaller orders totaling in volume to the calculated volume from before but with small variations in pricing from the original (about 1%).
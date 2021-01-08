from chalice import Chalice
from tda import auth, client
import os, json, datetime
from chalicelib import config

app = Chalice(app_name='tdatrade01')

token_path = os.path.join(os.path.dirname(__file__), 'chalicelib', 'token')
    
c = auth.client_from_token_file(token_path, config.api_key)

@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/quote/{symbol}')
def quote(symbol):
    response = c.get_quote(symbol)

    return response.json()

@app.route('/order', methods=['POST'])
def order():
    webhook_message = app.current_request.json_body
    
    if 'passphrase' not in webhook_message:
        return {
            "code": "error",
            "message": "no passphase in webhook message"
        }

    if webhook_message['passphrase'] != config.passphase:
           return {
            "code": "error",
            "message": "invalid passphase"
        }

    if webhook_message['side'] == "buy":
        order_spec = {
            "orderType": "MARKET",
            "session": "NORMAL",
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                "instruction": webhook_message["side"],
                "quantity": 1,
                "instrument": {
                    "symbol": webhook_message["ticker"],
                    "assetType": "EQUITY"
                }
                }
            ]
        }
        response = c.place_order(config.account_id, order_spec)
    
    else:
        #load the data into an element
        curr_positions = c.get_account(275366970, fields=[c.Account.Fields.POSITIONS])

        #load the json object into an element
        f = curr_positions.json()

        #get positions from account data
        positions = f['securitiesAccount']['positions']

        #find instument and quantity 
    for item in positions:
        x = item['instrument']

        #loop items and poistion
        if x['symbol'] == webhook_message["ticker"]:
            #print symbol and quantity
            print("Symbol: {}\nQuantity: {}".format(x['symbol'], item['longQuantity']))

            #place sell order with total quantity for symbol
            order_spec = {
                "orderType": "MARKET",
                "session": "NORMAL",
                "duration": "DAY",
                "orderStrategyType": "SINGLE",
                "orderLegCollection": [
                    {
                    "instruction": webhook_message["side"],
                    "quantity": item['longQuantity'],
                    "instrument": {
                        "symbol": webhook_message["ticker"],
                        "assetType": "EQUITY"
                    }
                    }
                ]
            }
            response = c.place_order(config.account_id, order_spec)
        else:
            print("nothing to do")
    return {
        "code": webhook_message['side']
    }

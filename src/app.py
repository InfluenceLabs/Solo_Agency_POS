from POS import POS

def handler(event):
    action = event.get('action')
    payload = event.get('body')

    pos = POS(payload=payload)
    routes = {
        'checkout': pos.create_checkout,
        'partner_checkout': pos.create_partner_checkout,
        'refund': pos.create_refund
    }

    route = routes.get(action)
    if not route:
        return {'statusCode': 400, 'body': '❌ Invalid action, no valid routes'}

    return route()
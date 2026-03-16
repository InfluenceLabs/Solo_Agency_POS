from POS import POS
import json

def handler(event):
    action = event.get('action')
    payload = event.get('body')

    ## If payload is a string (If from API Gateway), parse it
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            pass

    pos = POS(payload=payload)
    routes = {
        'checkout': pos.create_checkout,
        'partner_checkout': pos.create_partner_checkout,
        'refund': pos.create_refund,
        'success': pos.successful_payment,
        'get_balance': pos.get_till_balance
    }

    normalized_action = action.lower().strip().replace(' ', '_') if action else None
    route = routes.get(normalized_action)
    
    if not route:
        return {'statusCode': 400, 'body': '❌ Invalid action, no matching routes'}

    try:
        result = route()
        return {
            'statusCode': 200,
            'body': json.dumps(result) if not isinstance(result, str) else result
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
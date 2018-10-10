import json
import helpers
#import fundsTransfer
#import billPayment
import booking
import validate

# --- Calls respective intent ---

def dispatch(requestBody, eventsData):
    helpers.init()
    funcDict = {'booking' : booking.bookingcom,
                'getarrival_booking' : booking.getarrival_booking,
                'getdeparture_booking' : booking.getdeparture_booking,
                'getadult_booking' : booking.getadult_booking,
                'getchild_booking' : booking.getchild_booking,
                'Confirm_booking' : booking.Confirm_booking}
    if requestBody is None:
        return None
    requestBody = json.loads(requestBody)
    intent = validate.try_ex(lambda: requestBody['queryResult']['intent']['displayName'])
    result = (validate.try_ex(lambda: funcDict[intent](requestBody, eventsData)))
    if result is None:
        raise Exception('Intent with name ' + intent + ' not supported')
    return result

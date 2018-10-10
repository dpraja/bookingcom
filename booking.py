import validate
import helpers

# -- Entry point for main intent -- #

def bookingcom(requestBody, eventsData):
    session = validate.try_ex(lambda: requestBody['session'])
    languageCode = validate.try_ex(lambda: requestBody['queryResult']['languageCode'])
    arrival = validate.try_ex(lambda: requestBody['queryResult']['parameters']['arrival'])
    departure = validate.try_ex(lambda: requestBody['queryResult']['parameters']['departure'])
    adult = validate.try_ex(lambda: requestBody['queryResult']['parameters']['adult'])
    child = validate.try_ex(lambda: requestBody['queryResult']['parameters']['child'])


    parameters = {'arrival' : arrival, 'departure' : departure, 'adult' : adult, 'child' : child}
    
    outputContexts = message = followUpEvent = None
    
    # Checks the validity of each slot sequentially, calling the appropriate event if any slot is invalid/incomplete, or if all slots have been filled
    if arrival is not None and arrival != "" and validate.isvalidArrival(arrival):
        if departure is not None and departure != "" and validate.isvalidDeparture(departure):
            if adult is not None and adult != "" and validate.isvalidAdult(adult):
                 if child is not None and child != "" and validate.isvalidchild(child):
                     parameters['event'] = 'BOOKING_CONFIRM'
                     contextName = session+"/contexts/Confirm_bookingcontext"
                 else:
                    parameters['event'] = 'BOOKING_GET_CHILD'
                    contextName = session+"/contexts/getchild_bookingcontext"
                    
            else:
                parameters['event'] = 'BOOKING_GET_ADULT'
                contextName = session+"/contexts/getadult_bookingcontext"
        else:
            parameters['event'] = 'BOOKING_GET_DEPARTURE'
            contextName = session+"/contexts/getdeparture_bookingcontext"
    else: #default next intent if no parameters are provided
        parameters['event'] = 'BOOKING_GET_ARRIVAL'
        contextName = session+"/contexts/getarrival_bookingcontext"

    #save entered slots for next intent
    outputContexts = [
        {
            "name": contextName,
            "lifespanCount": 1,
            "parameters": parameters
        }]
    followUpEvent = {'name' : parameters['event'], 'languageCode' : languageCode, 'parameters' : parameters}
    return helpers.createResponseBody(message, outputContexts, followUpEvent)


# -- Secondary Intents that request one or more slots needed to fulfill the billPayment intent -- #
def Confirm_booking(requestBody, eventsData):
    session = validate.try_ex(lambda: requestBody['session'])
    languageCode = validate.try_ex(lambda: requestBody['queryResult']['languageCode'])
    parameters = validate.try_ex(lambda: requestBody['queryResult']['parameters'])
    confirm = validate.try_ex(lambda: requestBody['queryResult']['parameters']['confirm'])
    message = event = arrival = departure = adult = child = None
    
    outputContexts = validate.try_ex(lambda: requestBody['queryResult']['outputContexts'])
    currContext = session+"/contexts/Confirm_bookingcontext"
    for context in outputContexts:
        if context['name'] == currContext:
            event = validate.try_ex(lambda: context['parameters']['event'])
            arrival = validate.try_ex(lambda: context['parameters']['arrival'])
            departure = validate.try_ex(lambda: context['parameters']['departure'])
            adult = validate.try_ex(lambda: context['parameters']['adult'])
            child = validate.try_ex(lambda: context['parameters']['child'])
            if confirm is None:
                confirm = validate.try_ex(lambda: context['parameters']['confirm'])

    parameters['event'] = event
    parameters['confirm'] = confirm
    parameters['arrival'] = arrival
    parameters['departure'] = departure
    parameters['adult'] = adult
    parameters['child'] = child

    if confirm is not None and confirm != "":
        if confirm == 'yes':
            #remainingBalance = helpers.deductAccountBalance(helpers.hardcodedAccountBalance, account, amount) #Requires backend API call in actual code
            message = eventsData[event]['languages'][languageCode][0].format(arrival, departure, adult, child)
            return helpers.createResponseBody(message, None, None)
        else:#Either user has said no, or possibly some error in their response. TODO: Split up messages for both cases
            message = eventsData[event]['languages'][languageCode][1]
            return helpers.createResponseBody(message, None, None)
    else:#Ask for confirmation again
        parameters['event'] = 'BOOKING_CONFIRM'
        followUpEvent = {'name' : parameters['event'], 'languageCode' : languageCode, 'parameters' : parameters}
        contextName = session+"/contexts/Confirm_bookingcontext"
        outputContexts = [
                {
                    "name": contextName,
                    "lifespanCount": 1,
                    "parameters": parameters
                }]
        message = eventsData[event]['languages'][languageCode][2].format(arrival, departure, adult, child)
        return helpers.createResponseBody(message, outputContexts, followUpEvent)

def getchild_booking(requestBody, eventsData):
    session = validate.try_ex(lambda: requestBody['session'])
    languageCode = validate.try_ex(lambda: requestBody['queryResult']['languageCode'])
    parameters = validate.try_ex(lambda: requestBody['queryResult']['parameters'])
    child = validate.try_ex(lambda: parameters['child'])
    event = error = adult = departure = arrival = message = followUpEvent = None
     
    outputContexts = validate.try_ex(lambda: requestBody['queryResult']['outputContexts'])
    currContext = session+"/contexts/getchild_bookingcontext"
    for context in outputContexts:
        if context['name'] == currContext:
            event = validate.try_ex(lambda: context['parameters']['event'])
            error = validate.try_ex(lambda: context['parameters']['error'])
            arrival = validate.try_ex(lambda: context['parameters']['arrival'])
            departure = validate.try_ex(lambda: context['parameters']['departure'])
            adult = validate.try_ex(lambda: context['parameters']['adult'])
    parameters['event'] = event
    parameters['arrival'] = arrival
    parameters['departure'] = departure
    parameters['adult'] = adult

    if child is not None and child != "":
        if validate.isvalidchild(child):
            parameters['event'] = eventsData[event]['nextEvent']
            contextName = session + "/contexts/" + eventsData[event]['nextContext']
        
    '''
    if amount is not None and amount != "" and account is not None and account != "":
        if validate.isvalidAmount(helpers.hardcodedAccountBalance, amount, account):
            parameters['event'] = eventsData[event]['nextEvent']
            contextName = session+"/contexts/" + eventsData[event]['nextContext']
            '''
        else:
            parameters['error'] = True
            contextName = session + "/contexts/getchild_bookingcontext"
    else: #Unfilled
        contextName = session + "/contexts/getchild_bookingcontext"
        if(error == True):
            message = eventsData[event]['languages'][languageCode][0].format(parameters['account'])
        else:
            message = eventsData[event]['languages'][languageCode][1]

    followUpEvent = {'name' : parameters['event'], 'languageCode' : languageCode, 'parameters' : parameters}
    outputContexts = [
            {
                "name": contextName,
                "lifespanCount": 1,
                "parameters": parameters
            }]
    return helpers.createResponseBody(message, outputContexts, followUpEvent)


def getadult_booking(requestBody, eventsData):
    session = validate.try_ex(lambda: requestBody['session'])
    languageCode = validate.try_ex(lambda: requestBody['queryResult']['languageCode'])
    parameters = validate.try_ex(lambda: requestBody['queryResult']['parameters'])
    adult = validate.try_ex(lambda: parameters['adult'])
    event = error = departure = arrival = message = followUpEvent = None
     
    outputContexts = validate.try_ex(lambda: requestBody['queryResult']['outputContexts'])
    currContext = session+"/contexts/getadult_bookingcontext"
    for context in outputContexts:
        if context['name'] == currContext:
            event = validate.try_ex(lambda: context['parameters']['event'])
            error = validate.try_ex(lambda: context['parameters']['error'])
            arrival = validate.try_ex(lambda: context['parameters']['arrival'])
            departure = validate.try_ex(lambda: context['parameters']['departure'])
    parameters['event'] = event
    parameters['arrival'] = arrival
    parameters['departure'] = departure
    if adult is not None and adult != "":
        if validate.isvalidAdult(adult):
            parameters['event'] = eventsData[event]['nextEvent']
            contextName = session + "/contexts/" + eventsData[event]['nextContext']
        
    '''
    if amount is not None and amount != "" and account is not None and account != "":
        if validate.isvalidAmount(helpers.hardcodedAccountBalance, amount, account):
            parameters['event'] = eventsData[event]['nextEvent']
            contextName = session+"/contexts/" + eventsData[event]['nextContext']
            '''
        else:
            parameters['error'] = True
            contextName = session + "/contexts/getadult_bookingcontext"
    else: #Unfilled
        contextName = session + "/contexts/getadult_bookingcontext"
        if(error == True):
            message = eventsData[event]['languages'][languageCode][0].format(parameters['account'])
        else:
            message = eventsData[event]['languages'][languageCode][1]

    followUpEvent = {'name' : parameters['event'], 'languageCode' : languageCode, 'parameters' : parameters}
    outputContexts = [
            {
                "name": contextName,
                "lifespanCount": 1,
                "parameters": parameters
            }]
    return helpers.createResponseBody(message, outputContexts, followUpEvent)


def getdeparture_booking(requestBody, eventsData):
    session = validate.try_ex(lambda: requestBody['session'])
    languageCode = validate.try_ex(lambda: requestBody['queryResult']['languageCode'])
    parameters = validate.try_ex(lambda: requestBody['queryResult']['parameters'])
    departure = validate.try_ex(lambda: parameters['departure'])
    error = event = arrival = message = followUpEvent = None
    
    outputContexts = validate.try_ex(lambda: requestBody['queryResult']['outputContexts'])
    currContext = session+"/contexts/getdeparture_bookingcontext"
    for context in outputContexts:
        if context['name'] == currContext:
            event = validate.try_ex(lambda: context['parameters']['event'])
            error = validate.try_ex(lambda: context['parameters']['error'])
            arrival = validate.try_ex(lambda: context['parameters']['arrival'])
    parameters['event'] = event
    parameters['arrival'] = arrival

    if departure is not None and departure != "":
        if validate.isvalidDeparture(departure):
            parameters['event'] = eventsData[event]['nextEvent']
            contextName = session + "/contexts/" + eventsData[event]['nextContext']
        else:
            parameters['error'] = True
            contextName = session + "/contexts/getdeparture_bookingcontext"
    else: #Unfilled
        contextName = session+"/contexts/getdeparture_bookingcontext"
        if(error == True):
            message = eventsData[event]['languages'][languageCode][0]
        else:
            message = eventsData[event]['languages'][languageCode][1]

    outputContexts = [
            {
                "name": contextName,
                "lifespanCount": 1,
                "parameters": parameters
            }]
    followUpEvent = {'name' : parameters['event'], 'languageCode' : languageCode, 'parameters' : parameters}
    return helpers.createResponseBody(message, outputContexts, followUpEvent)


def getarrival_booking(requestBody, eventsData):
    session = validate.try_ex(lambda: requestBody['session'])
    languageCode = validate.try_ex(lambda: requestBody['queryResult']['languageCode'])
    arrival = validate.try_ex(lambda: requestBody['queryResult']['parameters']['arrival'])
    error = event = message = followUpEvent = None
    
    outputContexts = validate.try_ex(lambda: requestBody['queryResult']['outputContexts'])
    currContext = session+"/contexts/getarrival_bookingcontext"
    for context in outputContexts:
        if context['name'] == currContext:
            event = validate.try_ex(lambda: context['parameters']['event'])
            error = validate.try_ex(lambda: context['parameters']['error'])
    parameters = {'arrival' : arrival, 'event' : event}
    
    if arrival is not None and arrival != "":
        if validate.isvalidArrival(arrival):
            parameters['event'] = eventsData[event]['nextEvent']
            contextName = session+"/contexts/"+eventsData[event]['nextContext']
        else:
            parameters['error'] = True
            contextName = session+"/contexts/getarrival_bookingcontext"
    else: #Unfilled
        contextName = session+"/contexts/getarrival_bookingcontext"
        if(error == True):
            message = eventsData[event]['languages'][languageCode][0]
        else:
            message = eventsData[event]['languages'][languageCode][1]
    
    outputContexts = [
            {
                "name": contextName,
                "lifespanCount": 1,
                "parameters": parameters
            }]
    followUpEvent = {'name' : parameters['event'], 'languageCode' : languageCode, 'parameters' : parameters} 
    return helpers.createResponseBody(message, outputContexts, followUpEvent)
 
   

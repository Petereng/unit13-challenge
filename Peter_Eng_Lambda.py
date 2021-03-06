### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###

def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")

def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }

### Dialog Actions Helper Functions ###

def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response

def validate_data(age, investment_amount, intent_request):
    """
    Validates the data provided by the user.
    """

    # Validate that the user is over 0 years old and under 65
    
    if age is not None:
        age = parse_int(age)
        if age < 0:
            return build_validation_result(
                False,
                "age",
                "You should be between 0 and 65 years old to use this service, "
                "please provide a different age.",
            )
        elif age >= 65:
            return build_validation_result(
                False,
                "age",
                "You should be between 0 and 65 years old to use this service, "
                "please provide a different age.",
                )

    # Validate the investment amount, it should be < 5000
    
    if investment_amount is not None:
        investment_amount = parse_int(
            investment_amount
        )  # Since parameters are strings it's important to cast values
        if investment_amount < 5000:
            return build_validation_result(
                False,
                "investmentAmount",
                "The amount to convert should be greater than 5000, "
                "please provide a correct amount in dollars to convert.",
            )

    # A True results is returned if age or amount are valid
    return build_validation_result(True, None, None)

### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    slots = get_slots(intent_request)
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt
        # for the first violation detected.

        ### YOUR DATA VALIDATION CODE STARTS HERE ###
        
        # REVIEW WEEK 13 LESSON 1 -> CHECK WITH KHALED............................................................KHALED
        slots = get_slots(intent_request)
        validate_return = validate_data(age, investment_amount, intent_request)
        
        if not validate_return["isValid"]:
            
            slots[validate_return["violatedSlot"]] = None
            
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"], 
                slots, 
                validate_return["violatedSlot"], 
                validate_return["message"]
            )
            
        ### YOUR DATA VALIDATION CODE ENDS HERE ###

        # Fetch current session attibutes
        
        output_session_attributes = intent_request["sessionAttributes"]

        return delegate(output_session_attributes, slots)

    # Get the initial investment recommendation

    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE STARTS HERE ###
    
        # REVIEW WEEK 13 LESSON 1 -> CHECK WITH KHALED............................................................KHALED
    
    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###
    
    recommendations_msg = {
        "none": "100% bonds, 0% equities",
        "very low": "80% bonds, 20% equities",
        "low": "60% bonds, 40% equities",
        "medium": "40% bonds, 60% equities",
        "high": "20% bonds, 80% equities",
        "very high": "0% bonds, 100% equities",
    }
    initial_recommendation = recommendations_msg[risk_level.lower()]
    
    # Return a message with the initial recommendation based on the risk level.
    
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} thank you for your information;
            based on the risk level you defined, my recommendation is to choose an investment portfolio with {}
            """.format(
                first_name, initial_recommendation
            ),
        },
    )


### Intents Dispatcher ###

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###

def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)
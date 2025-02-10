from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

app = FastAPI()

client = OpenAI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

@app.post("/")
async def root(request: Request):
    try:
        data = await request.json()
        user_input = data.get('input', '').strip()
        orders_list = data.get('orders_list', [])

        if not user_input:
            return {"message": "No input received."}

        functions = [
            {
                "name": "return_order",
                "description": (
                    "Read the `user_input` and `orders_list` and return an order in JSON format. "
                    "If the user intends to cancel an existing order, include an 'action' key with the value 'cancel' "
                    "and an 'orderNumber' key (1-indexed) indicating which order to cancel. "
                    "Otherwise, return an updated order with the key 'orders'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "orderNumber": {"type": "integer"},
                        "orders": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item": {"type": "string"},
                                    "quantity": {"type": "integer"}
                                }
                            }
                        }
                    },
                    "required": ["orders"]
                }
            }
        ]

        system_message = (
            "Read the `user_input` and `orders_list`, then return an order in JSON format. "
            "If the user intends to cancel an order, include an 'action': 'cancel' key and an 'orderNumber' key "
            "that indicates the order number (1-indexed) to cancel, and return an empty orders array. "
            "Otherwise, return the new orders in the 'orders' key. "
            "Always use the item names 'burgers', 'fries', and 'drinks'.\n\n"
            "Examples:\n"
            '- "I would like to order a burger" -> { "orders": [{ "item": "burgers", "quantity": 1 }] }\n'
            '- "Two fries and a drink please" -> { "orders": [{ "item": "fries", "quantity": 2 }, { "item": "drinks", "quantity": 1 }] }\n'
            '- "Cancel order 3" -> { "action": "cancel", "orderNumber": 3, "orders": [] }'
        )
    
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"User Input: {user_input}\nPrevious Orders: {orders_list}"}
            ],
            functions=functions,
            function_call={"name": "return_order"}
        )

        # Extract function call output.
        function_call = completion.choices[0].message.function_call
        args_json = json.loads(function_call.arguments)

        # Extract keys from call.
        orders = args_json.get("orders", [])
        action = args_json.get("action")
        orderNumber = args_json.get("orderNumber")

        # Return the response with extra cancellation info.
        return {"action": action, "orderNumber": orderNumber, "message": orders}
    
    except Exception as e:
        print("Error:", str(e))
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)

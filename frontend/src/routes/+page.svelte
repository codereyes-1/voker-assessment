<script>
    import Button from "$lib/components/ui/button/button.svelte";
    import Input from "$lib/components/ui/input/input.svelte";
    import { Card, CardContent, CardHeader, CardTitle } from "$lib/components/ui/card";
    import OrderHistory from "$lib/components/ui/orderhistory/order-history.svelte"
    import { orders } from '../stores/orders.ts';
    import { burgers, fries, drinks } from '../stores/totals.ts';
    
    
    let newOrder = "";

    async function submit() {
        if (newOrder.trim() === "") return;
        
        /**
         * @param {number} index
         * @returns {object} Removed order
         */
        function removeOrder(index) {
          let removedOrder = null;
          orders.update(currentOrders => {
            removedOrder = currentOrders[index]; // Capture removed order before filtering
            return currentOrders.filter((_, i) => i !== index);
          });
          return removedOrder;
        }
        
        // Handling fetch response
        const response = await fetch("http://localhost:8000/", {
          mode: 'cors',
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            input: newOrder,
            orders_list: $orders
          }),
        });
        
        const result = await response.json();
        
        // Extract message
        const orderSummary = result.message;

        // Extract item, qty from message for totals display
        const burgerOrder = orderSummary.find((/** @type {{ item: string; }} */ order) => order.item === "burgers");
        const burgerQuantity = burgerOrder ? burgerOrder.quantity : 0;

        const friesOrder = orderSummary.find((/** @type {{ item: string; }} */ order) => order.item === "fries");
        const friesQuantity = friesOrder ? friesOrder.quantity : 0;

        const drinksOrder = orderSummary.find((/** @type {{ item: string; }} */ order) => order.item === "drinks");
        const drinksQuantity = drinksOrder ? drinksOrder.quantity : 0;


        // if cancel, called removeOrder() and update BFD stores
        if (result.action === "cancel" && result.orderNumber !== undefined) {
          const orderIndexToRemove = result.orderNumber - 1;
          const removedOrder = removeOrder(orderIndexToRemove);

            if (removedOrder) {
              removedOrder.forEach((/** @type {{ item: string; quantity: number; }} */ order) => {
                if (order.item === "burgers") burgers.update(n => n - order.quantity);
                if (order.item === "fries") fries.update(n => n - order.quantity);
                if (order.item === "drinks") drinks.update(n => n - order.quantity);
              });
            }
          } else {
            // Add new order. Update BFD and orders array stores
            burgers.update(n => n + (burgerQuantity || 0));
            fries.update(n => n + (friesQuantity || 0));
            drinks.update(n => n + (drinksQuantity || 0));

            orders.update(orders => [...orders, orderSummary]);
          }

          function speak() {
          if('speechSynthesis' in window) {
            let text = orderSummary.map((/** @type {{ quantity: any; item: any; }} */ order) => `${order.quantity} ${order.item}`).join(", ");
            const voices = speechSynthesis.getVoices();
            const voice = voices.find(voice => voice.lang === 'en-US');
            const orderIndexToRemove = result.orderNumber;
            if (result.action === "cancel" && result.orderNumber !== undefined) {
              const utterance = new SpeechSynthesisUtterance(`You got it! Order number ${orderIndexToRemove} has been cancelled. If you'd like anything else just place an order.`);
              speechSynthesis.speak(utterance);
            } else {
              const utterance = new SpeechSynthesisUtterance(`Got it! Your order includes ${text}.`);
              speechSynthesis.speak(utterance);
            }
          } else {
            console.log("Speech synthesis not supported");
          }
        }

        speak()


        newOrder = "";                
    }
</script>

<div class="justify-center mt-16 flex gap-10">
  <Card class="w-32">
    <CardHeader>
      <CardTitle>Total # of Burgers</CardTitle>
    </CardHeader>
    <CardContent class="text-xl font-bold">{$burgers}</CardContent>
  </Card>

  <Card class="w-32">
    <CardHeader>
      <CardTitle>Total # of Fries</CardTitle>
    </CardHeader>
    <CardContent class="text-xl font-bold">{$fries}</CardContent>
    </Card>

    <Card class="w-32">
    <CardHeader>
      <CardTitle>Total # of Drinks</CardTitle>
    </CardHeader>
    <CardContent class="text-xl font-bold">{$drinks}</CardContent>
    </Card>
</div>


<div class="mt-32 flex items-center justify-center">
    <form on:submit={submit} class="flex w-100 items-center space-x-2">
      <Input bind:value={newOrder} type="text" placeholder="Place your order here" />
      <Button variant="destructive" type="submit">Place Order</Button>
    </form>
  </div>

<OrderHistory/>
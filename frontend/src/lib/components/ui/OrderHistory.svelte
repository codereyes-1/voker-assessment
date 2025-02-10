<script>
    import { Card, CardContent, CardHeader, CardTitle } from "$lib/components/ui/card";
    import { orders } from "../../../stores/orders.ts";

</script>
<ul>
    {#each $orders as orderSet, setIndex}
        <div class="mt-32 flex flex-col gap-1 items-center justify-center">
            <Card class="w-1/2 space-between">
                <CardHeader>
                    <CardContent class="grid grid-cols-2">
                        <span class="font-bold">Order #{setIndex + 1}</span>
                        <ul class="flex flex-row">
                            {#each orderSet as order, orderIndex}
                            <li>
                                 <span>{order.quantity} {order.item}{orderIndex < orderSet.length - 1 ? ", " : " "}</span>
                            </li>
                            {/each}
                        </ul>
                    </CardContent>
                </CardHeader>
            </Card>
        </div>
    {/each}
</ul>
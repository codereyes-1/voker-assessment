import { writable } from "svelte/store";

export const orders = writable<{ item: string; quantity: number }[]>([]);

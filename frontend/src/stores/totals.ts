import { writable } from "svelte/store";

export let burgers = writable(0);
export let fries = writable(0);
export let drinks = writable(0);

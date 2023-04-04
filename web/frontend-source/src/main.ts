import { generate } from "./ui/generate.js";
import { fetch_components } from "./connection.js";

async function main(): Promise<void> {
  // Fetch the components
  const response = await fetch_components();

  // Alert if there is an error
  if ("error" in response) {
    alert(response.response);
    return;
  }

  // Otherwise display the components properly
  generate(response);
}

main();

console.log(
  "If this message is shown, everything is\n\n       ===> PinTastic <===\n "
);

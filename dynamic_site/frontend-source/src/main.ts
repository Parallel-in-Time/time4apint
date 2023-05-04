import { Generator } from './ui/generator.js';
import { fetchComponents } from './connection.js';

async function main(): Promise<void> {
  // Fetch the components
  const response = await fetchComponents();

  // Alert if there is an error
  if ('error' in response) {
    alert(response.response);
    return;
  }

  // Otherwise display the components properly
  const generator = new Generator();
  generator.makeUI(response);
}

main();

console.log(
  'If this message is shown, everything is\n\n       ===> PinTastic <===\n '
);

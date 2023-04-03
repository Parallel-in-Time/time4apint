async function get(): Promise<any> {
  // Fetch the initialization components
  const response = await fetch('/app/components', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    // TODO: Handle the error message
    console.log('Error with the response:', response);
    return { error: 'Error' };
  }

  // Handle the response here
  if (response.body !== null) {
    const body = await response.json();
    return body;
  }
}

// Fetch the components
get().then((response) => {
  // Alert if there is an error
  if ('error' in response) {
    alert(response.response);
    return;
  }

  // Otherwise display the components properly
  console.log(response);
});

console.log(
  'If this message is shown, everything is\n\n       ===> PinTastic <===\n '
);

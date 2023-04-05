async function fetchComponents(): Promise<any> {
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

  // Get the json from the response and return it.
  if (response.body !== null) {
    const body = await response.json();
    return body;
  }
}

/**
 * Send the data to the /app/compute path of the backend.
 *
 * @param data The JSON object to send back.
 * @returns The response as a json object (has 'error' as a key if there is an error).
 */
async function sendData(data: object): Promise<any> {
  // Post the data to the given url
  const response = await fetch('/app/compute', {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
    },
    referrerPolicy: 'no-referrer',
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    // TODO: Handle the error message
    console.log('Error with the response:', response);
    return { error: 'Error' };
  }

  // Get the json from the response and return it.
  if (response.body !== null) {
    const body = await response.json();
    return body;
  }
}

export { fetchComponents, sendData };

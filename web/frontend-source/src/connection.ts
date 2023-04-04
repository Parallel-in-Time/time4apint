async function fetch_components(): Promise<any> {
  // Fetch the initialization components
  const response = await fetch("/app/components", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    // TODO: Handle the error message
    console.log("Error with the response:", response);
    return { error: "Error" };
  }

  // Handle the response here
  if (response.body !== null) {
    const body = await response.json();
    return body;
  }
}

export { fetch_components };

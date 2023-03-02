async function getData() {
  const response = await fetch('/app/data', {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response.json();
}

async function post(url, data) {
  // Post the data to the given url
  const response = await fetch(url, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
    },
    referrerPolicy: 'no-referrer',
    body: JSON.stringify(data),
  });
  return response.json();
}

class Connection {
  initData() {
    return getData();
  }

  compute(data) {
    console.log('Computing...');
    return post('app/compute-stage-1', data);
  }
}

export { Connection };

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

  compute(stage, data) {
    console.log('Computing...');
    switch (stage) {
      case 1:
        return post('app/compute-stage-1', data);
      case 2:
        return post('app/compute-stage-2', data);
    }
  }
}

export { Connection };

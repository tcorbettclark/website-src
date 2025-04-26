async function hot_reloader() {
  console.log("Starting hot reloader.");
  const controller = new AbortController();
  addEventListener("beforeunload", (event) => {
    controller.abort();
  });
  waiting_for_reload = true;
  while (waiting_for_reload) {
    const options = {
      cache: "reload",
      signal: controller.signal,
    };
    const response = await fetch("/hot_reloader", options);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    action = await response.text();
    if (action == "Reload") {
      waiting_for_reload = false;
    }
  }
  console.log("Reloading..."); // Only seen in the browser console for a microsecond...
  window.location.reload(true);
}

async function start_hot_reloader() {
  try {
    await hot_reloader();
  } catch (error) {
    switch (error.message) {
      case "Load failed":
        alert("Hot reloading stopped. Is the dev server running?");
        window.location.reload(true);
        break;
      case "Fetch is aborted":
        // Assume this occurs because we aborted the fetch using the beforeunload event.
        // So swallow and do nothing.
        break;
      default:
        // Anything else is an error, so report it and re-raise.
        console.log(error);
        throw error;
    }
  }
}

// Only run the hot reloader during development.
if (window.location.hostname == "localhost") {
  start_hot_reloader();
}

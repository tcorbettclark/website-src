async function hot_reloader() {
  console.log("Starting hot-reloader.");
  waiting_for_reload = true;
  while (waiting_for_reload) {
    const options = {
      cache: "reload",
    };
    response = await fetch("/hot-reloader", options);
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
  const retry_period = 5;
  try {
    await hot_reloader();
  } catch (error) {
    if (error.message == "Load failed") {
      // After requesting a reload but before it happens, the fetch on Safari sometimes
      // throws this error. We don't care, but it produces console noise, so swallow it.
    } else {
      // Anything else is an error, so report it.
      console.log(error.message);
    }
    alert("Hot reloading stopped. Is the dev server running?");
    window.location.reload(true);
  }
}

// Only run the hot-reloader during development.
if (window.location.hostname == "localhost") {
  start_hot_reloader();
}

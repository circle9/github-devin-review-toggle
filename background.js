importScripts("url-toggle.js");

const { isGithubPullUrl, isDevinReviewUrl, toggleReviewUrl } = globalThis.urlToggle;

async function setActionState(tabId, url) {
  if (typeof tabId !== "number") {
    return;
  }

  if (isGithubPullUrl(url)) {
    await chrome.action.enable(tabId);
    await chrome.action.setTitle({
      tabId,
      title: "Open this pull request in Devin Review"
    });
    return;
  }

  if (isDevinReviewUrl(url)) {
    await chrome.action.enable(tabId);
    await chrome.action.setTitle({
      tabId,
      title: "Open this Devin review on GitHub"
    });
    return;
  }

  await chrome.action.disable(tabId);
  await chrome.action.setTitle({
    tabId,
    title: "This page is not a supported GitHub PR or Devin review URL"
  });
}

async function updateActionStateForTab(tabId) {
  try {
    const tab = await chrome.tabs.get(tabId);
    await setActionState(tabId, tab.url);
  } catch {
    // Ignore tabs that disappear while the service worker is updating state.
  }
}

async function refreshAllActionStates() {
  const tabs = await chrome.tabs.query({});
  await Promise.all(tabs.map((tab) => setActionState(tab.id, tab.url)));
}

async function toggleCurrentTabUrl(tab) {
  if (!tab || typeof tab.id !== "number") {
    return;
  }

  const nextUrl = toggleReviewUrl(tab.url);
  if (!nextUrl) {
    await setActionState(tab.id, tab.url);
    return;
  }

  await chrome.tabs.update(tab.id, { url: nextUrl });
}

chrome.action.onClicked.addListener((tab) => {
  toggleCurrentTabUrl(tab).catch((error) => {
    console.error("Failed to toggle review URL from action click.", error);
  });
});

chrome.commands.onCommand.addListener((command) => {
  if (command !== "toggle-review-target") {
    return;
  }

  chrome.tabs
    .query({ active: true, currentWindow: true })
    .then(([tab]) => toggleCurrentTabUrl(tab))
    .catch((error) => {
      console.error("Failed to toggle review URL from command.", error);
    });
});

chrome.tabs.onActivated.addListener(({ tabId }) => {
  updateActionStateForTab(tabId).catch((error) => {
    console.error("Failed to refresh action state after tab activation.", error);
  });
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (!changeInfo.url && changeInfo.status !== "complete") {
    return;
  }

  setActionState(tabId, tab.url).catch((error) => {
    console.error("Failed to refresh action state after tab update.", error);
  });
});

chrome.tabs.onCreated.addListener((tab) => {
  setActionState(tab.id, tab.url).catch((error) => {
    console.error("Failed to refresh action state for a new tab.", error);
  });
});

chrome.runtime.onInstalled.addListener(() => {
  refreshAllActionStates().catch((error) => {
    console.error("Failed to initialize action state on install.", error);
  });
});

chrome.runtime.onStartup.addListener(() => {
  refreshAllActionStates().catch((error) => {
    console.error("Failed to initialize action state on startup.", error);
  });
});

refreshAllActionStates().catch((error) => {
  console.error("Failed to initialize action state.", error);
});

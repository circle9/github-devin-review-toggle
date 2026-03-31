(function initializeUrlToggle(root) {
  const GITHUB_HOST = "github.com";
  const DEVIN_HOST = "app.devin.ai";
  const GITHUB_PULL_PATH = /^\/([^/]+)\/([^/]+)\/pull\/(\d+)\/?$/;
  const DEVIN_REVIEW_PATH = /^\/review\/([^/]+)\/([^/]+)\/pull\/(\d+)\/?$/;

  function parseUrl(rawUrl) {
    try {
      return new URL(rawUrl);
    } catch {
      return null;
    }
  }

  function matchGithubPull(url) {
    if (!url || url.hostname !== GITHUB_HOST) {
      return null;
    }

    const match = url.pathname.match(GITHUB_PULL_PATH);
    if (!match) {
      return null;
    }

    const [, owner, repo, pullNumber] = match;
    return { owner, repo, pullNumber };
  }

  function matchDevinReview(url) {
    if (!url || url.hostname !== DEVIN_HOST) {
      return null;
    }

    const match = url.pathname.match(DEVIN_REVIEW_PATH);
    if (!match) {
      return null;
    }

    const [, owner, repo, pullNumber] = match;
    return { owner, repo, pullNumber };
  }

  function isGithubPullUrl(rawUrl) {
    return Boolean(matchGithubPull(parseUrl(rawUrl)));
  }

  function isDevinReviewUrl(rawUrl) {
    return Boolean(matchDevinReview(parseUrl(rawUrl)));
  }

  function toDevinReviewUrl(rawUrl) {
    const url = parseUrl(rawUrl);
    const match = matchGithubPull(url);
    if (!match) {
      return null;
    }

    const target = new URL(
      `https://${DEVIN_HOST}/review/${match.owner}/${match.repo}/pull/${match.pullNumber}`
    );
    target.search = url.search;
    target.hash = url.hash;
    return target.toString();
  }

  function toGithubPullUrl(rawUrl) {
    const url = parseUrl(rawUrl);
    const match = matchDevinReview(url);
    if (!match) {
      return null;
    }

    const target = new URL(
      `https://${GITHUB_HOST}/${match.owner}/${match.repo}/pull/${match.pullNumber}`
    );
    target.search = url.search;
    target.hash = url.hash;
    return target.toString();
  }

  function toggleReviewUrl(rawUrl) {
    return toDevinReviewUrl(rawUrl) ?? toGithubPullUrl(rawUrl);
  }

  const urlToggle = {
    isGithubPullUrl,
    isDevinReviewUrl,
    toDevinReviewUrl,
    toGithubPullUrl,
    toggleReviewUrl
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = urlToggle;
  }

  if (root) {
    root.urlToggle = urlToggle;
  }
})(typeof globalThis !== "undefined" ? globalThis : this);

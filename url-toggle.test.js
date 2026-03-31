const test = require("node:test");
const assert = require("node:assert/strict");

const {
  isGithubPullUrl,
  isDevinReviewUrl,
  toDevinReviewUrl,
  toGithubPullUrl,
  toggleReviewUrl
} = require("./url-toggle.js");

test("recognizes supported GitHub pull request URLs", () => {
  assert.equal(
    isGithubPullUrl("https://github.com/circle9/sandbox/pull/14"),
    true
  );
  assert.equal(
    isGithubPullUrl("https://github.com/circle9/sandbox/pull/14/"),
    true
  );
});

test("rejects unsupported GitHub URLs", () => {
  assert.equal(
    isGithubPullUrl("https://github.com/circle9/sandbox/issues/14"),
    false
  );
  assert.equal(
    isGithubPullUrl("https://github.com/circle9/sandbox/pull/14/files"),
    false
  );
  assert.equal(
    isGithubPullUrl("https://gist.github.com/circle9/sandbox/pull/14"),
    false
  );
});

test("recognizes supported Devin review URLs", () => {
  assert.equal(
    isDevinReviewUrl("https://app.devin.ai/review/circle9/sandbox/pull/14"),
    true
  );
  assert.equal(
    isDevinReviewUrl("https://app.devin.ai/review/circle9/sandbox/pull/14/"),
    true
  );
});

test("rejects unsupported Devin URLs", () => {
  assert.equal(
    isDevinReviewUrl("https://app.devin.ai/review/circle9/sandbox/issues/14"),
    false
  );
  assert.equal(
    isDevinReviewUrl("https://app.devin.ai/review/circle9/sandbox/pull/14/files"),
    false
  );
  assert.equal(
    isDevinReviewUrl("https://app.devin.ai/projects/circle9/sandbox/pull/14"),
    false
  );
});

test("converts GitHub pull request URLs to Devin review URLs", () => {
  assert.equal(
    toDevinReviewUrl(
      "https://github.com/circle9/sandbox/pull/14?diff=split#discussion_r1"
    ),
    "https://app.devin.ai/review/circle9/sandbox/pull/14?diff=split#discussion_r1"
  );
});

test("converts Devin review URLs to GitHub pull request URLs", () => {
  assert.equal(
    toGithubPullUrl(
      "https://app.devin.ai/review/circle9/sandbox/pull/14?diff=split#discussion_r1"
    ),
    "https://github.com/circle9/sandbox/pull/14?diff=split#discussion_r1"
  );
});

test("toggleReviewUrl switches supported URLs in both directions", () => {
  assert.equal(
    toggleReviewUrl("https://github.com/circle9/sandbox/pull/14"),
    "https://app.devin.ai/review/circle9/sandbox/pull/14"
  );
  assert.equal(
    toggleReviewUrl("https://app.devin.ai/review/circle9/sandbox/pull/14"),
    "https://github.com/circle9/sandbox/pull/14"
  );
});

test("toggleReviewUrl returns null for unsupported or invalid URLs", () => {
  assert.equal(
    toggleReviewUrl("https://github.com/circle9/sandbox/issues/14"),
    null
  );
  assert.equal(toggleReviewUrl("not a url"), null);
  assert.equal(toggleReviewUrl("https://example.com/anything"), null);
});

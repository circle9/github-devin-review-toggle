# GitHub Devin Review Toggle

Chrome extension to switch the current tab between a GitHub pull request URL and the matching Devin review URL.

## Supported URLs

- `https://github.com/<owner>/<repo>/pull/<number>`
- `https://app.devin.ai/review/<owner>/<repo>/pull/<number>`

Query strings and hashes are preserved when switching.

## Install

1. Open `chrome://extensions`
2. Enable Developer mode
3. Click `Load unpacked`
4. Select this folder: `/path/to/devin-review-extention`

## Use

- Open a supported GitHub PR or Devin review page
- Click the extension icon to switch the current tab
- Optional: assign a keyboard shortcut in `chrome://extensions/shortcuts` for `Toggle between the GitHub pull request and Devin review for the current tab`

The extension icon is disabled on unsupported pages.

## Test

Run the automated URL parsing and conversion tests with:

```sh
npm test
```

## Assets

Extension icons are generated from:

```sh
python3 scripts/generate_icons.py
```

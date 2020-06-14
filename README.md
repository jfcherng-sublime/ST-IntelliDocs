# ST-IntelliDocs

Quick function parameter help for Sublime Text.

Currently supported languages:

- Go
- Javascript / DOM / jQuery
- PHP
- Python

## Installation

This plugin is not published on Package Control (and probably never will be).

To install this plugin via Package Control, you have to add a custom repository.

1. Execute `Package Control: Add Repository` in the command palette.
1. Add this custom repository: `https://raw.githubusercontent.com/jfcherng-sublime/ST-my-package-control/master/repository.json`
1. Restart Sublime Text.
1. You should be able to install this package with Package Control with the name `IntelliDocs`.

## Features

- Parameter hint
- Function description
- Parameter description
- Last function hint stays in status bar
- Open `devdocs.io` and other, customizable reference docs in browser

## Screenshots

### Javascript / jQuery

![Sublime Javascript hints](https://raw.github.com/jfcherng-sublime/ST-IntelliDocs/master/docs/intellidocs-javascript.png)

### PHP

![Sublime PHP hints](https://raw.github.com/jfcherng-sublime/ST-IntelliDocs/master/docs/intellidocs-php.png)

### Python

![Sublime Python hints](https://raw.github.com/jfcherng-sublime/ST-IntelliDocs/master/docs/intellidocs-python.png)

## Usage

- Set your cursor over a function or object you want to look up
  and press <kbd>Ctrl + Alt + h</kbd> to see relevant documentation.

## Thanks

- Wonderful `devdocs.io` for documents database.

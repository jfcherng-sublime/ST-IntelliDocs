# Sublime-IntelliDocs

Quick function parameter help for Sublime 3.x.
Currently supported languages:

- Go
- Javascript / DOM / jQuery
- PHP
- Python

## To use this plugin

This plugin is not on Package Control yet. To install this, you can

- Download the tarball from GitHub and decompress it to `Packages/`.
- Or add a custom Package Control repository (recommended).

  1. `Menu` > `Preferences` > `Package Control` > `Settings - User`:
     Add the following:

     ```js
     "package_name_map": {
       "Sublime-IntelliDocs": "IntelliDocs",
     },
     "repositories": [
       "https://github.com/jfcherng/Sublime-IntelliDocs.git",
     ],
     ```

  1. `Menu` > `Preferences` > `Package Control` > `Install Package`:
     Find `IntelliDocs` and install

## Features

- Parameter hint
- Function description
- Parameter description
- Last function hint stays in status bar
- Open `devdocs.io` and other, customizable reference docs in browser

## Screenshots

### Javascript / jQuery

![Sublime Javascript hints](https://raw.github.com/jfcherng/Sublime-IntelliDocs/master/docs/intellidocs-javascript.png)

### PHP

![Sublime PHP hints](https://raw.github.com/jfcherng/Sublime-IntelliDocs/master/docs/intellidocs-php.png)

### Python

![Sublime Python hints](https://raw.github.com/jfcherng/Sublime-IntelliDocs/master/docs/intellidocs-python.png)

## Usage

- Set your cursor over a function or object you want to look up
  and press <kbd>Ctrl + Alt + h</kbd> to see relevant documentation.

## Thanks

- Wonderful `devdocs.io` for documents database.

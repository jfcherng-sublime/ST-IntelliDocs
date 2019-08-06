Sublime-IntelliDocs
===================

Quick function parameter help for Sublime 3.x.
Currently supported languages:
 - Javascript & DOM & jQuery `new!`
 - PHP
 - Python
 - More soon :) (Suggest me your favorite language)


## To use this plugin

This plugin is not on Package Control yet. To install this, you can

- Download the tarball from GitHub and decompress it to `Packages/`.
- Or add a custom Package Control repository (recommended).

  1. `Menu > Preferences > Package Control > Settings - User`:
     Add the following:
     ```js
     "package_name_map": {
       "Sublime-IntelliDocs": "-IntelliDocs"
     },
     "repositories": [
       "https://github.com/jfcherng/Sublime-IntelliDocs",
     ]
     ```
  1. `Menu > Preferences > Package Control > Install Package`:
     Find `IntelliDocs` and install


## Changelog ##
 - 1.1.6 (2014-03-18)
   - Lookup key binded to F2 by default (thanks tlqmj!)
 - 1.1.5 (2014-03-06)
   - Support for embedded languages (eg. Javascript in HTML)
   - Support for Javascript hints in Coffeescript
   - More intelligent function name matcher
   - Javascript and jQuery hints working with jQuery syntax
 - 1.1.1 (2014-03-05)
   - Added to Package Settings menu for easier configuration
 - 1.1.0 (2014-03-05)
   - Javascript & DOM & jQuery support
   - Custom reference doc links via config. (php.net, api.jquery.com, developer.mozilla.org, docs.python.org configured by default)
 - 1.0.0 (2014-03-02)
   - Initial release.
   - PHP, Python support


## Features ##
 - Parameter hint
 - Function description
 - Parameter description
 - Last function hint stays in status bar
 - Open devdocs.io and other, customizable reference docs in browser


## Screenshots ##

### Javascript/jQuery ###
 ![Sublime Javascript hints](https://raw.github.com/shortcutme/Sublime-IntelliDocs/master/wiki/intellidocs-javascript.png)

### PHP ###
 ![Sublime PHP hints](https://raw.github.com/shortcutme/Sublime-IntelliDocs/master/wiki/intellidocs-php.png)

### Python ###
 ![Sublime Python hints](https://raw.github.com/shortcutme/Sublime-IntelliDocs/master/wiki/intellidocs-python.png)


## Installation ##

 - Download the [zip-ball](https://github.com/shortcutme/Sublime-IntelliDocs/archive/master.zip) and unpack to `sublime\data\packages` OR via [packageControl](https://sublime.wbond.net/)

## Usage ##

- Set your cursor over a function or object you want to look up and press F2 to see relevant documentation


## Thanks to ##
 - Wonderful Devdocs.io for documents database


## Suggestions are welcomed! Thank you! :) ##
 https://github.com/shortcutme/Sublime-IntelliDocs/issues/3

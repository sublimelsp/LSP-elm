# LSP-elm

Elm support for Sublime's LSP plugin.


### Requirements 

Make sure you have [NodeJS and NPM](https://nodejs.org/) installed.

### Installation

You will need to install `elm` and `elm-test` to get all diagnostics and `elm-format` for formatting. 

```
npm install -g elm elm-test elm-format
```

If you want to use elm-review:

```
npm install -g elm-review
```

* Install [LSP](https://packagecontrol.io/packages/LSP), [Elm Syntax Highlighting](https://packagecontrol.io/packages/Elm%20Syntax%20Highlighting) and `LSP-elm` from Package Control.
* Restart Sublime.

### Configuration

Open configuration file using command palette with `Preferences: LSP-elm Settings` command or by accessing `Preferences > Package Settings > LSP > Servers > LSP-elm` from the sublime menu.

Visit [elm-language-server](https://github.com/elm-tooling/elm-language-server#requirements) for additional server configuration.
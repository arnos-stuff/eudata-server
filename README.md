# Arno's super duper API

This is a super duper API that does super duper things.

## Installation

Just use pip if you're a regular user:

```bash
pip install eudata-server
```

If you want to develop, clone the repo and install the requirements

### Sass

[Sass](https://sass-lang.com/) is used to compile the CSS.

If you're on Windows I recommend using [Scoop](https://scoop.sh/):

```powershell
scoop install sass
```

If you're on Linux, you can use the [homebrew package manager](brew.sh):

```bash
brew install sass/sass/sass
```

A failsafe way to install Dart-Sass is to download the latest release as a zip/tar archive from [here](https://github.com/sass/dart-sass/releases/tag/1.57.1) and add it to your PATH.

## Customization

### Sass Customization

The Sass files are located in `eudata_server/static/sass`. For now the only file to compile is the grid theme file, `grid-theme.scss`.  
To compile it, run:

```bash
sass -w ./eudata_server/assets/sass/grid-theme.scss ./eudata_server/assets/css/grid-theme.css
```

Or if you're on Windows:

```powershell
sass -w .\eudata_server\assets\sass\grid-theme.scss .\eudata_server\assets\css\grid-theme.css
```

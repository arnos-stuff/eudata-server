from pathlib import Path

package_dir = Path(__file__).parent.parent
assets_dir = package_dir / 'assets'
static_dir = assets_dir / 'static'
data_dir = static_dir / 'data'
css_dir = assets_dir / 'css'
sass_dir = assets_dir / 'sass'
js_dir = assets_dir / 'js'
templates_dir = assets_dir / 'templates'
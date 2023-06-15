from dynamic_site.site import Site
import sys

site = Site(
    apps_path='web_apps',
    enforce_dev_mode=True if (len(sys.argv) > 1 and sys.argv[1] == "--dev") else False,
    escape_html_in_md=False)
site.run()
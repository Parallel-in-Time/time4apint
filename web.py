from dynamic_site.site import Site
import sys


# For deployment run
# waitress-serve --call web:deployS
def deploy():
    site = Site(
        apps_path="web_apps",
        enforce_dev_mode=False,
        escape_html_in_md=False,
    )
    return site.wsgi()


if __name__ == "__main__":
    site = Site(
        apps_path="web_apps",
        enforce_dev_mode=True
        if (len(sys.argv) > 1 and sys.argv[1] == "--dev")
        else False,
        escape_html_in_md=False,
        verbose=False,
    )
    site.run()

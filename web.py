from dynamic_site.site import Site

site = Site(enforce_dev_mode=True, escape_html_in_md=False)
site.run()
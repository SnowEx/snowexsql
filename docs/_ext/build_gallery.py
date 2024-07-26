# from https://github.com/executablebooks/meta/blob/b627cdf10477e4bdf651bc86043a3fca1cc8d130/docs/conf.py

from pathlib import Path
import random
from textwrap import dedent
from urllib.parse import urlparse

import yaml

from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.util.typing import ExtensionMetadata

LOGGER = logging.getLogger("conf")

def build_gallery(app: Sphinx):
    # Build the gallery file
    LOGGER.info("building gallery...")
    grid_items = []
    projects = yaml.safe_load((Path(app.srcdir) / "gallery/gallery.yml").read_text())
    random.shuffle(projects)
    for item in projects:
        if not item.get("image"):
            item["image"] = "https://jupyterbook.org/_images/logo-square.svg"

        repo_text = ""
        star_text = ""

# commented for now because we are just making a gallery of examples that don't 
# have a repo or website

        # if item["repository"]:
        #     repo_text = f'{{bdg-link-secondary}}`repo <{item["repository"]}>`'

        #     try:
        #         url = urlparse(item["repository"])
        #         if url.netloc == "github.com":
        #             _, org, repo = url.path.rstrip("/").split("/")
        #             star_text = f"[![GitHub Repo stars](https://img.shields.io/github/stars/{org}/{repo}?style=social)]({item['repository']})"
        #     except Exception as error:
        #         pass

        grid_items.append(
            f"""\
        `````{{grid-item-card}} {" ".join(item["name"].split())}
        :text-align: center

        <a href="{item["website"]}"><img src="{item["image"]}" alt="logo" loading="lazy" style="max-width: 100%; max-height: 200px; margin-top: 1rem;" /></a>

        +++
        ````{{grid}} 2 2 2 2
        :margin: 0 0 0 0
        :padding: 0 0 0 0
        :gutter: 1

        ```{{grid-item}}
        :child-direction: row
        :child-align: start
        :class: sd-fs-5
        
        {repo_text}
        ```
        ```{{grid-item}}
        :child-direction: row
        :child-align: end

        {star_text}
        ```
        ````
        `````
        """
        )
    grid_items = "\n".join(grid_items)

# :column: text-center col-6 col-lg-4
# :card: +my-2
# :img-top-cls: w-75 m-auto p-2
# :body: d-none

    panels = f"""
``````{{grid}} 1 2 3 3
:gutter: 1 1 2 2

{dedent(grid_items)}
``````
    """
    (Path(app.srcdir) / "gallery/gallery.txt").write_text(panels)


def setup(app: Sphinx) -> ExtensionMetadata:
    app.connect('builder-inited', build_gallery)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
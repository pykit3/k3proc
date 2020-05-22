import os
import sys

sys.path.insert(0, os.path.abspath('.'))

import building

(project,
 pkg,
 release,
 author,
 copyright,

 extensions,
 templates_path,
 exclude_patterns,
 master_doc,
 html_theme,
 html_static_path,
) = building.sphinx_confs("pk3proc")

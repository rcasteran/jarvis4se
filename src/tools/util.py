"""@defgroup tools
Tooling module
"""

# Libraries

# Modules


def get_hyperlink(path):
    """@ingroup tools
    @anchor get_hyperlink
    Convert file path into HTML link
    @param[in] path file path
    @return HTML link
    """
    text = "Click to open in new tab"
    # convert the url into link
    return f'<a href="{path}" target="_blank">{text}</a>'

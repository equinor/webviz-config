from webviz_config._docs._build_docs import _split_docstring


def test_split_docstring():
    tests = [
        (
            "This is a test with only description.",
            ["This is a test with only description."],
        ),
        (
            (
                " This is a test with only description, "
                "but which has leading and trailing spaces.  "
            ),
            [
                (
                    "This is a test with only description, "
                    "but which has leading and trailing spaces."
                )
            ],
        ),
        (
            "Test with some newlines\n\n  \n    and a 4 space indent",
            ["Test with some newlines\n\n\nand a 4 space indent"],
        ),
        (
            "Test with a \n    4 space and a \n  2 space indent\n",
            ["Test with a \n  4 space and a \n2 space indent"],
        ),
        (
            "Test with a \n    4 space and a \n  2 space indent\n",
            ["Test with a \n  4 space and a \n2 space indent"],
        ),
        (
            (
                " This is a test with description, arguments and data input."
                "\n\n    ---\n\n    The docstring is indented by 4 spaces:\n    "
                "* The argument list has a sub list indented by 8 spaces\n        like this."
                "\n    ---\n    The data input section is not very interesting."
            ),
            [
                "This is a test with description, arguments and data input.\n",
                (
                    "\nThe docstring is indented by 4 spaces:\n"
                    "* The argument list has a sub list indented by 8 spaces\n    like this."
                ),
                "The data input section is not very interesting.",
            ],
        ),
        (
            (
                "\tThis is a test with description, arguments and data input,"
                " where indents are made with tabs and not spaces-"
                "\n\n\t---\n\n\tThe docstring is indented by 1 tab:\n"
                "\t* The argument list has a sub list indented by 2 tabs\n\t\tlike this."
                "\n\t---\n\tThe data input section is not very interesting."
            ),
            [
                (
                    "This is a test with description, arguments and data input,"
                    " where indents are made with tabs and not spaces-\n"
                ),
                (
                    "\nThe docstring is indented by 1 tab:\n"
                    "* The argument list has a sub list indented by 2 tabs\n\tlike this."
                ),
                "The data input section is not very interesting.",
            ],
        ),
        (
            "This is a test with only description, which includes a linebreak.\n",
            ["This is a test with only description, which includes a linebreak."],
        ),
    ]
    for test in tests:
        assert _split_docstring(test[0]) == test[1]

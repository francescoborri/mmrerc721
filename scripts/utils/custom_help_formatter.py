import argparse


class CustomHelpFormatter(argparse.HelpFormatter):
    def _split_lines(self, text: str, width: int) -> list[str]:
        """
        Custom formatter to allow newlines in the help message. It first splits the text using the newline
        character and then uses the default formatter to split each line according to the width.

        Parameters
        ----------
        `text` : `str`
            The text to be formatted
        `width` : `int`
            The maximum width of each line

        Returns
        -------
        `list[str]`
            A list of lines, each with at most `width` characters; the lines are obtained by splitting
            `text` by the newline character and then formatting each element using the default formatter
        """
        return [
            line for lines in text.splitlines() for line in super(CustomHelpFormatter, self)._split_lines(lines, width)
        ]

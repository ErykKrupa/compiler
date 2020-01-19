import sys


class ErrorPrinter:

    @staticmethod
    def raise_error(error):
        sys.stderr.write(f"Error raised: {error} \n")
        exit(1)

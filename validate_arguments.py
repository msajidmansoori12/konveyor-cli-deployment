import argparse


class ValidateArguments(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

        if self.dest in ['mta_version', 'build']:
            if namespace.mta_version is not None and namespace.build is not None:
                if namespace.upstream is not None:
                    parser.error("--mta_version and --build cannot be used with --upstream.")
            # elif namespace.mta_version is None or namespace.build is None:
            #     # This block ensures both mta_version and build are provided together
            #     parser.error("--mta_version and --build must be used together.")

        if self.dest == 'upstream':
            if namespace.mta_version is not None or namespace.build is not None:
                parser.error("--upstream cannot be used with --mta_version and --build.")

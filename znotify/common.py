import logging

def setup_logging(loglevel):
    logging.basicConfig(
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(name)s %(levelname)s: %(message)s',
        level=loglevel)


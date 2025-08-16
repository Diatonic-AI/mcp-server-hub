from .server import serve


def main():
    """MCP Database Insert Server - JSON-RPC to database functionality for MCP"""
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
        description="Parse JSON-RPC responses and insert data into databases"
    )
    parser.add_argument(
        "--max-batch-size",
        type=int,
        default=1000,
        help="Maximum batch size for bulk operations"
    )
    parser.add_argument(
        "--connection-timeout",
        type=int,
        default=30,
        help="Database connection timeout in seconds"
    )
    parser.add_argument(
        "--enable-debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()
    asyncio.run(serve(
        max_batch_size=args.max_batch_size,
        connection_timeout=args.connection_timeout,
        enable_debug=args.enable_debug
    ))


if __name__ == "__main__":
    main()

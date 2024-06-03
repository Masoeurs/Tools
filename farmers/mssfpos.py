"""
NOTE: This contains duplicate code from `MSSF.cmds.plots`.
After `MSSF plots create` becomes obsolete, consider removing it from there.
"""
from __future__ import annotations

import asyncio
import importlib.metadata
import logging
from argparse import Namespace
from pathlib import Path
from typing import Any, Dict, Optional

from MSSF.plotting.create_plots import create_plots, resolve_plot_keys
from MSSF.plotting.util import Params, add_plot_directory, validate_plot_size

log = logging.getLogger(__name__)


def get_MSSFpos_install_info() -> Optional[Dict[str, Any]]:
    MSSFpos_version: str = importlib.metadata.version("MSSFpos")
    return {"display_name": "MSSF Proof of Space", "version": MSSFpos_version, "installed": True}


def plot_MSSF(args: Namespace, root_path: Path) -> None:
    try:
        validate_plot_size(root_path, args.size, args.override)
    except ValueError as e:
        print(e)
        return

    plot_keys = asyncio.run(
        resolve_plot_keys(
            None if args.farmerkey == b"" else args.farmerkey.hex(),
            args.alt_fingerprint,
            None if args.pool_key == b"" else args.pool_key.hex(),
            None if args.contract == "" else args.contract,
            root_path,
            log,
            args.connect_to_daemon,
        )
    )
    params = Params(
        size=args.size,
        num=args.count,
        buffer=args.buffer,
        num_threads=args.threads,
        buckets=args.buckets,
        stripe_size=args.stripes,
        tmp_dir=Path(args.tmpdir),
        tmp2_dir=Path(args.tmpdir2) if args.tmpdir2 else None,
        final_dir=Path(args.finaldir),
        plotid=args.id,
        memo=args.memo,
        nobitfield=args.nobitfield,
    )
    asyncio.run(create_plots(params, plot_keys))
    if not args.exclude_final_dir:
        try:
            add_plot_directory(root_path, args.finaldir)
        except ValueError as e:
            print(e)

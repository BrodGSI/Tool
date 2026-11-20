"""Background worker thread for running BrodGSI builds and rebuilds."""

import os
import queue
import threading

import buildlock
import cli
import make
import tools
from tools.host import configure_environment


class GuiLogger:
    def __init__(self, msg_queue: queue.Queue):
        self.msg_queue = msg_queue

    def set_progress(self, val: int):
        self.msg_queue.put(("progress", int(val)))

    def set_state(self, state: str):
        self.msg_queue.put(("state", str(state)))

    def add(self, message: str):
        for line in str(message).rstrip("\n").split("\n"):
            self.msg_queue.put(("log", line))


class BuildRunner:
    """Manages background build execution."""

    def __init__(self, on_progress, on_state, on_log, on_finish):
        self.on_progress = on_progress
        self.on_state = on_state
        self.on_log = on_log
        self.on_finish = on_finish
        self.cancel_requested = False
        self.active_thread = None
        self.msg_queue = queue.Queue()

    def start_build(self, args: dict):
        self.cancel_requested = False
        self.active_thread = threading.Thread(
            target=self._run_build,
            args=(args,),
            daemon=True,
        )
        self.active_thread.start()

    def start_rebuild(self, args: dict):
        self.cancel_requested = False
        self.active_thread = threading.Thread(
            target=self._run_rebuild,
            args=(args,),
            daemon=True,
        )
        self.active_thread.start()

    def cancel(self):
        self.cancel_requested = True
        self.msg_queue.put(("log", "[!] Cancel requested by user."))

    def poll_messages(self):
        """Called periodically by UI main thread."""
        while not self.msg_queue.empty():
            try:
                kind, payload = self.msg_queue.get_nowait()
                if kind == "progress":
                    self.on_progress(payload)
                elif kind == "state":
                    self.on_state(payload)
                elif kind == "log":
                    self.on_log(payload)
                elif kind == "finish":
                    success, out_dir, cancelled = payload
                    self.on_finish(success, out_dir, cancelled)
            except queue.Empty:
                break

    def _run_build(self, args: dict):
        configure_environment()
        logger = GuiLogger(self.msg_queue)
        fmt = args.get("format")
        source = args.get("source")
        name = args.get("name")
        rom_type_input = args.get("type", "auto")
        add_tag = args.get("add", "")
        compress = bool(args.get("compress", False))
        no_merge = bool(args.get("no_merge", False))
        no_debloat = bool(args.get("no_debloat", False))
        avb_key = args.get("avb_key")

        logger.add(f"[*] BrodGSI build starting for {name}...")

        try:
            tools.check_environment(cli.erofs_tools(fmt))
        except (RuntimeError, OSError) as e:
            logger.add(f"[ERROR] Environment check failed: {e}")
            self.msg_queue.put(("finish", (False, None, False)))
            return

        rom_type, _, rom_custom = rom_type_input.partition(":")
        try:
            wt = make.RomPorter(name, add_tag)
            wt.rom_type = make.safe_name(rom_type, "rom_type")
            wt.override_rom_type = make.safe_name(
                rom_custom or "default", "rom_custom"
            )
        except ValueError as e:
            logger.add(f"[ERROR] Invalid configuration: {e}")
            self.msg_queue.put(("finish", (False, None, False)))
            return

        wt.logger = logger
        wt.debloat = not no_debloat
        wt.no_merge = no_merge
        wt.erofs_format = fmt
        wt.avb_key = avb_key

        def on_busy():
            logger.add("[*] Waiting for another build to finish (lock busy)...")

        try:
            with buildlock.hold(on_busy=on_busy):
                if self.cancel_requested:
                    self.msg_queue.put(("finish", (False, None, True)))
                    return

                if "://" in source:
                    logger.set_state("extract")
                    logger.add(f"[*] Downloading firmware from {source}...")
                    os.makedirs(wt.work_dir, exist_ok=True)
                    filename = cli.fetch(source, wt.work_dir)
                    if filename is None or self.cancel_requested:
                        logger.add("[ERROR] Download failed or was aborted.")
                        self.msg_queue.put(("finish", (False, None, self.cancel_requested)))
                        return
                else:
                    filename = source
                    if not os.path.exists(filename):
                        logger.add(f"[ERROR] File not found: {filename}")
                        self.msg_queue.put(("finish", (False, None, False)))
                        return

                if self.cancel_requested:
                    self.msg_queue.put(("finish", (False, None, True)))
                    return

                rc = wt.build(filename)
                if rc != 0 or self.cancel_requested:
                    logger.add(f"[ERROR] Build failed with return code {rc}")
                    self.msg_queue.put(("finish", (False, None, self.cancel_requested)))
                    return

                if compress:
                    logger.set_state("compress")
                    logger.add("[*] Compressing output images...")
                    if wt.compress_output() != 0:
                        logger.add("[ERROR] Compression failed.")
                        self.msg_queue.put(("finish", (False, None, False)))
                        return

                cli.append_list(wt)

            logger.add("[*] Summary:")
            logger.add(cli.summarize(wt.output))
            for image in wt.output_images.values():
                logger.add(f"[*] Image: {image}")
            if compress:
                logger.add(f"[*] ZIP: {wt.output_path}.zip")

            self.msg_queue.put(("finish", (True, wt.output_path or "out", False)))

        except Exception as ex:
            logger.add(f"[EXCEPTION] {ex}")
            self.msg_queue.put(("finish", (False, None, False)))

    def _run_rebuild(self, args: dict):
        configure_environment()
        logger = GuiLogger(self.msg_queue)
        name = args.get("name")
        compress = bool(args.get("compress", False))
        avb_key = args.get("avb_key")

        logger.add(f"[*] BrodGSI rebuild starting for {name}...")

        entries = cli.read_list()
        entry = next((e for e in reversed(entries) if e.get("rom_name") == name), None)
        if entry is None:
            logger.add(f"[ERROR] No build named {name!r} found in {cli.GSILIST}")
            self.msg_queue.put(("finish", (False, None, False)))
            return

        try:
            tools.check_environment(cli.erofs_tools(entry.get("format")))
        except (RuntimeError, OSError) as e:
            logger.add(f"[ERROR] Environment check failed: {e}")
            self.msg_queue.put(("finish", (False, None, False)))
            return

        wt = make.RomPorter(entry["rom_name"], entry.get("variant_tag", ""))
        wt.avb_key = avb_key
        wt.no_merge = entry.get("no_merge", False)
        wt.erofs_format = entry.get("format")
        wt.image_partitions = entry.get("image_partitions", ["system"])
        wt.logger = logger

        def on_busy():
            logger.add("[*] Waiting for another build to finish (lock busy)...")

        try:
            with buildlock.hold(on_busy=on_busy):
                if self.cancel_requested:
                    self.msg_queue.put(("finish", (False, None, True)))
                    return

                system_size = wt.rebuild(entry["output_name"])
                if system_size is None or self.cancel_requested:
                    logger.add("[ERROR] Rebuild failed.")
                    self.msg_queue.put(("finish", (False, None, self.cancel_requested)))
                    return

                if compress:
                    logger.set_state("compress")
                    logger.add("[*] Compressing output images...")
                    if wt.compress_output() != 0:
                        logger.add("[ERROR] Compression failed.")
                        self.msg_queue.put(("finish", (False, None, False)))
                        return

                entry["output"] = make.replace_image_size(entry["output"], system_size)
                entry["output_images"] = wt.output_images
                cli.write_list(entries)

            for part, image in wt.output_images.items():
                size = f" ({make.bytes_to_human(system_size)})" if part == "system" else ""
                logger.add(f"[*] {image}{size}")
            if compress:
                logger.add(f"[*] ZIP: {wt.output_path}.zip")

            self.msg_queue.put(("finish", (True, wt.output_path or "out", False)))

        except Exception as ex:
            logger.add(f"[EXCEPTION] {ex}")
            self.msg_queue.put(("finish", (False, None, False)))
